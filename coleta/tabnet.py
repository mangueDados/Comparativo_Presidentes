"""Consulta ao TabNet do SIM/DATASUS (óbitos por causas externas, por residência)."""

from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request

TABNET_URL = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sim/cnv/ext10uf.def"
TABNET_FORM = "http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sim/cnv/ext10uf.def"
# Códigos do formulário: grande grupo CID-10 e sexo.
GROUPS = {"4": ("X85", "agressoes"), "5": ("Y10", "indeterminada"), "6": ("Y35", "intervencao")}
SEX_CODES = {"todos": "TODAS_AS_CATEGORIAS__", "feminino": "2"}
FILTER_FIELDS = (
    "SRegião", "SUnidade_da_Federação", "SGrupo_CID10", "SCategoria_CID10",
    "SFaixa_Etária", "SFaixa_Etária_OPS", "SFaixa_Etária_det", "SFx.Etária_Menor_1A",
    "SCor/raça", "SEscolaridade", "SEstado_civil", "SLocal_ocorrência", "SAcid._Trabalho",
)


def form_data(first_year: int, last_year: int, sex: str = "todos") -> bytes:
    pairs = [("Linha", "Grande_Grupo_CID10"), ("Coluna", "Ano_do_Óbito"),
             ("Incremento", "Óbitos_p/Residênc")]
    pairs += [("Arquivos", f"extuf{year % 100:02d}.dbf") for year in range(first_year, last_year + 1)]
    pairs += [(field, "TODAS_AS_CATEGORIAS__") for field in FILTER_FIELDS]
    pairs.append(("SSexo", SEX_CODES[sex]))
    pairs += [("SGrande_Grupo_CID10", code) for code in GROUPS]
    pairs += [("formato", "prn"), ("mostre", "Mostra")]
    return urllib.parse.urlencode(pairs, encoding="latin-1").encode()


def fetch(first_year: int, last_year: int, sex: str = "todos") -> str:
    request = urllib.request.Request(
        TABNET_URL, data=form_data(first_year, last_year, sex),
        headers={"User-Agent": "Mozilla/5.0 (comparativo Mangue)"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read().decode("latin-1")


def parse(body: str) -> dict[str, dict[int, int]]:
    """Lê a saída 'prn': grupo de causa → {ano: óbitos}. Ignora a coluna Total."""
    match = re.search(r"<PRE>(.*?)</PRE>", body, re.S | re.I)
    if not match:
        raise ValueError("TabNet não devolveu tabela.")
    lines = [line for line in html.unescape(match.group(1)).splitlines() if line.startswith('"')]
    header = [cell.strip('"') for cell in lines[0].split(";")]
    years = [int(cell) for cell in header[1:] if cell.isdigit()]
    groups = {}
    for line in lines[1:]:
        cells = [cell.strip('"') for cell in line.split(";")]
        for prefix, key in GROUPS.values():
            if cells[0].startswith(prefix):
                groups[key] = {year: int(value) for year, value in zip(years, cells[1:])}
    return groups
