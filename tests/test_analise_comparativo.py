import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path

from analise_comparativo import (
    GOVERNMENT_COLUMNS,
    REQUIRED_COLUMNS,
    DataValidationError,
    create_outputs,
    describe_overlap,
    format_axis_number,
    format_number,
    focus_rows,
    government_overlap,
    load_notes,
    validate_csv,
    validate_governments,
)

ROOT = Path(__file__).resolve().parent.parent
TODAY = date(2026, 10, 6)


def write_csv(test_case, headers, rows, name="dados.csv"):
    temporary_directory = tempfile.TemporaryDirectory()
    test_case.addCleanup(temporary_directory.cleanup)
    path = Path(temporary_directory.name) / name
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return path


def government(name, start, end, president=None):
    return {"governo": name, "presidente": president or name.split()[0],
            "inicio": date.fromisoformat(start),
            "fim": date.fromisoformat(end) if end else None}


# Datas fictícias, independentes de dados/governos.csv.
GOVERNMENTS = [
    government("A", "2015-01-01", "2016-05-11"),
    government("B interino", "2016-05-12", "2016-08-30"),
    government("B", "2016-08-31", "2018-12-31"),
    government("C", "2019-01-01", None),
]


class ValidateCsvTests(unittest.TestCase):
    def write(self, rows):
        return write_csv(self, list(REQUIRED_COLUMNS), rows)

    def example_row(self, **overrides):
        row = {
            "indicador": "Indicador de teste",
            "serie": "Brasil",
            "ano": "2020",
            "valor": "1.5",
            "unidade": "unidade de teste",
            "fonte": "Fonte de teste",
            "url_fonte": "https://example.org/dados",
            "periodo_ref": "ano-calendário 2020",
            "inicio_periodo": "2020-01-01",
            "fim_periodo": "2020-12-31",
            "tipo_dado": "observado",
            "data_acesso": "2026-10-01",
            "validada": "sim",
            "metodologia": "metodologia fictícia usada somente no teste",
        }
        row.update(overrides)
        return row

    def assert_rejected(self, message, rows):
        with self.assertRaisesRegex(DataValidationError, message):
            validate_csv(self.write(rows), today=TODAY)

    def test_accepts_a_documented_valid_observation(self):
        rows = validate_csv(self.write([self.example_row()]), today=TODAY)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ano"], 2020)
        self.assertEqual(rows[0]["valor"], 1.5)
        self.assertEqual(rows[0]["inicio_periodo"], date(2020, 1, 1))

    def test_rejects_unvalidated_observation(self):
        self.assert_rejected("não está validada", [self.example_row(validada="não")])

    def test_preview_accepts_unvalidated_but_keeps_other_rules(self):
        rows = validate_csv(
            self.write([self.example_row(validada="nao")]), today=TODAY, allow_unvalidated=True
        )
        self.assertEqual(rows[0]["validada"], "nao")
        with self.assertRaisesRegex(DataValidationError, "futuro"):
            validate_csv(
                self.write([self.example_row(validada="nao", data_acesso="2027-01-01")]),
                today=TODAY, allow_unvalidated=True,
            )

    def test_rejects_duplicate_year_in_same_series(self):
        self.assert_rejected(
            "ano duplicado", [self.example_row(), self.example_row(valor="2.5")]
        )

    def test_rejects_inconsistent_units_in_series(self):
        self.assert_rejected(
            "inconsistente",
            [
                self.example_row(),
                self.example_row(
                    ano="2021",
                    inicio_periodo="2021-01-01",
                    fim_periodo="2021-12-31",
                    unidade="outra unidade",
                ),
            ],
        )

    def test_rejects_overlapping_periods_in_same_series(self):
        self.assert_rejected(
            "sobrepõe",
            [
                self.example_row(),
                self.example_row(
                    ano="2021", inicio_periodo="2020-08-01", fim_periodo="2021-07-31"
                ),
            ],
        )

    def test_rejects_period_ending_before_it_starts(self):
        self.assert_rejected(
            "posterior", [self.example_row(inicio_periodo="2021-01-01")]
        )

    def test_rejects_invalid_dates(self):
        self.assert_rejected("AAAA-MM-DD", [self.example_row(fim_periodo="31/12/2020")])

    def test_rejects_future_access_date(self):
        self.assert_rejected("futuro", [self.example_row(data_acesso="2026-10-07")])

    def test_rejects_unknown_data_type(self):
        self.assert_rejected("tipo_dado", [self.example_row(tipo_dado="projeção")])

    def test_rejects_missing_new_columns(self):
        path = write_csv(
            self, [c for c in REQUIRED_COLUMNS if c != "data_acesso"], []
        )
        with self.assertRaisesRegex(DataValidationError, "data_acesso"):
            validate_csv(path, today=TODAY)

    def test_rejects_row_with_more_values_than_header(self):
        path = self.write([self.example_row()])
        with path.open("a", encoding="utf-8") as csv_file:
            csv_file.write(",".join(self.example_row(ano="2021").values()) + ",extra\n")
        with self.assertRaisesRegex(DataValidationError, "mais valores"):
            validate_csv(path, today=TODAY)

    def test_accepts_source_urls_that_change_between_observations(self):
        rows = validate_csv(
            self.write(
                [
                    self.example_row(),
                    self.example_row(
                        ano="2021",
                        inicio_periodo="2021-01-01",
                        fim_periodo="2021-12-31",
                        url_fonte="https://example.org/dados-2021",
                    ),
                ]
            ),
            today=TODAY,
        )
        self.assertEqual(len(rows), 2)

    def test_project_template_has_expected_header(self):
        with (ROOT / "dados" / "indicadores_modelo.csv").open(encoding="utf-8") as f:
            self.assertEqual(next(csv.reader(f)), list(REQUIRED_COLUMNS))


class GovernmentTests(unittest.TestCase):
    def example_row(self, **overrides):
        row = {
            "governo": "A",
            "presidente": "Pessoa A",
            "condicao": "titular",
            "inicio": "2019-01-01",
            "fim": "2022-12-31",
            "fonte": "Fonte de teste",
            "url_fonte": "https://example.org/governo",
            "data_acesso": "2026-10-01",
            "validada": "sim",
        }
        row.update(overrides)
        return row

    def validate(self, rows):
        return validate_governments(
            write_csv(self, list(GOVERNMENT_COLUMNS), rows), today=TODAY
        )

    def test_accepts_open_ended_current_government(self):
        governments = self.validate(
            [self.example_row(), self.example_row(governo="B", inicio="2023-01-01", fim="")]
        )
        self.assertIsNone(governments[-1]["fim"])

    def test_rejects_overlapping_governments(self):
        with self.assertRaisesRegex(DataValidationError, "começa antes"):
            self.validate(
                [self.example_row(), self.example_row(governo="B", inicio="2022-12-31", fim="")]
            )

    def test_rejects_open_end_before_last_government(self):
        with self.assertRaisesRegex(DataValidationError, "mais recente"):
            self.validate(
                [self.example_row(fim=""),
                 self.example_row(governo="B", inicio="2023-01-01", fim="2024-12-31")]
            )

    def test_rejects_unvalidated_government(self):
        with self.assertRaisesRegex(DataValidationError, "não está validado"):
            self.validate([self.example_row(validada="não")])

    def test_project_governments_file_is_valid(self):
        governments = validate_governments(ROOT / "dados" / "governos.csv", today=TODAY)
        self.assertEqual(governments[0]["inicio"], date(2003, 1, 1))
        self.assertIsNone(governments[-1]["fim"])


class OverlapTests(unittest.TestCase):
    def test_calendar_year_within_one_government_is_not_mixed(self):
        text, mixed, _ = describe_overlap(date(2020, 1, 1), date(2020, 12, 31), GOVERNMENTS)
        self.assertFalse(mixed)
        self.assertEqual(text, "C: 366 de 366 dias (100%)")

    def test_transition_year_lists_every_government_with_days(self):
        overlaps, uncovered = government_overlap(
            date(2016, 1, 1), date(2016, 12, 31), GOVERNMENTS
        )
        self.assertEqual(
            [(g["governo"], days) for g, days in overlaps],
            [("A", 132), ("B interino", 111), ("B", 123)],
        )
        self.assertEqual(uncovered, 0)
        _, mixed, change = describe_overlap(date(2016, 1, 1), date(2016, 12, 31), GOVERNMENTS)
        self.assertTrue(mixed)
        self.assertTrue(change)

    def test_change_of_term_by_same_president_is_mixed_without_president_change(self):
        _, mixed, change = describe_overlap(date(2016, 8, 1), date(2017, 7, 31), GOVERNMENTS)
        self.assertTrue(mixed)
        self.assertFalse(change)

    def test_august_to_july_period_crossing_inauguration_is_mixed(self):
        overlaps, _ = government_overlap(date(2018, 8, 1), date(2019, 7, 31), GOVERNMENTS)
        self.assertEqual([(g["governo"], days) for g, days in overlaps], [("B", 153), ("C", 212)])

    def test_period_before_first_government_is_reported_as_uncovered(self):
        text, mixed, _ = describe_overlap(date(2014, 1, 1), date(2014, 12, 31), GOVERNMENTS)
        self.assertFalse(mixed)
        self.assertIn("sem governo cadastrado: 365 de 365 dias", text)


class FocusTests(unittest.TestCase):
    def frame(self, periods):
        import pandas as pd

        return pd.DataFrame(
            {"inicio_periodo": [date.fromisoformat(a) for a, _ in periods],
             "fim_periodo": [date.fromisoformat(b) for _, b in periods]}
        )

    def test_selects_periods_touching_focus_and_leaves_mixed_unassigned(self):
        group = self.frame([
            ("2017-01-01", "2017-12-31"),  # só B: fora do recorte
            ("2018-08-01", "2019-07-31"),  # B e C: misto, não atribuído
            ("2020-01-01", "2020-12-31"),  # só C
        ])
        self.assertEqual(focus_rows(group, GOVERNMENTS, ("C",)), [(1, None), (2, "C")])

    def test_outputs_focus_and_history_charts(self):
        import pandas  # noqa: F401  (dependência do gráfico)

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        output_dir = Path(directory.name)
        rows = OutputTests.rows(self)
        generated = create_outputs(rows, output_dir, GOVERNMENTS, focus=("C",))
        names = {path.name for path in generated}
        self.assertIn("indicador-de-teste--brasil.png", names)
        self.assertIn("indicador-de-teste--brasil--historico--celular.png", names)


class OutputTests(unittest.TestCase):
    def rows(self):
        base = {
            "indicador": "Indicador de teste",
            "serie": "Brasil",
            "unidade": "unidade de teste",
            "fonte": "Fonte de teste",
            "url_fonte": "https://example.org/dados",
            "data_acesso": date(2026, 10, 1),
            "validada": "sim",
            "metodologia": "fictícia",
        }
        return [
            {**base, "ano": 2016, "valor": 2.0, "periodo_ref": "ago/2015–jul/2016",
             "inicio_periodo": date(2015, 8, 1), "fim_periodo": date(2016, 7, 31),
             "tipo_dado": "observado"},
            {**base, "ano": 2018, "valor": 1.25, "periodo_ref": "ago/2017–jul/2018",
             "inicio_periodo": date(2017, 8, 1), "fim_periodo": date(2018, 7, 31),
             "tipo_dado": "observado"},
            {**base, "ano": 2020, "valor": 3.0, "periodo_ref": "ago/2019–jul/2020",
             "inicio_periodo": date(2019, 8, 1), "fim_periodo": date(2020, 7, 31),
             "tipo_dado": "preliminar"},
        ]

    def output_dir(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        return Path(temporary_directory.name) / "saida"

    def test_generates_chart_table_and_summary_with_governments(self):
        output_dir = self.output_dir()
        generated = create_outputs(self.rows(), output_dir, GOVERNMENTS)

        self.assertEqual(len(generated), 4)
        self.assertTrue(any(path.suffix == ".png" for path in generated))
        with (output_dir / "dados_validados.csv").open(encoding="utf-8-sig") as f:
            table = list(csv.DictReader(f))
        self.assertEqual([row["periodo_misto"] for row in table], ["sim", "não", "não"])

        summary = (output_dir / "resumos.md").read_text(encoding="utf-8")
        self.assertIn("Menor valor: 1,25 (ago/2017–jul/2018)", summary)
        self.assertIn("Anos-rótulo sem observação entre o primeiro e o último: 2017, 2019", summary)
        self.assertIn("Períodos com troca de presidente: ago/2015–jul/2016", summary)
        self.assertIn("troca_de_presidente", table[0])
        self.assertIn("preliminar (1)", summary)
        self.assertNotRegex(summary.lower(), r"\bcausou\b|\bgraças\b|\bculpa\b")

    def test_refuses_series_without_context_note(self):
        with self.assertRaisesRegex(DataValidationError, "Sem nota de contexto"):
            create_outputs(self.rows(), self.output_dir(), GOVERNMENTS, notes={})

    def test_context_note_goes_to_summary(self):
        output_dir = self.output_dir()
        create_outputs(self.rows(), output_dir, notes={"Indicador de teste": "Nota X."})
        self.assertIn("- Atenção: Nota X.", (output_dir / "resumos.md").read_text(encoding="utf-8"))

    def test_generates_outputs_without_governments(self):
        output_dir = self.output_dir()
        create_outputs(self.rows(), output_dir)
        with (output_dir / "dados_validados.csv").open(encoding="utf-8-sig") as f:
            self.assertNotIn("periodo_misto", next(csv.reader(f)))
        self.assertNotIn(
            "Governos em exercício",
            (output_dir / "resumos.md").read_text(encoding="utf-8"),
        )


class NotesTests(unittest.TestCase):
    def write(self, rows):
        return write_csv(self, ["id", "indicador_csv", "nota_grafico"], rows)

    def test_reads_only_linked_indicators(self):
        notes = load_notes(self.write([
            {"id": "a", "indicador_csv": "Indicador A", "nota_grafico": "Contexto A."},
            {"id": "b", "indicador_csv": "", "nota_grafico": ""},
        ]))
        self.assertEqual(notes, {"Indicador A": "Contexto A."})

    def test_rejects_linked_indicator_without_note_or_duplicated(self):
        with self.assertRaisesRegex(DataValidationError, "sem nota_grafico"):
            load_notes(self.write([{"id": "a", "indicador_csv": "A", "nota_grafico": ""}]))
        with self.assertRaisesRegex(DataValidationError, "mais de uma vez"):
            load_notes(self.write([
                {"id": "a", "indicador_csv": "A", "nota_grafico": "x"},
                {"id": "b", "indicador_csv": "A", "nota_grafico": "y"},
            ]))

    def test_project_dictionary_is_valid(self):
        self.assertIn(
            "Taxa de homicídios registrados",
            load_notes(ROOT / "dados" / "dicionario_indicadores.csv"),
        )


class FormatTests(unittest.TestCase):
    def test_axis_numbers_use_brazilian_separators(self):
        self.assertEqual(
            [format_axis_number(v) for v in (0, 25000.0, 1234567, 2.5, -1500)],
            ["0", "25.000", "1.234.567", "2,5", "-1.500"],
        )

    def test_format_number_uses_decimal_comma_without_rounding(self):
        self.assertEqual(format_number(13235.0), "13235")
        self.assertEqual(format_number(5.43), "5,43")


if __name__ == "__main__":
    unittest.main()
