"""Funções compartilhadas pelos scripts de coleta."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analise_comparativo import REQUIRED_COLUMNS  # noqa: E402

INDICATORS_FILE = ROOT / "dados" / "indicadores.csv"
MONTHS = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")


def merge_into(path: Path, indicator: str, series: str, new_rows: list[dict[str, str]]) -> None:
    """Substitui só as linhas da série informada, preservando as demais.

    Uma linha nova ou alterada entra com validada=nao. Uma linha idêntica à já
    conferida, em todos os campos exceto 'validada', mantém a validação.
    """
    others: list[dict[str, str]] = []
    validated: set[tuple[str, ...]] = set()
    if path.is_file():
        with path.open(encoding="utf-8-sig", newline="") as csv_file:
            for row in csv.DictReader(csv_file):
                if (row["indicador"], row["serie"]) != (indicator, series):
                    others.append(row)
                elif row["validada"].strip().casefold() == "sim":
                    validated.add(_content(row))
    for row in new_rows:
        row["validada"] = "sim" if _content(row) in validated else "nao"
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(others + new_rows)


def _content(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[column] for column in REQUIRED_COLUMNS if column != "validada")
