"""Transforma os arquivos brutos do PIB (IBGE/SIDRA) em linhas do CSV de
indicadores: variação real anual do PIB e do PIB per capita.

Uso, a partir da raiz do projeto:
    python coleta/pib.py

Fontes, ambas salvas sem edição em dados/brutos/:
- Contas Nacionais Anuais (tabela 6784): dado consolidado, variáveis 9810
  (PIB, variação em volume) e 9814 (PIB per capita, variação em volume);
- Contas Nacionais Trimestrais (tabela 5932): taxa acumulada no ano no 4º
  trimestre (variável 6563), usada só para anos ainda sem conta anual e
  marcada como preliminar. Nos anos em comum, as duas fontes são comparadas e
  a coleta falha se a diferença passar de TOLERANCE.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from coleta.comum import INDICATORS_FILE, ROOT, merge_into
except ModuleNotFoundError:  # execução direta: python coleta/pib.py
    from comum import INDICATORS_FILE, ROOT, merge_into

ANNUAL_FILE = ROOT / "dados" / "brutos" / "ibge_sidra_6784_pib_anual_acesso-2026-10-06.json"
QUARTERLY_FILE = ROOT / "dados" / "brutos" / "ibge_sidra_5932_pib_trimestral_acesso-2026-10-06.json"
ANNUAL_URL = "https://sidra.ibge.gov.br/tabela/6784"
QUARTERLY_URL = "https://sidra.ibge.gov.br/tabela/5932"
ACCESS_DATE = "2026-10-06"
FIRST_YEAR = 2002  # base, ADR-009
# Os valores têm uma casa decimal; diferenças de arredondamento entre as
# contas anuais e trimestrais chegam a 0,1 ponto (2018 e 2019).
TOLERANCE = 0.1 + 1e-9

GDP = "PIB: variação real anual"
GDP_PER_CAPITA = "PIB per capita: variação real anual"
SERIES = "Brasil"


def _serie(raw: list[dict], variable_id: str) -> dict[str, str]:
    for variable in raw:
        if variable["id"] == variable_id:
            return variable["resultados"][0]["series"][0]["serie"]
    raise ValueError(f"Variável {variable_id} ausente no arquivo bruto.")


def _numeric(serie: dict[str, str]) -> dict[int, float]:
    """Converte para número; '...', '-' e similares (sem dado) são ignorados."""
    values = {}
    for period, value in serie.items():
        try:
            values[int(period[:4])] = float(value)
        except ValueError:
            continue
    return values


def gdp_rates(annual_raw: list[dict], quarterly_raw: list[dict]):
    """Devolve (ano, valor, tipo, fonte) para o PIB e (ano, valor) per capita."""
    annual = _numeric(_serie(annual_raw, "9810"))
    per_capita = _numeric(_serie(annual_raw, "9814"))
    quarterly_serie = _serie(quarterly_raw, "6563")
    fourth_quarter = _numeric(
        {period: value for period, value in quarterly_serie.items() if period.endswith("04")}
    )

    for year in sorted(set(annual) & set(fourth_quarter)):
        if abs(annual[year] - fourth_quarter[year]) > TOLERANCE:
            raise ValueError(
                f"PIB {year}: contas anuais ({annual[year]}) e trimestrais "
                f"({fourth_quarter[year]}) divergem mais que {TOLERANCE:.1f} ponto."
            )

    last_annual = max(annual)
    gdp = [(year, annual[year], "observado", "anual") for year in sorted(annual) if year >= FIRST_YEAR]
    gdp += [
        (year, fourth_quarter[year], "preliminar", "trimestral")
        for year in sorted(fourth_quarter)
        if year > last_annual
    ]
    gdp_per_capita = [(year, per_capita[year]) for year in sorted(per_capita) if year >= FIRST_YEAR]
    return gdp, gdp_per_capita, max(quarterly_serie)


def _row(indicator: str, year: int, value: float, data_type: str, source: str) -> dict[str, str]:
    if source == "anual":
        fonte = "IBGE, Contas Nacionais Anuais (SIDRA, tabela 6784)"
        url = ANNUAL_URL
        method = "Variação em volume do Sistema de Contas Nacionais anual (dado consolidado)."
    else:
        fonte = "IBGE, Contas Nacionais Trimestrais (SIDRA, tabela 5932)"
        url = QUARTERLY_URL
        method = (
            "Taxa acumulada no ano até o 4º trimestre (variável 6563), primeira "
            "estimativa anual; será substituída pela conta anual quando publicada."
        )
    return {
        "indicador": indicator,
        "serie": SERIES,
        "ano": str(year),
        "valor": f"{value:.1f}",
        "unidade": "% em relação ao ano anterior",
        "fonte": fonte,
        "url_fonte": url,
        "periodo_ref": f"jan–dez/{year}",
        "inicio_periodo": f"{year}-01-01",
        "fim_periodo": f"{year}-12-31",
        "tipo_dado": data_type,
        "data_acesso": ACCESS_DATE,
        "validada": "nao",
        "metodologia": method + " Transformação em coleta/pib.py.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=INDICATORS_FILE)
    args = parser.parse_args()

    annual_raw = json.loads(ANNUAL_FILE.read_text(encoding="utf-8"))
    quarterly_raw = json.loads(QUARTERLY_FILE.read_text(encoding="utf-8"))
    gdp, gdp_per_capita, last_quarter = gdp_rates(annual_raw, quarterly_raw)

    gdp_rows = [_row(GDP, *item) for item in gdp]
    per_capita_rows = [
        _row(GDP_PER_CAPITA, year, value, "observado", "anual") for year, value in gdp_per_capita
    ]
    merge_into(args.output, GDP, SERIES, gdp_rows)
    merge_into(args.output, GDP_PER_CAPITA, SERIES, per_capita_rows)

    print(f"{len(gdp_rows)} linhas de '{GDP}' e {len(per_capita_rows)} de '{GDP_PER_CAPITA}'.")
    print(f"Último trimestre publicado: {int(last_quarter[4:])}º/{last_quarter[:4]} (ano em curso excluído).")
    print("Linhas novas ou alteradas ficam com validada=nao até a conferência.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
