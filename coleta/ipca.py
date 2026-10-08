"""Transforma o arquivo bruto do IPCA (IBGE/SIDRA, tabela 1737) em linhas do
CSV de indicadores: variação acumulada no ano, só para anos completos.

Uso, a partir da raiz do projeto:
    python coleta/ipca.py

O arquivo bruto é a resposta da API de agregados do IBGE para as variáveis 69
(variação acumulada no ano) e 2266 (número-índice), salva sem edição. Cada
valor publicado é conferido contra o recalculado pelo número-índice.
"""

from __future__ import annotations

import argparse
import calendar
import json
from pathlib import Path

try:
    from coleta.comum import INDICATORS_FILE, ROOT, merge_into
except ModuleNotFoundError:  # execução direta: python coleta/ipca.py
    from comum import INDICATORS_FILE, ROOT, merge_into

RAW_FILE = ROOT / "dados" / "brutos" / "ibge_sidra_1737_ipca_acesso-2026-10-06.json"
SOURCE_URL = "https://sidra.ibge.gov.br/tabela/1737"
ACCESS_DATE = "2026-10-06"
# Último ano-calendário inteiramente anterior à posse de 2003 (base, ADR-009).
FIRST_YEAR = 2002
# Diferença máxima aceita entre o publicado (2 casas) e o recalculado.
TOLERANCE = 0.006

INDICATOR = "Inflação (IPCA) acumulada no ano"
SERIES = "Brasil"


def _series(raw: list[dict], variable_id: str) -> dict[str, str]:
    for variable in raw:
        if variable["id"] == variable_id:
            return variable["resultados"][0]["series"][0]["serie"]
    raise ValueError(f"Variável {variable_id} ausente no arquivo bruto.")


def annual_rates(raw: list[dict]) -> tuple[list[tuple[int, float]], str]:
    """Variação de janeiro a dezembro de cada ano completo e o último mês
    publicado. Falha se o publicado divergir do número-índice."""
    accumulated = _series(raw, "69")
    index = _series(raw, "2266")
    last_month = max(accumulated)
    rates = []
    for period in sorted(accumulated):
        year = int(period[:4])
        if period[4:] != "12" or year < FIRST_YEAR:
            continue
        published = float(accumulated[period])
        recalculated = (float(index[period]) / float(index[f"{year - 1}12"]) - 1) * 100
        if abs(published - recalculated) > TOLERANCE:
            raise ValueError(
                f"IPCA {year}: publicado {published} difere do recalculado "
                f"{recalculated:.4f} pelo número-índice."
            )
        rates.append((year, published))
    return rates, last_month


def to_rows(rates: list[tuple[int, float]]) -> list[dict[str, str]]:
    return [
        {
            "indicador": INDICATOR,
            "serie": SERIES,
            "ano": str(year),
            "valor": f"{value:.2f}",
            "unidade": "% no ano",
            "fonte": "IBGE, IPCA (SIDRA, tabela 1737)",
            "url_fonte": SOURCE_URL,
            "periodo_ref": f"jan–dez/{year}",
            "inicio_periodo": f"{year}-01-01",
            "fim_periodo": f"{year}-12-{calendar.monthrange(year, 12)[1]}",
            "tipo_dado": "observado",
            "data_acesso": ACCESS_DATE,
            "validada": "nao",
            "metodologia": (
                "Variação acumulada no ano (variável 69), conferida contra o "
                "número-índice (variável 2266, base dez/1993=100). Só anos "
                "completos; transformação em coleta/ipca.py."
            ),
        }
        for year, value in rates
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=INDICATORS_FILE)
    args = parser.parse_args()

    raw = json.loads(RAW_FILE.read_text(encoding="utf-8"))
    rates, last_month = annual_rates(raw)
    rows = to_rows(rates)
    merge_into(args.output, INDICATOR, SERIES, rows)
    print(f"{len(rows)} linhas de '{INDICATOR} / {SERIES}' gravadas em {args.output}")
    if not last_month.endswith("12"):
        print(
            f"Ano em curso excluído: dado só até {last_month[4:]}/{last_month[:4]}; "
            "acumulado parcial não é comparável a anos completos."
        )
    print("Linhas novas ou alteradas ficam com validada=nao até a conferência.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
