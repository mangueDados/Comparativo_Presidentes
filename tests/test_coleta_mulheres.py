import unittest

from coleta import tabnet
from coleta.sim_mulheres import RAW_FILE, to_rows as women_rows
from coleta.sinesp_feminicidio import annual, to_rows as femicide_rows


class FemicideTests(unittest.TestCase):
    def test_excludes_incomplete_year_and_marks_preliminary(self):
        monthly = {f"2025-{m:02d}": {"vitimas": 10, "feminino": 9} for m in range(1, 13)}
        monthly.update({f"2026-{m:02d}": {"vitimas": 5, "feminino": 5} for m in range(1, 9)})
        years = annual(monthly)
        self.assertEqual(years[2025], (120, 108, 12))
        rows = femicide_rows(years)
        self.assertEqual([r["ano"] for r in rows], ["2025"])
        self.assertEqual(rows[0]["tipo_dado"], "preliminar")
        self.assertIn("12 sem essa marcação", rows[0]["metodologia"])


class WomenHomicideTests(unittest.TestCase):
    def test_sums_aggression_and_legal_intervention(self):
        groups = {"agressoes": {y: 100 for y in range(2002, 2025)},
                  "intervencao": {y: 2 for y in range(2002, 2025)}}
        rows = women_rows(groups)
        self.assertEqual((rows[0]["ano"], rows[0]["valor"]), ("2002", "102"))
        self.assertEqual(rows[-1]["ano"], "2024")

    def test_raw_file_matches_atlas(self):
        groups = tabnet.parse(RAW_FILE.read_text(encoding="utf-8"))
        values = {r["ano"]: r["valor"] for r in women_rows(groups)}
        self.assertEqual((values["2002"], values["2023"]), ("3868", "3903"))


if __name__ == "__main__":
    unittest.main()
