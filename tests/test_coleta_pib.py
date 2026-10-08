import json
import unittest

from coleta.pib import ANNUAL_FILE, QUARTERLY_FILE, gdp_rates


def raw(variables):
    return [
        {"id": variable_id, "resultados": [{"series": [{"serie": serie}]}]}
        for variable_id, serie in variables.items()
    ]


class PibTests(unittest.TestCase):
    def test_quarterly_only_fills_years_after_last_annual_as_preliminary(self):
        annual = raw({"9810": {"2002": "3.1", "2003": "1.1"}, "9814": {"2002": "1.8", "2003": "-0.1"}})
        quarterly = raw({"6563": {"200304": "1.2", "200402": "4.0", "200404": "5.8", "200502": "3.0"}})
        gdp, per_capita, last_quarter = gdp_rates(annual, quarterly)
        self.assertEqual(
            gdp,
            [(2002, 3.1, "observado", "anual"), (2003, 1.1, "observado", "anual"),
             (2004, 5.8, "preliminar", "trimestral")],
        )
        self.assertEqual(per_capita, [(2002, 1.8), (2003, -0.1)])
        self.assertEqual(last_quarter, "200502")

    def test_rejects_divergence_between_annual_and_quarterly(self):
        annual = raw({"9810": {"2003": "1.1"}, "9814": {"2003": "-0.1"}})
        quarterly = raw({"6563": {"200304": "1.5"}})
        with self.assertRaisesRegex(ValueError, "divergem"):
            gdp_rates(annual, quarterly)

    def test_raw_files_match_known_ibge_values(self):
        gdp, per_capita, _ = gdp_rates(
            json.loads(ANNUAL_FILE.read_text(encoding="utf-8")),
            json.loads(QUARTERLY_FILE.read_text(encoding="utf-8")),
        )
        values = {year: (value, kind) for year, value, kind, _ in gdp}
        self.assertEqual(values[2015], (-3.5, "observado"))
        self.assertEqual(values[2020], (-3.3, "observado"))
        self.assertEqual(values[2023], (3.2, "observado"))
        self.assertEqual(values[2025], (2.3, "preliminar"))
        self.assertNotIn(2026, values)
        self.assertEqual(per_capita[-1], (2023, 2.8))


if __name__ == "__main__":
    unittest.main()
