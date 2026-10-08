"""Conferência automática independente de dados/indicadores.csv.

Uso, a partir da raiz do projeto:
    python conferencia/verificar.py

Baixa cada série por um caminho diferente do usado na coleta e compara valor
a valor:
- IBGE: API SIDRA "values" (apisidra.ibge.gov.br), e não a API de agregados;
- Atlas da Violência: SIM/DATASUS pelo TabNet (fonte primária do Atlas);
- PRODES: texto de notícias oficiais do INPE, quando citam a taxa do ano.

Grava as respostas em conferencia/brutos/ e o resultado em
conferencia/resultado_conferencia.csv. Não altera a coluna 'validada': a
aprovação continua humana (conferencia/aplicar.py).
"""

from __future__ import annotations

import csv
import html
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from coleta import tabnet as sim_tabnet  # noqa: E402
from coleta.atlas_violencia import (  # noqa: E402
    HOMICIDE_RATE,
    LEGAL_INTERVENTION,
    LEGAL_INTERVENTION_SHARE,
    UNDETERMINED,
)
from coleta.ipca import INDICATOR as IPCA  # noqa: E402
from coleta.pib import GDP, GDP_PER_CAPITA  # noqa: E402
from coleta.prodes_amazonia import INDICATOR as PRODES  # noqa: E402
from coleta.sim_mulheres import INDICATOR as WOMEN_HOMICIDES  # noqa: E402
from coleta.sinesp_feminicidio import INDICATOR as FEMICIDES  # noqa: E402

OUT_DIR = ROOT / "conferencia"
RAW_DIR = OUT_DIR / "brutos"
INDICATORS_FILE = ROOT / "dados" / "indicadores.csv"
RESULT_FILE = OUT_DIR / "resultado_conferencia.csv"
LOG_FILE = OUT_DIR / "log_urls.csv"

OK, DIVERGE, MANUAL = "OK", "DIVERGE", "MANUAL"
RESULT_COLUMNS = (
    "indicador", "serie", "ano", "periodo_ref", "valor_csv", "valor_checagem",
    "diferenca", "resultado", "fonte_checagem", "como_conferir", "pendencia",
)

TABNET_FORM = sim_tabnet.TABNET_FORM
INPE_NEWS = {
    # Ano PRODES → (URL oficial, trecho que o texto precisa conter)
    2025: ("https://www.gov.br/inpe/pt-br/assuntos/ultimas-noticias/"
           "sistema-do-inpe-aponta-5-731-km2-de-desmatamento-na-amazonia-em-2025", "5.731 km"),
    2024: ("https://www.gov.br/inpe/pt-br/assuntos/ultimas-noticias/"
           "sistema-do-inpe-aponta-5-731-km2-de-desmatamento-na-amazonia-em-2025",
           "taxa de 2024, que foi de 6.518"),
}

MANUAL_LINKS = {
    PRODES: "Painel TerraBrasilis, tabela de taxas: https://terrabrasilis.dpi.inpe.br/app/"
            "dashboard/deforestation/biomes/legal_amazon/rates",
    IPCA: "SIDRA 1737, variável 'acumulada no ano', mês dezembro: https://sidra.ibge.gov.br/tabela/1737",
    GDP: "SIDRA 6784 (até 2023) e 5932 (2024–2025, 4º trimestre, 'acumulada ao longo do ano')",
    GDP_PER_CAPITA: "SIDRA 6784, 'PIB per capita - variação em volume': https://sidra.ibge.gov.br/tabela/6784",
    HOMICIDE_RATE: "Atlas da Violência, série 20: https://www.ipea.gov.br/atlasviolencia/dados-series/20",
    LEGAL_INTERVENTION: "TabNet SIM, causas externas, grande grupo Y35-Y36, óbitos por residência: "
                        + TABNET_FORM,
    LEGAL_INTERVENTION_SHARE: "Recalcular: Y35-Y36 ÷ (X85-Y09 + Y35-Y36) × 100 no TabNet SIM",
    UNDETERMINED: "TabNet SIM, causas externas, grande grupo Y10-Y34: " + TABNET_FORM,
    WOMEN_HOMICIDES: "Atlas da Violência, série 40: https://www.ipea.gov.br/atlasviolencia/"
                     "dados-series/40 (ou TabNet SIM, sexo feminino, X85-Y09 + Y35-Y36)",
    FEMICIDES: "Planilha bancovde-<ano>.xlsx do MJSP: filtrar evento 'Feminicídio' e somar "
               "total_vitima (ou dados/derivados/sinesp_feminicidio_mensal.csv)",
}

# Pendências de um ano específico, mostradas na própria linha.
PENDING = {
    (HOMICIDE_RATE, 2024): "API do Atlas dá 20,03; notícia oficial do Atlas 2026 dá 20,1. "
                           "Conferir a taxa e a população usada no relatório Atlas 2026.",
    (LEGAL_INTERVENTION, 2003): "Salto de 121 para 491 óbitos: confirmar a nota sobre provável "
                                "mudança de registro.",
    (FEMICIDES, 2024): "Base atual dá 1.501; o MJSP divulgou 1.464 no início de 2025 e o Anuário "
                       "do FBSP, 1.492. Diferença atribuída a envios atrasados dos estados.",
    (FEMICIDES, 2025): "Base atual dá 1.578 (preliminar); divulgações de 2026 variaram de 1.470 "
                       "a 1.568 conforme a data. Conferir a data de atualização da base.",
}
# Pendências da série inteira: decisão editorial, fora da conferência linha a linha.
SERIES_PENDING = {
    GDP_PER_CAPITA: "A população da tabela 6784 (210,9 milhões em 2022) é maior que a do Censo "
                    "2022. Confirmar na nota metodológica do IBGE se haverá revisão e decidir "
                    "se a série é publicada com essa ressalva.",
    LEGAL_INTERVENTION: "O metadado oficial do Atlas está incompleto. A checagem usou o grupo "
                        "Y35-Y36 do TabNet (Y36 = operações de guerra), que bateu ano a ano com o "
                        "Atlas. Confirmar se a redação 'intervenção legal' está adequada.",
    FEMICIDES: "Decidir entre 'total_vitima' (usado; inclui vítimas sem marcação de sexo) e "
               "'feminino' (de 7 a 29 vítimas a menos por ano). Decidir também se a peça cita "
               "o Anuário do FBSP, que usa outra compilação e dá números diferentes.",
    HOMICIDE_RATE: "O TabNet/SIM já traz 17.207 mortes de causa indeterminada em 2024 (contra "
                   "13.896 em 2023), dado ainda não publicado pelo Atlas. Decidir se a nota do "
                   "gráfico de homicídios menciona esse aumento.",
}

LOG: list[dict[str, str]] = []


def _get(url: str, data: bytes | None = None, encoding: str = "utf-8") -> str:
    request = urllib.request.Request(
        url, data=data, headers={"User-Agent": "Mozilla/5.0 (conferencia Mangue)"}
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            body = response.read().decode(encoding, errors="replace")
            status = str(response.status)
    except Exception as error:  # registra e segue: a linha vira MANUAL
        LOG.append({"url": url, "params": "POST" if data else "", "status": f"erro: {error}",
                    "quando": datetime.now().strftime("%Y-%m-%d %H:%M")})
        raise
    LOG.append({"url": url, "params": "POST" if data else "", "status": status,
                "quando": datetime.now().strftime("%Y-%m-%d %H:%M")})
    return body


def _save(name: str, content: str) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / name).write_text(content, encoding="utf-8")


def sidra(table: str, variable: str, periods: str, classification: str = "") -> dict[str, float]:
    """Valores do Brasil pela API SIDRA 'values', por código de período."""
    url = (f"https://apisidra.ibge.gov.br/values/t/{table}/n1/all/v/{variable}/p/{periods}"
           + (f"/{classification}" if classification else ""))
    body = _get(url)
    _save(f"apisidra_{table}_{variable}.json", body)
    rows = json.loads(body)[1:]
    values = {}
    for row in rows:
        if row["D1N"] != "Brasil":
            raise ValueError(f"SIDRA {table}: nível territorial inesperado {row['D1N']!r}.")
        try:
            values[row["D3C"]] = float(row["V"])
        except ValueError:
            continue
    return values


def tabnet(first_year: int, last_year: int, sex: str = "todos") -> dict[str, dict[int, int]]:
    body = sim_tabnet.fetch(first_year, last_year, sex)
    LOG.append({"url": sim_tabnet.TABNET_URL, "params": f"POST sexo={sex}", "status": "200",
                "quando": datetime.now().strftime("%Y-%m-%d %H:%M")})
    _save(f"tabnet_sim_causas_externas_{sex}.html", body)
    return sim_tabnet.parse(body)


def inpe_text_checks() -> dict[int, float]:
    """Anos PRODES cuja taxa aparece no texto de notícia oficial do INPE."""
    found = {}
    pages: dict[str, str] = {}
    for year, (url, excerpt) in INPE_NEWS.items():
        if url not in pages:
            raw = _get(url)
            _save(f"inpe_noticia_{year}.html", raw)
            text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
            pages[url] = re.sub(r"\s+", " ", text)
        if excerpt in pages[url]:
            number = re.search(r"(\d{1,3}(?:\.\d{3})+)", excerpt.split("foi de")[-1])
            found[year] = float(number.group(1).replace(".", ""))
    return found


def build_references(years: range) -> dict[tuple[str, int], tuple[float, str]]:
    """{(indicador, ano): (valor de referência, descrição da fonte)}."""
    refs: dict[tuple[str, int], tuple[float, str]] = {}
    decembers = ",".join(f"{year}12" for year in years)
    annual = ",".join(str(year) for year in years)

    def attempt(label, function):
        try:
            function()
        except Exception as error:
            print(f"Aviso: checagem '{label}' indisponível ({error}); linhas ficam MANUAL.")

    def ipca():
        for period, value in sidra("1737", "69", decembers).items():
            refs[(IPCA, int(period[:4]))] = (value, "apisidra 1737 v69 (dezembro)")

    def gdp():
        for period, value in sidra("6784", "9810", annual).items():
            refs[(GDP, int(period))] = (value, "apisidra 6784 v9810")
        for period, value in sidra("6784", "9814", annual).items():
            refs[(GDP_PER_CAPITA, int(period))] = (value, "apisidra 6784 v9814")
        quarters = ",".join(f"{year}04" for year in years)
        for period, value in sidra("5932", "6563", quarters, "c11255/90707").items():
            refs.setdefault((GDP, int(period[:4])), (value, "apisidra 5932 v6563 (4º tri)"))

    def sim():
        groups = tabnet(years.start, years.stop - 1)
        population = sidra("6784", "93", annual)
        for year in years:
            aggression = groups["agressoes"].get(year)
            intervention = groups["intervencao"].get(year)
            if intervention is not None:
                refs[(LEGAL_INTERVENTION, year)] = (intervention, "TabNet SIM, Y35-Y36")
            if groups["indeterminada"].get(year) is not None:
                refs[(UNDETERMINED, year)] = (groups["indeterminada"][year], "TabNet SIM, Y10-Y34")
            if aggression is not None and intervention is not None:
                homicides = aggression + intervention
                refs[(LEGAL_INTERVENTION_SHARE, year)] = (
                    round(100 * intervention / homicides, 2),
                    "TabNet SIM: Y35-Y36 ÷ (X85-Y09 + Y35-Y36)",
                )
                if str(year) in population:
                    refs[(HOMICIDE_RATE, year)] = (
                        round(homicides / (population[str(year)] * 1000) * 100_000, 2),
                        "TabNet SIM (X85-Y09 + Y35-Y36) ÷ população apisidra 6784",
                    )

    def women():
        body = _get("https://www.ipea.gov.br/dados-api/series-values/40/1")
        _save("atlas_serie_40.json", body)
        for item in json.loads(body):
            if item["regiao_id"] == 1076:
                refs[(WOMEN_HOMICIDES, int(item["periodo"][:4]))] = (
                    float(item["valor"]), "Atlas da Violência, série 40")

    def prodes():
        for year, value in inpe_text_checks().items():
            refs[(PRODES, year)] = (value, "texto de notícia oficial do INPE")

    attempt("IPCA", ipca)
    attempt("PIB", gdp)
    attempt("SIM/TabNet", sim)
    attempt("INPE", prodes)
    attempt("Atlas mulheres", women)
    return refs


def compare(rows, refs, tolerance: float = 0.006) -> list[dict[str, str]]:
    results = []
    for row in rows:
        indicator, year = row["indicador"], int(row["ano"])
        value = float(row["valor"])
        reference = refs.get((indicator, year))
        pending = PENDING.get((indicator, year), "")
        if reference is None:
            result, ref_value, difference, source = MANUAL, "", "", "sem checagem automática"
        else:
            ref, source = reference
            diff = value - ref
            result = OK if abs(diff) <= tolerance else DIVERGE
            ref_value, difference = f"{ref:g}", f"{diff:+.4g}"
        results.append({
            "indicador": indicator, "serie": row["serie"], "ano": str(year),
            "periodo_ref": row["periodo_ref"], "valor_csv": row["valor"],
            "valor_checagem": ref_value, "diferenca": difference, "resultado": result,
            "fonte_checagem": source, "como_conferir": MANUAL_LINKS.get(indicator, row["url_fonte"]),
            "pendencia": pending,
        })
    order = {DIVERGE: 0, MANUAL: 1, OK: 2}
    results.sort(key=lambda r: (order[r["resultado"]], not r["pendencia"], r["indicador"], r["ano"]))
    return results


def main() -> int:
    with INDICATORS_FILE.open(encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    years = range(min(int(r["ano"]) for r in rows), max(int(r["ano"]) for r in rows) + 1)
    results = compare(rows, build_references(years))

    with RESULT_FILE.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)
    with LOG_FILE.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=("url", "params", "status", "quando"))
        writer.writeheader()
        writer.writerows(LOG)

    counts = {key: sum(r["resultado"] == key for r in results) for key in (OK, DIVERGE, MANUAL)}
    print(f"{len(results)} linhas: {counts[OK]} OK, {counts[DIVERGE]} divergentes, "
          f"{counts[MANUAL]} para conferência manual; "
          f"{sum(bool(r['pendencia']) for r in results)} com pendência.")
    print(f"Resultado: {RESULT_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
