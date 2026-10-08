"""Aplica as decisões da planilha de conferência em dados/indicadores.csv.

Uso, a partir da raiz do projeto:
    python conferencia/aplicar.py conferencia/conferencia_comparativo_v1_AAAAMMDD.xlsx

Marca validada=sim só nas linhas com decisao='aprovar', nome em
'conferido_por' e valor igual ao do CSV atual. Cada aprovação fica registrada
em conferencia/registro_conferencia.csv (quem, quando, o quê).
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analise_comparativo import REQUIRED_COLUMNS  # noqa: E402

INDICATORS_FILE = ROOT / "dados" / "indicadores.csv"
REGISTER_FILE = ROOT / "conferencia" / "registro_conferencia.csv"
REGISTER_COLUMNS = ("quando", "conferido_por", "indicador", "serie", "ano", "valor",
                    "resultado_automatico", "observacao")


def read_decisions(path: Path) -> list[dict[str, object]]:
    ws = load_workbook(path, data_only=True)["Conferência"]
    header = [cell.value for cell in ws[5]]
    return [dict(zip(header, row)) for row in ws.iter_rows(min_row=6, values_only=True)]


def apply(decisions, indicators_file: Path = INDICATORS_FILE,
          register_file: Path = REGISTER_FILE) -> dict[str, list[str]]:
    with indicators_file.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    index = {(r["indicador"], r["serie"], r["ano"]): r for r in rows}
    report: dict[str, list[str]] = {"aprovadas": [], "rejeitadas": [], "sem_nome": [],
                                    "valor_mudou": [], "pendentes": 0}
    register = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for d in decisions:
        decision = str(d.get("decisao") or "").strip().casefold()
        key = (str(d["indicador"]), str(d["serie"]), str(d["ano"]))
        label = " / ".join(key)
        if not decision:
            report["pendentes"] += 1
            continue
        if decision == "rejeitar":
            report["rejeitadas"].append(label)
            continue
        reviewer = str(d.get("conferido_por") or "").strip()
        if not reviewer:
            report["sem_nome"].append(label)
            continue
        row = index.get(key)
        if row is None or float(row["valor"]) != float(d["valor_csv"]):
            report["valor_mudou"].append(label)
            continue
        row["validada"] = "sim"
        report["aprovadas"].append(label)
        register.append({"quando": now, "conferido_por": reviewer, "indicador": key[0],
                         "serie": key[1], "ano": key[2], "valor": row["valor"],
                         "resultado_automatico": d.get("resultado") or "",
                         "observacao": d.get("observacao") or ""})

    with indicators_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    new_file = not register_file.is_file()
    with register_file.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REGISTER_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerows(register)
    return report


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    report = apply(read_decisions(Path(sys.argv[1])))
    print(f"Aprovadas: {len(report['aprovadas'])}; rejeitadas: {len(report['rejeitadas'])}; "
          f"sem decisão: {report['pendentes']}.")
    for key, message in (("sem_nome", "aprovadas sem 'conferido_por' (ignoradas)"),
                         ("valor_mudou", "valor diferente do CSV atual (ignoradas; gere a planilha de novo)"),
                         ("rejeitadas", "rejeitadas (continuam validada=nao)")):
        if report[key]:
            print(f"{message}:")
            for label in report[key]:
                print(f"  - {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
