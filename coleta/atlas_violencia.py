"""Transforma as séries do Atlas da Violência (Ipea, a partir do SIM/Ministério
da Saúde) em linhas do CSV de indicadores de segurança pública.

Uso, a partir da raiz do projeto:
    python coleta/atlas_violencia.py

Arquivos brutos em dados/brutos/, salvos sem edição a partir de
https://www.ipea.gov.br/dados-api/series-values/<série>/1:
- série 20: taxa de homicídios registrados (CID-10 X85-Y09 e Y35);
- série 328: homicídios registrados (número);
- série 77: óbitos por intervenção legal (número);
- série 78: mortes violentas por causa indeterminada (número).

Gera quatro séries do Brasil (região 1076 da API): taxa de homicídios, mortes
por intervenção legal, participação delas nos homicídios e mortes de causa
indeterminada. A taxa é conferida contra contagem / população do IBGE.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from coleta.comum import INDICATORS_FILE, ROOT, merge_into
except ModuleNotFoundError:  # execução direta: python coleta/atlas_violencia.py
    from comum import INDICATORS_FILE, ROOT, merge_into

RAW_DIR = ROOT / "dados" / "brutos"
RAW_TEMPLATE = "ipea_atlas_serie_{}_acesso-2026-10-06.json"
POPULATION_FILE = RAW_DIR / "ibge_sidra_6784_pib_anual_acesso-2026-10-06.json"
API_URL = "https://www.ipea.gov.br/dados-api/series-values/{}/1"
PAGE_URL = "https://www.ipea.gov.br/atlasviolencia/dados-series/{}"
ACCESS_DATE = "2026-10-06"
BRAZIL_REGION_ID = 1076
FIRST_YEAR = 2002  # base, ADR-009
RATE_TOLERANCE = 0.006  # a taxa publicada tem duas casas decimais

HOMICIDE_RATE = "Taxa de homicídios registrados"
LEGAL_INTERVENTION = "Mortes por intervenção legal (agentes do Estado)"
LEGAL_INTERVENTION_SHARE = "Mortes por intervenção legal: parcela dos homicídios"
UNDETERMINED = "Mortes violentas por causa indeterminada"
SERIES = "Brasil"

# Observações por ano, exibidas na metodologia da linha correspondente.
NOTES = {
    (LEGAL_INTERVENTION, 2003): (
        "Salto de 121 (2002) para 491 (2003) óbitos; variações desse porte podem "
        "refletir mudança de registro, não só de ocorrência."
    ),
    (HOMICIDE_RATE, 2019): (
        "Queda dos homicídios registrados coincide com alta das mortes violentas "
        "por causa indeterminada; ver série própria."
    ),
    (HOMICIDE_RATE, 2024): (
        "Taxa da API (20,03) difere da divulgada em notícia oficial do Atlas 2026 "
        "(20,1); conferir no relatório antes de validar."
    ),
}


def brazil_values(raw: list[dict]) -> dict[int, float]:
    """Valores anuais do Brasil; falha se houver ano repetido."""
    values: dict[int, float] = {}
    for item in raw:
        if item["regiao_id"] != BRAZIL_REGION_ID:
            continue
        year = int(item["periodo"][:4])
        if year in values:
            raise ValueError(f"Série {item['serie_id']}: ano {year} repetido para o Brasil.")
        values[year] = float(item["valor"])
    if not values:
        raise ValueError("Nenhum valor para o Brasil (regiao_id 1076).")
    return values


def population_by_year(raw: list[dict]) -> dict[int, float]:
    for variable in raw:
        if variable["id"] == "93":  # população residente, mil pessoas
            serie = variable["resultados"][0]["series"][0]["serie"]
            return {int(year): float(value) * 1000 for year, value in serie.items()}
    raise ValueError("População (variável 93) ausente no arquivo do IBGE.")


def build_series(rate, homicides, interventions, undetermined, population):
    """Devolve {indicador: [(ano, valor, unidade, séries de origem)]}."""
    for year, rate_value in rate.items():
        if year >= FIRST_YEAR and year in population and year in homicides:
            recalculated = homicides[year] / population[year] * 100_000
            if abs(rate_value - recalculated) > RATE_TOLERANCE:
                raise ValueError(
                    f"Taxa {year}: publicada {rate_value} difere de "
                    f"{recalculated:.3f} (homicídios / população do IBGE)."
                )
    for year, count in interventions.items():
        if year in homicides and count > homicides[year]:
            raise ValueError(f"{year}: intervenções legais excedem o total de homicídios.")

    def years(values):
        return sorted(year for year in values if year >= FIRST_YEAR)

    return {
        HOMICIDE_RATE: [
            (y, round(rate[y], 2), "óbitos por 100 mil habitantes", (20,)) for y in years(rate)
        ],
        LEGAL_INTERVENTION: [
            (y, int(interventions[y]), "óbitos", (77,)) for y in years(interventions)
        ],
        LEGAL_INTERVENTION_SHARE: [
            (y, round(100 * interventions[y] / homicides[y], 2),
             "% dos homicídios registrados", (77, 328))
            for y in years(interventions) if y in homicides
        ],
        UNDETERMINED: [
            (y, int(undetermined[y]), "óbitos", (78,)) for y in years(undetermined)
        ],
    }


def to_rows(series: dict) -> list[tuple[str, dict[str, str]]]:
    rows = []
    for indicator, points in series.items():
        for year, value, unit, sources in points:
            ids = ", ".join(str(source) for source in sources)
            method = (
                f"Atlas da Violência/Ipea, séries {ids} (SIM/Ministério da Saúde, óbitos "
                "por residência). Homicídios: CID-10 X85-Y09 e Y35; intervenção legal: "
                "subconjunto já incluído no total de homicídios."
            )
            if indicator == LEGAL_INTERVENTION_SHARE:
                method += " Calculado: série 77 / série 328 × 100."
            note = NOTES.get((indicator, year))
            if note:
                method += f" {note}"
            rows.append(
                (
                    indicator,
                    {
                        "indicador": indicator,
                        "serie": SERIES,
                        "ano": str(year),
                        "valor": str(value),
                        "unidade": unit,
                        "fonte": "Ipea, Atlas da Violência (SIM/MS)",
                        "url_fonte": PAGE_URL.format(sources[0]),
                        "periodo_ref": f"jan–dez/{year}",
                        "inicio_periodo": f"{year}-01-01",
                        "fim_periodo": f"{year}-12-31",
                        "tipo_dado": "observado",
                        "data_acesso": ACCESS_DATE,
                        "validada": "nao",
                        "metodologia": method + " Transformação em coleta/atlas_violencia.py.",
                    },
                )
            )
    return rows


def load_raw(series_id: int) -> list[dict]:
    return json.loads((RAW_DIR / RAW_TEMPLATE.format(series_id)).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=INDICATORS_FILE)
    args = parser.parse_args()

    series = build_series(
        brazil_values(load_raw(20)),
        brazil_values(load_raw(328)),
        brazil_values(load_raw(77)),
        brazil_values(load_raw(78)),
        population_by_year(json.loads(POPULATION_FILE.read_text(encoding="utf-8"))),
    )
    rows = to_rows(series)
    for indicator in series:
        merge_into(args.output, indicator, SERIES, [row for name, row in rows if name == indicator])
        years = [point[0] for point in series[indicator]]
        print(f"'{indicator}': {len(years)} anos ({years[0]}–{years[-1]}).")
    print("Linhas novas ou alteradas ficam com validada=nao até a conferência.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
