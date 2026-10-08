"""Transforma o arquivo bruto de taxas PRODES Amazônia Legal (INPE) em linhas
do CSV de indicadores, sempre com validada=nao para conferência editorial.

Uso, a partir da raiz do projeto:
    python coleta/prodes_amazonia.py

O arquivo bruto é o JSON que alimenta o painel TerraBrasilis, salvo sem edição
em dados/brutos/. Ele traz a taxa por estado; a taxa da Amazônia Legal é a
soma dos nove estados em cada período.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

try:
    from coleta.comum import INDICATORS_FILE, MONTHS, ROOT, merge_into
except ModuleNotFoundError:  # execução direta: python coleta/prodes_amazonia.py
    from comum import INDICATORS_FILE, MONTHS, ROOT, merge_into

RAW_FILE = ROOT / "dados" / "brutos" / "inpe_prodes_amazonia_rates2025_acesso-2026-10-06.json"
SOURCE_URL = (
    "https://terrabrasilis.dpi.inpe.br/app/prodes/dashboard/deforestation/files/rates2025.json"
)
ACCESS_DATE = "2026-10-06"
EXPECTED_STATES = 9
# Primeiro ano PRODES inteiramente anterior à posse de 2003 (base, ADR-002).
FIRST_YEAR = 2002

INDICATOR = "Taxa de desmatamento PRODES"
SERIES = "Amazônia Legal"


def _to_date(parts: dict) -> date:
    return date(parts["year"], parts["month"], parts["day"])


def rates_by_period(raw: dict) -> list[tuple[date, date, int]]:
    """Soma a taxa dos estados em cada período; falha se faltar algum estado."""
    if raw.get("name") != "PRODES LEGAL AMAZON":
        raise ValueError(f"Arquivo inesperado: name={raw.get('name')!r}.")
    periods = []
    for period in raw["periods"]:
        start, end = _to_date(period["startDate"]), _to_date(period["endDate"])
        states = {feature["loiname"] for feature in period["features"]}
        if len(states) != EXPECTED_STATES or len(period["features"]) != EXPECTED_STATES:
            raise ValueError(
                f"Período {start}–{end}: esperados {EXPECTED_STATES} estados, "
                f"encontrados {len(states)}."
            )
        total = sum(area["area"] for feature in period["features"] for area in feature["areas"])
        periods.append((start, end, total))
    return periods


def to_rows(periods: list[tuple[date, date, int]]) -> list[dict[str, str]]:
    rows = []
    for start, end, total in periods:
        if end.year < FIRST_YEAR:
            continue
        rows.append(
            {
                "indicador": INDICATOR,
                "serie": SERIES,
                "ano": str(end.year),
                "valor": str(total),
                "unidade": "km²/ano",
                "fonte": "INPE, PRODES (TerraBrasilis)",
                "url_fonte": SOURCE_URL,
                "periodo_ref": (
                    f"{MONTHS[start.month - 1]}/{start.year}–"
                    f"{MONTHS[end.month - 1]}/{end.year} (ano PRODES {end.year})"
                ),
                "inicio_periodo": start.isoformat(),
                "fim_periodo": end.isoformat(),
                "tipo_dado": "observado",
                "data_acesso": ACCESS_DATE,
                "validada": "nao",
                "metodologia": (
                    "Taxa anual consolidada estimada pelo INPE por imagens de satélite "
                    "(corte raso). Soma das taxas dos 9 estados da Amazônia Legal no "
                    "arquivo do painel TerraBrasilis (atualização de 2026-08-07); "
                    "transformação em coleta/prodes_amazonia.py."
                ),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=INDICATORS_FILE)
    args = parser.parse_args()

    raw = json.loads(RAW_FILE.read_text(encoding="utf-8"))
    rows = to_rows(rates_by_period(raw))
    merge_into(args.output, INDICATOR, SERIES, rows)
    print(f"{len(rows)} linhas de '{INDICATOR} / {SERIES}' gravadas em {args.output}")
    print("Todas com validada=nao: confira cada valor na fonte antes de marcar 'sim'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
