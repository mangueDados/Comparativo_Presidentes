import json
import unittest

from coleta.atlas_violencia import (
    HOMICIDE_RATE,
    LEGAL_INTERVENTION,
    LEGAL_INTERVENTION_SHARE,
    POPULATION_FILE,
    UNDETERMINED,
    brazil_values,
    build_series,
    load_raw,
    population_by_year,
    to_rows,
)


def item(year, value, region=1076, serie=1):
    return {"periodo": f"{year}-01-15T00:00:00.000Z", "valor": value,
            "regiao_id": region, "serie_id": serie}


class AtlasTests(unittest.TestCase):
    def test_keeps_only_brazil_and_rejects_repeated_year(self):
        self.assertEqual(brazil_values([item(2020, 5), item(2020, 9, region=1276)]), {2020: 5.0})
        with self.assertRaisesRegex(ValueError, "repetido"):
            brazil_values([item(2020, 5), item(2020, 6)])

    def test_share_is_interventions_over_homicides(self):
        series = build_series(
            rate={2020: 10.0}, homicides={2020: 1000.0}, interventions={2020: 50.0},
            undetermined={2020: 7.0}, population={2020: 10_000_000.0},
        )
        self.assertEqual(series[LEGAL_INTERVENTION_SHARE], [(2020, 5.0, "% dos homicídios registrados", (77, 328))])
        self.assertEqual(series[LEGAL_INTERVENTION][0][1], 50)

    def test_rejects_rate_inconsistent_with_population(self):
        with self.assertRaisesRegex(ValueError, "difere"):
            build_series({2020: 11.0}, {2020: 1000.0}, {}, {}, {2020: 10_000_000.0})

    def test_rejects_interventions_above_homicides(self):
        with self.assertRaisesRegex(ValueError, "excedem"):
            build_series({}, {2020: 10.0}, {2020: 11.0}, {}, {})

    def test_rows_carry_year_notes(self):
        series = build_series({}, {2003: 50000.0}, {2003: 491.0}, {}, {})
        rows = dict((row["ano"], row) for name, row in to_rows(series) if name == LEGAL_INTERVENTION)
        self.assertIn("mudança de registro", rows["2003"]["metodologia"])

    def test_raw_files_match_published_totals(self):
        series = build_series(
            brazil_values(load_raw(20)), brazil_values(load_raw(328)),
            brazil_values(load_raw(77)), brazil_values(load_raw(78)),
            population_by_year(json.loads(POPULATION_FILE.read_text(encoding="utf-8"))),
        )
        rate = {year: value for year, value, *_ in series[HOMICIDE_RATE]}
        interventions = {year: value for year, value, *_ in series[LEGAL_INTERVENTION]}
        self.assertEqual(rate[2002], 27.79)
        self.assertEqual(interventions[2024], 2644)
        self.assertEqual(series[UNDETERMINED][-1][0], 2023)


if __name__ == "__main__":
    unittest.main()
