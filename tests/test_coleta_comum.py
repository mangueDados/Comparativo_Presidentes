import csv
import tempfile
import unittest
from pathlib import Path

from analise_comparativo import REQUIRED_COLUMNS
from coleta.comum import merge_into


def row(indicator, year, value, validated="nao"):
    base = {column: "x" for column in REQUIRED_COLUMNS}
    base.update(indicador=indicator, serie="Brasil", ano=year, valor=value, validada=validated)
    return base


class MergeIntoTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "indicadores.csv"

    def read(self):
        with self.path.open(encoding="utf-8") as csv_file:
            return list(csv.DictReader(csv_file))

    def test_keeps_other_series_and_validation_of_unchanged_rows(self):
        merge_into(self.path, "B", "Brasil", [row("B", "2020", "1")])
        rows = self.read()
        rows[0]["validada"] = "sim"
        with self.path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerows(rows + [row("A", "2020", "9", "sim")])

        merge_into(self.path, "B", "Brasil", [row("B", "2020", "1"), row("B", "2021", "2")])

        result = {(r["indicador"], r["ano"]): r["validada"] for r in self.read()}
        self.assertEqual(
            result, {("A", "2020"): "sim", ("B", "2020"): "sim", ("B", "2021"): "nao"}
        )

    def test_changed_value_requires_new_validation(self):
        merge_into(self.path, "B", "Brasil", [row("B", "2020", "1", "sim")])
        merge_into(self.path, "B", "Brasil", [row("B", "2020", "1.5")])
        self.assertEqual(self.read()[0]["validada"], "nao")


if __name__ == "__main__":
    unittest.main()
