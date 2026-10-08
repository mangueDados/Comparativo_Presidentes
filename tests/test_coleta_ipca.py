import json
import unittest

from coleta.ipca import RAW_FILE, annual_rates, to_rows


def raw(accumulated, index):
    return [
        {"id": "69", "resultados": [{"series": [{"serie": accumulated}]}]},
        {"id": "2266", "resultados": [{"series": [{"serie": index}]}]},
    ]


class IpcaTests(unittest.TestCase):
    def test_uses_only_complete_years_and_reports_last_month(self):
        rates, last_month = annual_rates(
            raw(
                {"200212": "10.00", "200312": "5.00", "200403": "1.00"},
                {"200112": "100", "200212": "110", "200312": "115.5", "200403": "116.66"},
            )
        )
        self.assertEqual(rates, [(2002, 10.0), (2003, 5.0)])
        self.assertEqual(last_month, "200403")

    def test_rejects_published_value_inconsistent_with_index(self):
        with self.assertRaisesRegex(ValueError, "difere"):
            annual_rates(raw({"200212": "11.00"}, {"200112": "100", "200212": "110"}))

    def test_rows_cover_calendar_year(self):
        row = to_rows([(2016, 6.29)])[0]
        self.assertEqual((row["inicio_periodo"], row["fim_periodo"]), ("2016-01-01", "2016-12-31"))
        self.assertEqual(row["valor"], "6.29")

    def test_raw_file_matches_known_ibge_values(self):
        rates, last_month = annual_rates(json.loads(RAW_FILE.read_text(encoding="utf-8")))
        rates = dict(rates)
        self.assertEqual((rates[2002], rates[2015], rates[2025]), (12.53, 10.67, 4.26))
        self.assertNotIn(2026, rates)
        self.assertEqual(last_month, "202608")


if __name__ == "__main__":
    unittest.main()
