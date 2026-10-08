import json
import unittest
from datetime import date

from coleta.prodes_amazonia import RAW_FILE, rates_by_period, to_rows


def period(start_year, areas):
    return {
        "startDate": {"year": start_year, "month": 8, "day": 1},
        "endDate": {"year": start_year + 1, "month": 7, "day": 31},
        "features": [
            {"loi": 1, "loiname": state, "areas": [{"type": 1, "area": area}]}
            for state, area in enumerate(areas)
        ],
    }


class ProdesAmazoniaTests(unittest.TestCase):
    def test_sums_the_nine_states_and_keeps_august_to_july_period(self):
        raw = {"name": "PRODES LEGAL AMAZON", "periods": [period(2018, [1] * 8 + [100])]}
        self.assertEqual(
            rates_by_period(raw), [(date(2018, 8, 1), date(2019, 7, 31), 108)]
        )

    def test_rejects_period_with_missing_state(self):
        raw = {"name": "PRODES LEGAL AMAZON", "periods": [period(2018, [1] * 8)]}
        with self.assertRaisesRegex(ValueError, "esperados 9"):
            rates_by_period(raw)

    def test_rows_start_at_base_year_and_are_not_validated(self):
        raw = {"name": "PRODES LEGAL AMAZON",
               "periods": [period(2000, [1] * 9), period(2001, [2] * 9)]}
        rows = to_rows(rates_by_period(raw))
        self.assertEqual([row["ano"] for row in rows], ["2002"])
        self.assertEqual(rows[0]["validada"], "nao")
        self.assertEqual(rows[0]["periodo_ref"], "ago/2001–jul/2002 (ano PRODES 2002)")

    def test_raw_file_matches_rates_published_by_inpe(self):
        # Valores divulgados pelo INPE: 2022 (nota técnica consolidada) e
        # 2024/2025 (notícia da taxa consolidada de 2025).
        raw = json.loads(RAW_FILE.read_text(encoding="utf-8"))
        rates = {end.year: total for _, end, total in rates_by_period(raw)}
        self.assertEqual(rates[2022], 11594)
        self.assertEqual(rates[2024], 6518)
        self.assertEqual(rates[2025], 5731)


if __name__ == "__main__":
    unittest.main()
