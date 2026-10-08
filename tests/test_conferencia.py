import csv
import tempfile
import unittest
from pathlib import Path

from analise_comparativo import REQUIRED_COLUMNS
from conferencia.aplicar import apply
from coleta.tabnet import parse as parse_tabnet
from conferencia.verificar import DIVERGE, MANUAL, OK, compare


def csv_row(indicator, year, value):
    row = {column: "x" for column in REQUIRED_COLUMNS}
    row.update(indicador=indicator, serie="Brasil", ano=str(year), valor=str(value),
               periodo_ref=f"{year}", url_fonte="https://example.org", validada="nao")
    return row


class CompareTests(unittest.TestCase):
    def test_classifies_and_puts_problems_first(self):
        rows = [csv_row("A", 2020, 1.0), csv_row("A", 2021, 2.0), csv_row("A", 2022, 3.0)]
        refs = {("A", 2020): (1.004, "x"), ("A", 2021): (2.5, "x")}
        result = {r["ano"]: r["resultado"] for r in compare(rows, refs)}
        self.assertEqual(result, {"2020": OK, "2021": DIVERGE, "2022": MANUAL})
        self.assertEqual(compare(rows, refs)[0]["resultado"], DIVERGE)


class TabnetTests(unittest.TestCase):
    def test_parses_cause_groups_by_year(self):
        body = ('<PRE>"Grande Grupo CID10";"2023";"2024";"Total"\n'
                '"X85-Y09 Agressões";43443;39946;83389\n'
                '"Y10-Y34 Eventos cuja intenção é indeterminada";13896;17207;31103\n'
                '"Y35-Y36 Intervenções legais e operações de guerra";2304;2644;4948\n'
                '"Total";59643;59797;119440\n</PRE>')
        groups = parse_tabnet(body)
        self.assertEqual(groups["intervencao"], {2023: 2304, 2024: 2644})
        self.assertEqual(groups["agressoes"][2024] + groups["intervencao"][2024], 42590)


class ApplyTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.csv = Path(directory.name) / "indicadores.csv"
        self.register = Path(directory.name) / "registro.csv"
        with self.csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerows([csv_row("A", 2020, 1.0), csv_row("A", 2021, 2.0),
                              csv_row("A", 2022, 3.0), csv_row("A", 2023, 4.0)])

    def decision(self, year, value, decisao, nome="Fulana"):
        return {"indicador": "A", "serie": "Brasil", "ano": year, "valor_csv": value,
                "decisao": decisao, "conferido_por": nome, "resultado": "OK"}

    def test_only_signed_approvals_with_unchanged_value_are_applied(self):
        report = apply([
            self.decision(2020, 1.0, "aprovar"),
            self.decision(2021, 2.0, "aprovar", nome=""),
            self.decision(2022, 9.9, "aprovar"),
            self.decision(2023, 4.0, "rejeitar"),
        ], self.csv, self.register)
        with self.csv.open(encoding="utf-8") as f:
            validated = {r["ano"]: r["validada"] for r in csv.DictReader(f)}
        self.assertEqual(validated, {"2020": "sim", "2021": "nao", "2022": "nao", "2023": "nao"})
        self.assertEqual(len(report["sem_nome"]), 1)
        self.assertEqual(len(report["valor_mudou"]), 1)
        with self.register.open(encoding="utf-8") as f:
            self.assertEqual([r["conferido_por"] for r in csv.DictReader(f)], ["Fulana"])


if __name__ == "__main__":
    unittest.main()
