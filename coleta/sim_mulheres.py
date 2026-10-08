"""Homicídios de mulheres a partir do SIM/DATASUS (TabNet), com a mesma
definição do Atlas da Violência: agressões (X85-Y09) e intervenções legais
(Y35-Y36), por residência, sexo feminino.

Uso, a partir da raiz do projeto:
    python coleta/sim_mulheres.py           # consulta o TabNet e salva o bruto
    python coleta/sim_mulheres.py --offline # usa o bruto já salvo
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from coleta import tabnet
    from coleta.comum import INDICATORS_FILE, ROOT, merge_into
except ModuleNotFoundError:  # execução direta: python coleta/sim_mulheres.py
    import tabnet
    from comum import INDICATORS_FILE, ROOT, merge_into

RAW_FILE = ROOT / "dados" / "brutos" / "datasus_tabnet_sim_mulheres_acesso-2026-10-07.html"
ACCESS_DATE = "2026-10-07"
FIRST_YEAR = 2002  # base, ADR-009
# Último ano com SIM consolidado (o mesmo publicado pelo Atlas 2026).
LAST_YEAR = 2024

INDICATOR = "Homicídios de mulheres"
SERIES = "Brasil"


def to_rows(groups: dict[str, dict[int, int]]) -> list[dict[str, str]]:
    rows = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        total = groups["agressoes"][year] + groups["intervencao"][year]
        rows.append({
            "indicador": INDICATOR,
            "serie": SERIES,
            "ano": str(year),
            "valor": str(total),
            "unidade": "óbitos",
            "fonte": "Ministério da Saúde, SIM (TabNet/DATASUS)",
            "url_fonte": tabnet.TABNET_FORM,
            "periodo_ref": f"jan–dez/{year}",
            "inicio_periodo": f"{year}-01-01",
            "fim_periodo": f"{year}-12-31",
            "tipo_dado": "observado",
            "data_acesso": ACCESS_DATE,
            "validada": "nao",
            "metodologia": (
                "Óbitos de mulheres por agressão (CID-10 X85-Y09) e intervenção legal "
                "(Y35-Y36), por residência; mesma definição de homicídio do Atlas da "
                "Violência. Inclui todos os homicídios de mulheres, não só feminicídios. "
                "Transformação em coleta/sim_mulheres.py."
            ),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=INDICATORS_FILE)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    if not args.offline:
        RAW_FILE.write_text(tabnet.fetch(FIRST_YEAR, LAST_YEAR, sex="feminino"), encoding="utf-8")
    rows = to_rows(tabnet.parse(RAW_FILE.read_text(encoding="utf-8")))
    merge_into(args.output, INDICATOR, SERIES, rows)
    print(f"{len(rows)} anos de '{INDICATOR}' ({FIRST_YEAR}–{LAST_YEAR}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
