"""Valida CSVs de indicadores e gera gráficos, tabelas e resumos por série."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
import re
import sys
import textwrap
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_COLUMNS = (
    "indicador",
    "serie",
    "ano",
    "valor",
    "unidade",
    "fonte",
    "url_fonte",
    "periodo_ref",
    "inicio_periodo",
    "fim_periodo",
    "tipo_dado",
    "data_acesso",
    "validada",
    "metodologia",
)
GOVERNMENT_COLUMNS = (
    "governo",
    "presidente",
    "condicao",
    "inicio",
    "fim",
    "fonte",
    "url_fonte",
    "data_acesso",
    "validada",
)
DATA_TYPES = ("observado", "revisado", "preliminar", "estimativa")
VALIDATED_VALUES = {"sim", "yes", "true"}
NOTE_MAX_LENGTH = 240
PLOT_PACKAGES = ("pandas", "matplotlib")

# Forma do marcador por tipo de dado: a distinção não depende de cor.
MARKERS = {
    "observado": {"marker": "o", "filled": True, "symbol": "●"},
    "revisado": {"marker": "s", "filled": True, "symbol": "■"},
    "preliminar": {"marker": "o", "filled": False, "symbol": "○"},
    "estimativa": {"marker": "^", "filled": False, "symbol": "△"},
}
POINT_COLOR = "#222222"
# Tons neutros alternados, sem associação partidária (ADR-004).
BAND_COLORS = ("#e6e6e6", "#f5f5f5")
CHANGE_MARK = "*"
PREVIEW_MARK = "PRÉVIA — DADOS NÃO CONFERIDOS — NÃO PUBLICAR"


class DataValidationError(ValueError):
    """Erro legível de estrutura ou conteúdo do CSV de indicadores."""


def check_environment() -> int:
    """Mostra se a instalação Python atual contém as dependências necessárias."""
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    missing = [
        package
        for package in PLOT_PACKAGES
        if importlib.util.find_spec(package) is None
    ]
    if missing:
        print(f"Dependências ausentes: {', '.join(missing)}")
        print("Instale-as com: python -m pip install -r requirements.txt")
        return 1
    print("Dependências de gráficos: OK")
    return 0


def _read_rows(path: Path, required: tuple[str, ...]):
    """Abre um CSV, confere o cabeçalho e devolve (número da linha, linha)."""
    if not path.is_file():
        raise DataValidationError(f"Arquivo não encontrado: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise DataValidationError(
                f"{path.name}: o CSV está vazio; inclua o cabeçalho esperado."
            )
        missing_columns = sorted(set(required) - set(reader.fieldnames))
        if missing_columns:
            raise DataValidationError(
                f"{path.name}: colunas obrigatórias ausentes: "
                + ", ".join(missing_columns)
            )
        for line_number, raw_row in enumerate(reader, start=2):
            if None in raw_row:
                raise DataValidationError(
                    f"{path.name}, linha {line_number}: há mais valores que "
                    "colunas no cabeçalho. Verifique vírgulas sem aspas."
                )
            yield line_number, {
                key: (value or "").strip() for key, value in raw_row.items()
            }


def _parse_date(value: str, where: str, column: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise DataValidationError(
            f"{where}: '{column}' deve ser uma data AAAA-MM-DD, recebido {value!r}."
        ) from error


def _check_url(value: str, where: str) -> None:
    parsed_url = urlparse(value)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise DataValidationError(f"{where}: url_fonte precisa ser uma URL http(s) válida.")


def _check_access_date(value: str, where: str, today: date) -> date:
    access_date = _parse_date(value, where, "data_acesso")
    if access_date > today:
        raise DataValidationError(f"{where}: data_acesso no futuro ({access_date}).")
    return access_date


def validate_csv(
    path: Path, today: date | None = None, allow_unvalidated: bool = False
) -> list[dict[str, object]]:
    """Lê e valida observações com fonte, período e método registrados.

    allow_unvalidated aceita linhas sem conferência editorial, só para prévia;
    todas as demais regras continuam valendo.
    """
    today = today or date.today()
    rows: list[dict[str, object]] = []
    seen_periods: set[tuple[str, str, int]] = set()
    group_units: dict[tuple[str, str], str] = {}
    group_intervals: dict[tuple[str, str], list[tuple[date, date, int]]] = {}

    for line_number, row in _read_rows(path, REQUIRED_COLUMNS):
        where = f"Linha {line_number}"
        for column in REQUIRED_COLUMNS:
            if not row[column]:
                raise DataValidationError(
                    f"{where}: a coluna '{column}' não pode ficar vazia."
                )

        validated = row["validada"].casefold() in VALIDATED_VALUES
        if not validated and not allow_unvalidated:
            raise DataValidationError(
                f"{where}: a observação não está validada. "
                "Só publique linhas revisadas e marcadas 'sim'."
            )

        try:
            year = int(row["ano"])
        except ValueError as error:
            raise DataValidationError(f"{where}: ano inválido: {row['ano']!r}.") from error
        if not 1900 <= year <= 2100:
            raise DataValidationError(f"{where}: ano fora do intervalo aceito: {year}.")

        try:
            value = float(row["valor"])
        except ValueError as error:
            raise DataValidationError(
                f"{where}: valor inválido: {row['valor']!r}. "
                "Use ponto como separador decimal."
            ) from error
        if not math.isfinite(value):
            raise DataValidationError(f"{where}: valor deve ser um número finito.")

        _check_url(row["url_fonte"], where)

        start = _parse_date(row["inicio_periodo"], where, "inicio_periodo")
        end = _parse_date(row["fim_periodo"], where, "fim_periodo")
        if start > end:
            raise DataValidationError(
                f"{where}: inicio_periodo ({start}) é posterior a fim_periodo ({end})."
            )

        data_type = row["tipo_dado"].casefold()
        if data_type not in DATA_TYPES:
            raise DataValidationError(
                f"{where}: tipo_dado {row['tipo_dado']!r} inválido. "
                f"Use um de: {', '.join(DATA_TYPES)}."
            )

        access_date = _check_access_date(row["data_acesso"], where, today)

        indicator = row["indicador"]
        series = row["serie"]
        period_key = (indicator, series, year)
        if period_key in seen_periods:
            raise DataValidationError(
                f"{where}: ano duplicado para '{indicator}' / '{series}' ({year})."
            )
        seen_periods.add(period_key)

        group_key = (indicator, series)
        if group_key in group_units and group_units[group_key] != row["unidade"]:
            raise DataValidationError(
                f"{where}: unidade inconsistente na série "
                f"'{indicator}' / '{series}'. Separe séries com unidades diferentes."
            )
        group_units[group_key] = row["unidade"]

        for other_start, other_end, other_line in group_intervals.get(group_key, []):
            if start <= other_end and other_start <= end:
                raise DataValidationError(
                    f"{where}: período {start}–{end} sobrepõe o da linha "
                    f"{other_line} na série '{indicator}' / '{series}'."
                )
        group_intervals.setdefault(group_key, []).append((start, end, line_number))

        rows.append(
            {
                "indicador": indicator,
                "serie": series,
                "ano": year,
                "valor": value,
                "unidade": row["unidade"],
                "fonte": row["fonte"],
                "url_fonte": row["url_fonte"],
                "periodo_ref": row["periodo_ref"],
                "inicio_periodo": start,
                "fim_periodo": end,
                "tipo_dado": data_type,
                "data_acesso": access_date,
                "validada": "sim" if validated else "nao",
                "metodologia": row["metodologia"],
            }
        )

    if not rows:
        raise DataValidationError(
            "Nenhuma observação encontrada. Preencha o CSV com dados reais "
            "e verifique a fonte antes de marcar 'validada=sim'."
        )
    return rows


def validate_governments(path: Path, today: date | None = None) -> list[dict[str, object]]:
    """Lê os períodos de exercício presidencial; exige datas conferidas e sem sobreposição."""
    today = today or date.today()
    governments: list[dict[str, object]] = []

    for line_number, row in _read_rows(path, GOVERNMENT_COLUMNS):
        where = f"{path.name}, linha {line_number}"
        for column in GOVERNMENT_COLUMNS:
            if column != "fim" and not row[column]:
                raise DataValidationError(
                    f"{where}: a coluna '{column}' não pode ficar vazia."
                )
        if row["validada"].casefold() not in VALIDATED_VALUES:
            raise DataValidationError(
                f"{where}: o período de '{row['governo']}' não está validado. "
                "Confira as datas na fonte oficial antes de marcar 'sim'."
            )
        _check_url(row["url_fonte"], where)
        _check_access_date(row["data_acesso"], where, today)
        start = _parse_date(row["inicio"], where, "inicio")
        end = _parse_date(row["fim"], where, "fim") if row["fim"] else None
        if end is not None and start > end:
            raise DataValidationError(f"{where}: inicio ({start}) é posterior a fim ({end}).")
        governments.append(
            {
                "governo": row["governo"],
                "presidente": row["presidente"],
                "inicio": start,
                "fim": end,
                "linha": line_number,
            }
        )

    if not governments:
        raise DataValidationError(f"{path.name}: nenhum governo cadastrado.")

    governments.sort(key=lambda government: government["inicio"])
    for previous, current in zip(governments, governments[1:]):
        if previous["fim"] is None:
            raise DataValidationError(
                f"{path.name}: só o governo mais recente pode ficar sem 'fim' "
                f"(linha {previous['linha']})."
            )
        if current["inicio"] <= previous["fim"]:
            raise DataValidationError(
                f"{path.name}: '{current['governo']}' começa antes do fim de "
                f"'{previous['governo']}'."
            )
    return governments


UNCOVERED_LABEL = "sem governo cadastrado"


def load_notes(path: Path) -> dict[str, str]:
    """Nota de contexto por indicador, lida do dicionário de dados.

    Liga a coluna 'indicador_csv' ao nome usado no CSV de observações; linhas
    sem esse vínculo são indicadores ainda não coletados e ficam de fora.
    """
    notes: dict[str, str] = {}
    for line_number, row in _read_rows(path, ("indicador_csv", "nota_grafico")):
        indicator = row["indicador_csv"]
        if not indicator:
            continue
        where = f"{path.name}, linha {line_number}"
        if not row["nota_grafico"]:
            raise DataValidationError(f"{where}: '{indicator}' está sem nota_grafico.")
        if len(row["nota_grafico"]) > NOTE_MAX_LENGTH:
            raise DataValidationError(
                f"{where}: nota_grafico com mais de {NOTE_MAX_LENGTH} caracteres."
            )
        if indicator in notes:
            raise DataValidationError(f"{where}: '{indicator}' aparece mais de uma vez.")
        notes[indicator] = row["nota_grafico"]
    return notes


def government_overlap(
    start: date, end: date, governments: list[dict[str, object]]
) -> tuple[list[tuple[dict[str, object], int]], int]:
    """Dias do período [start, end] em que cada governo esteve em exercício.

    Descreve coincidência temporal; não atribui o valor a nenhum governo.
    Devolve a lista (governo, dias) e os dias sem governo cadastrado.
    """
    overlaps: list[tuple[dict[str, object], int]] = []
    for government in governments:
        government_end = government["fim"] or date.max
        days = (min(end, government_end) - max(start, government["inicio"])).days + 1
        if days > 0:
            overlaps.append((government, days))
    total_days = (end - start).days + 1
    return overlaps, total_days - sum(days for _, days in overlaps)


def describe_overlap(
    start: date, end: date, governments: list[dict[str, object]]
) -> tuple[str, bool, bool]:
    """Texto com dias e percentual de cada governo, se há mais de um mandato
    no período (misto) e se há mais de uma pessoa na Presidência (troca)."""
    overlaps, uncovered = government_overlap(start, end, governments)
    total_days = (end - start).days + 1
    parts = [(str(government["governo"]), days) for government, days in overlaps]
    presidents = {str(government["presidente"]) for government, _ in overlaps}
    if uncovered:
        parts.append((UNCOVERED_LABEL, uncovered))
        presidents.add(UNCOVERED_LABEL)
    text = "; ".join(
        f"{name}: {days} de {total_days} dias ({round(100 * days / total_days)}%)"
        for name, days in parts
    )
    return text, len(parts) > 1, len(presidents) > 1


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    return slug or "serie"


def decimal_year(day: date) -> float:
    """Posição de uma data no eixo de anos (1º de janeiro = ano inteiro)."""
    year_start = date(day.year, 1, 1)
    year_length = (date(day.year + 1, 1, 1) - year_start).days
    return day.year + (day - year_start).days / year_length


def midpoint(start: date, end: date) -> date:
    return start + (end - start) / 2


def format_number(value: float) -> str:
    """Formata sem arredondar além do que o float guarda, com vírgula decimal."""
    text = repr(float(value))
    if text.endswith(".0"):
        text = text[:-2]
    return text.replace(".", ",")


def format_axis_number(value: float) -> str:
    """Rótulo de eixo no padrão brasileiro: ponto de milhar e vírgula decimal."""
    text = f"{value:,.2f}".rstrip("0").rstrip(".")
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def _unique(values) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values))


# Uma versão larga e outra para celular (RNF-01). Em 320 px de largura, a
# versão de celular mantém o texto em tamanho próximo ao do corpo da página.
LAYOUTS = {
    "": {"figsize": (9, 5.6), "font": 8, "title": 14, "wrap": 120,
         "title_wrap": 80, "point": 55, "nbins": 10, "mark_size": 16, "mark_wrap": 80,
         "plot_height": 4.4, "value_font": 8},
    "--celular": {"figsize": (4, 5.8), "font": 9, "title": 12, "wrap": 52,
                  "title_wrap": 34, "point": 40, "nbins": 5, "mark_size": 12,
                  "mark_wrap": 24, "plot_height": 4.2, "value_font": 7},
}
LABEL_ROWS = 3
# Faixas mais curtas que isto (a interinidade de Temer) ficam sem rótulo; o
# governo continua identificado na tabela e no resumo.
MIN_LABELED_YEARS = 0.5


def _draw_government_bands(axis, governments, x_min, x_max, layout) -> int:
    """Desenha as faixas e os rótulos; devolve quantas linhas de rótulo usou."""
    from matplotlib.transforms import blended_transform_factory

    label_transform = blended_transform_factory(axis.transData, axis.transAxes)
    # Largura aproximada da área do gráfico, para evitar rótulos sobrepostos.
    inches_per_year = 0.8 * layout["figsize"][0] / (x_max - x_min)
    gap = layout["font"] * 0.5 / 72
    row_ends: list[float] = []
    for index, government in enumerate(governments):
        start = decimal_year(government["inicio"])
        end = (
            decimal_year(government["fim"]) + 1 / 365
            if government["fim"] is not None
            else x_max
        )
        start, end = max(start, x_min), min(end, x_max)
        if end <= start:
            continue
        axis.axvspan(
            start, end, color=BAND_COLORS[index % len(BAND_COLORS)], zorder=0, lw=0
        )
        axis.axvline(start, color="#8a8a8a", lw=0.8, ls=(0, (3, 3)), zorder=1)
        if end - start < MIN_LABELED_YEARS:
            continue

        # Cada rótulo vai para a primeira linha em que não encosta no anterior.
        label = str(government["governo"])
        half_width = len(label) * layout["font"] * 0.55 / 72 / 2
        center = (start + end) / 2
        left = (center - x_min) * inches_per_year - half_width
        for row in range(LABEL_ROWS):
            if row == len(row_ends) or left >= row_ends[row] + gap:
                if row == len(row_ends):
                    row_ends.append(0.0)
                row_ends[row] = left + 2 * half_width
                axis.text(
                    center,
                    1.01 + 0.045 * row,
                    label,
                    transform=label_transform,
                    ha="center",
                    va="bottom",
                    fontsize=layout["font"],
                    color="#333333",
                )
                break
        else:
            raise RuntimeError(
                f"Sem espaço para o rótulo de '{label}'; ajuste o layout do gráfico."
            )
    return len(row_ends)


def _plot_series(
    group, governments, layout, image_path: Path, note: str | None, preview: bool = False
) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    indicator, series = group["indicador"].iloc[0], group["serie"].iloc[0]
    x_values = [
        decimal_year(midpoint(start, end))
        for start, end in zip(group["inicio_periodo"], group["fim_periodo"])
    ]
    x_min = decimal_year(group["inicio_periodo"].min()) - 0.25
    x_max = decimal_year(group["fim_periodo"].max()) + 0.25

    figure, axis = plt.subplots(figsize=layout["figsize"])
    label_rows = (
        _draw_government_bands(axis, governments, x_min, x_max, layout) if governments else 0
    )

    present_types = []
    for data_type in DATA_TYPES:
        mask = (group["tipo_dado"] == data_type).to_numpy()
        if not mask.any():
            continue
        style = MARKERS[data_type]
        axis.scatter(
            [x for x, keep in zip(x_values, mask) if keep],
            group.loc[mask, "valor"],
            s=layout["point"],
            marker=style["marker"],
            facecolors=POINT_COLOR if style["filled"] else "white",
            edgecolors=POINT_COLOR,
            linewidths=1.4,
            zorder=3,
        )
        present_types.append(data_type)

    has_change = governments is not None and (group["troca_de_presidente"] == "sim").any()
    if has_change:
        for x, value, change in zip(x_values, group["valor"], group["troca_de_presidente"]):
            if change == "sim":
                axis.annotate(
                    CHANGE_MARK,
                    (x, value),
                    xytext=(0, 7),
                    textcoords="offset points",
                    ha="center",
                    fontsize=layout["font"] + 4,
                    color=POINT_COLOR,
                    zorder=4,
                )

    title = textwrap.fill(f"{indicator} — {series}", layout["title_wrap"])
    axis.set_title(
        title, loc="left", fontsize=layout["title"], pad=8 + label_rows * (layout["font"] + 5)
    )
    axis.set_xlabel("Ano (pontos no meio do período de referência)", fontsize=layout["font"])
    axis.set_ylabel(str(group["unidade"].iloc[0]), fontsize=layout["font"])
    axis.tick_params(labelsize=layout["font"])
    axis.set_xlim(x_min, x_max)
    axis.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=layout["nbins"]))
    _format_value_axis(axis, group["valor"], headroom=0.06)
    footer = _source_lines(group, note, preview)
    # Legenda no rodapé, e não sobre o gráfico, para nunca cobrir pontos.
    if len(present_types) > 1:
        footer.append(
            "Marcadores: "
            + "; ".join(f"{MARKERS[kind]['symbol']} {kind}" for kind in present_types)
            + "."
        )
    if governments:
        footer.append(
            "Faixas cinza: períodos de exercício presidencial, apenas contexto "
            "temporal; não indicam causa."
        )
    if has_change:
        footer.append(f"{CHANGE_MARK} Período de referência com troca de presidente.")
    _finish_figure(figure, footer, layout, preview, image_path)


def _format_value_axis(axis, values, headroom: float) -> None:
    """Regra única para todas as séries (ADR-009): o zero fica sempre visível,
    para não ampliar visualmente as variações; com valores negativos, uma
    linha de referência marca o zero. A folga evita cortar rótulos e marcas."""
    from matplotlib.ticker import FuncFormatter

    if values.min() >= 0:
        axis.set_ylim(bottom=0)
    elif values.max() <= 0:
        axis.set_ylim(top=0)
    if values.min() < 0:
        axis.axhline(0, color=POINT_COLOR, lw=1, zorder=2)
    bottom, top = axis.get_ylim()
    span = top - bottom
    axis.set_ylim(
        bottom - (headroom * span if values.min() < 0 else 0),
        top + (headroom * span if values.max() > 0 else 0),
    )
    axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: format_axis_number(value)))
    axis.grid(axis="y", alpha=0.3, zorder=1)
    axis.spines[["top", "right"]].set_visible(False)


def _source_lines(group, note: str | None, preview: bool) -> list[str]:
    first_period, last_period = group["periodo_ref"].iloc[0], group["periodo_ref"].iloc[-1]
    return [
        f"Fonte: {'; '.join(_unique(group['fonte']))}. Períodos: {first_period} a "
        f"{last_period}. Acesso: {', '.join(_unique(group['data_acesso']))}.",
        *([f"Atenção: {note}"] if note else []),
        "Lacunas não são interpoladas; cálculos próprios estão descritos na "
        f"metodologia. URLs e valores: {_table_name(preview)} e resumos.md.",
    ]


def _finish_figure(figure, footer: list[str], layout, preview: bool, image_path: Path) -> None:
    import matplotlib.pyplot as plt

    wrapped = "\n".join(textwrap.fill(line, layout["wrap"]) for line in footer)
    footer_height = (wrapped.count("\n") + 1) * layout["font"] * 1.3 / 72 + 0.15
    # A figura cresce com o rodapé, para o gráfico nunca ser espremido.
    total_height = layout["plot_height"] + footer_height
    figure.set_size_inches(layout["figsize"][0], total_height)
    figure.text(0.01, 0.01, wrapped, ha="left", va="bottom", fontsize=layout["font"])
    figure.tight_layout(rect=(0, footer_height / total_height, 1, 1))
    if preview:
        figure.text(
            0.5, 0.55, textwrap.fill(PREVIEW_MARK, layout["mark_wrap"]),
            ha="center", va="center", rotation=25, fontsize=layout["mark_size"],
            color="#555555", alpha=0.35, weight="bold", zorder=10,
        )
    figure.savefig(image_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


# Recorte principal (ADR-013): últimos mandatos de cada grupo político.
FOCUS_GOVERNMENTS = ("Bolsonaro", "Lula III")
# Uma cor por governo do recorte, na ordem de --recorte (ADR-004): roxo e
# laranja-queimado, sem associação partidária, contraste ≥ 5:1 com o branco e
# distinguíveis nos tipos comuns de daltonismo. A identificação também vem do
# nome acima das barras; preliminar e período misto usam hachura.
FOCUS_COLORS = ("#6A3D9A", "#B4510B")
MIXED_EDGE = "#4a4a4a"


def _lighten(color: str, amount: float = 0.55) -> str:
    """Mistura a cor com branco (para dado preliminar)."""
    rgb = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(c + (255 - c) * amount):02x}" for c in rgb)


def focus_rows(group, governments, focus_names) -> list[tuple[int, str | None]]:
    """Posições das observações cujo período toca algum governo do recorte.

    Devolve (posição na série, governo) — governo é None quando o período
    tem dias de mais de um governo, e então não é atribuído a nenhum.
    """
    focus = [g for g in governments if g["governo"] in focus_names]
    selected = []
    for position, (start, end) in enumerate(zip(group["inicio_periodo"], group["fim_periodo"])):
        if not government_overlap(start, end, focus)[0]:
            continue
        overlaps, uncovered = government_overlap(start, end, governments)
        single = len(overlaps) == 1 and not uncovered
        selected.append((position, str(overlaps[0][0]["governo"]) if single else None))
    return selected


def _plot_focus(group, governments, focus_names, layout, image_path, note, preview) -> None:
    import matplotlib.pyplot as plt

    selected = focus_rows(group, governments, focus_names)
    rows = group.iloc[[position for position, _ in selected]]
    owners = [owner for _, owner in selected]
    values = rows["valor"].astype(float)
    preliminary = (rows["tipo_dado"] != "observado").to_numpy()

    colors = {name: FOCUS_COLORS[i % len(FOCUS_COLORS)] for i, name in enumerate(focus_names)}
    figure, axis = plt.subplots(figsize=layout["figsize"])
    positions = list(range(len(rows)))
    for x, value, owner, is_prelim in zip(positions, values, owners, preliminary):
        if owner is None:
            fill, edge, hatch = "white", MIXED_EDGE, "///"
        elif is_prelim:
            fill, edge, hatch = _lighten(colors[owner]), colors[owner], ".."
        else:
            fill, edge, hatch = colors[owner], colors[owner], None
        axis.bar(
            x, value, width=0.7, color=fill, hatch=hatch,
            edgecolor=edge, linewidth=1, zorder=3,
        )
    _format_value_axis(axis, values, headroom=0.14)

    # Valor escrito em cada barra: a leitura não depende da escala.
    offset = 0.015 * (axis.get_ylim()[1] - axis.get_ylim()[0])
    for x, value, owner in zip(positions, values, owners):
        label = format_axis_number(value) + (CHANGE_MARK if owner is None else "")
        axis.text(
            x, value + (offset if value >= 0 else -offset), label,
            ha="center", va="bottom" if value >= 0 else "top",
            fontsize=layout["value_font"], color="#222222", zorder=4,
        )

    # Separadores e nomes dos governos acima das barras de cada um.
    from matplotlib.transforms import blended_transform_factory

    label_transform = blended_transform_factory(axis.transData, axis.transAxes)
    by_name = {str(g["governo"]): g for g in governments}
    for name in focus_names:
        indexes = [x for x, owner in zip(positions, owners) if owner == name]
        if not indexes:
            continue
        government = by_name[name]
        end = government["fim"].year if government["fim"] else None
        period = f"{government['inicio'].year}–{end}" if end else f"desde {government['inicio'].year}"
        axis.text(
            (indexes[0] + indexes[-1]) / 2, 1.02, f"{name}\n({period})",
            transform=label_transform, ha="center", va="bottom",
            fontsize=layout["font"] + 1, color=colors[name], weight="bold",
        )
    for x in range(1, len(owners)):
        if owners[x] != owners[x - 1]:
            axis.axvline(x - 0.5, color="#8a8a8a", lw=0.8, ls=(0, (3, 3)), zorder=1)

    axis.set_xticks(positions)
    axis.set_xticklabels([str(year) for year in rows["ano"]], fontsize=layout["font"])
    axis.tick_params(axis="y", labelsize=layout["font"])
    axis.set_ylabel(str(group["unidade"].iloc[0]), fontsize=layout["font"])
    axis.set_xlabel("Ano de referência da fonte", fontsize=layout["font"])
    title = textwrap.fill(
        f"{group['indicador'].iloc[0]} — {group['serie'].iloc[0]}", layout["title_wrap"]
    )
    axis.set_title(title, loc="left", fontsize=layout["title"], pad=8 + 2 * (layout["font"] + 5))

    footer = _source_lines(rows, note, preview)
    legend = ["cor cheia: período inteiro no governo indicado acima"]
    if preliminary.any():
        legend.append("cor clara pontilhada: dado preliminar")
    if None in owners:
        legend.append(
            f"branco hachurado e {CHANGE_MARK}: período com dois governos, não atribuído"
        )
    if len(legend) > 1:
        footer.append("Barras — " + "; ".join(legend) + ".")
    for name in focus_names:
        government = by_name[name]
        if government["fim"] is None:
            footer.append(
                f"{name}: mandato em curso; último dado disponível: "
                f"{rows['periodo_ref'].iloc[-1]}."
            )
    footer.append(
        "Governos indicados apenas como contexto temporal; não indicam causa. "
        f"Série completa desde {group['ano'].iloc[0]}: gráfico histórico."
    )
    _finish_figure(figure, footer, layout, preview, image_path)


def _table_name(preview: bool) -> str:
    return "dados_previa.csv" if preview else "dados_validados.csv"


def create_outputs(
    rows: list[dict[str, object]],
    output_dir: Path,
    governments: list[dict[str, object]] | None = None,
    notes: dict[str, str] | None = None,
    preview: bool = False,
    focus: tuple[str, ...] = FOCUS_GOVERNMENTS,
) -> list[Path]:
    """Gera CSV acessível, resumos em texto e PNGs (largo e celular) por série.

    Com notes, toda série precisa de nota de contexto (regra de ouro 4).
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import pandas as pd
    except ImportError as error:
        raise RuntimeError(
            "Faltam dependências para gráficos. Execute "
            "'python -m pip install -r requirements.txt'."
        ) from error

    if notes is not None:
        missing = sorted({str(row["indicador"]) for row in rows} - set(notes))
        if missing:
            raise DataValidationError(
                "Sem nota de contexto no dicionário (indicador_csv/nota_grafico): "
                + "; ".join(missing)
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows).sort_values(["indicador", "serie", "inicio_periodo"])
    if governments:
        descriptions = [
            describe_overlap(start, end, governments)
            for start, end in zip(frame["inicio_periodo"], frame["fim_periodo"])
        ]
        frame["governos_no_periodo"] = [text for text, _, _ in descriptions]
        frame["periodo_misto"] = ["sim" if mixed else "não" for _, mixed, _ in descriptions]
        frame["troca_de_presidente"] = [
            "sim" if change else "não" for _, _, change in descriptions
        ]

    table_path = output_dir / _table_name(preview)
    frame.to_csv(table_path, index=False, encoding="utf-8-sig")
    generated = [table_path]
    summaries: list[str] = [
        "# Resumos das séries",
        "",
        *([f"**{PREVIEW_MARK}.** Inclui linhas com validada=nao.", ""] if preview else []),
        "Resumos descritivos gerados a partir de dados validados. Não indicam "
        "causa: as faixas e colunas de governo mostram apenas quem estava em "
        "exercício durante o período de referência de cada observação.",
    ]

    for (indicator, series), group in frame.groupby(["indicador", "serie"], sort=True):
        group = group.sort_values("inicio_periodo")
        slug = f"{slugify(str(indicator))}--{slugify(str(series))}"
        note = notes.get(str(indicator)) if notes else None
        image_names = []
        # Com governos, o gráfico principal é o recorte e o histórico completo
        # fica em arquivo próprio; sem governos, só existe o histórico.
        has_focus = bool(governments) and bool(focus_rows(group, governments, focus))
        history_prefix = f"{slug}--historico" if has_focus else slug
        for suffix, layout in LAYOUTS.items():
            history_path = output_dir / f"{history_prefix}{suffix}.png"
            _plot_series(group, governments, layout, history_path, note, preview)
            if has_focus:
                focus_path = output_dir / f"{slug}{suffix}.png"
                _plot_focus(group, governments, focus, layout, focus_path, note, preview)
                generated.append(focus_path)
                image_names.append(focus_path.name)
            generated.append(history_path)
            image_names.append(history_path.name)

        summaries.extend(_summary_section(indicator, series, group, image_names, note))

    summary_path = output_dir / "resumos.md"
    summary_path.write_text("\n".join(summaries) + "\n", encoding="utf-8")
    generated.append(summary_path)
    return generated


def _summary_section(
    indicator, series, group, image_names: list[str], note: str | None = None
) -> list[str]:
    """Resumo neutro e tabela equivalente ao gráfico (RF-03)."""

    def describe(row) -> str:
        return f"{format_number(row['valor'])} ({row['periodo_ref']})"

    by_value = group.sort_values("valor", kind="stable")
    years = sorted(int(year) for year in group["ano"])
    missing_years = sorted(set(range(years[0], years[-1] + 1)) - set(years))
    has_governments = "governos_no_periodo" in group
    type_counts = group["tipo_dado"].value_counts()

    lines = [
        "",
        f"## {indicator} — {series}",
        "",
        "Gráficos: " + ", ".join(f"`{name}`" for name in image_names),
        "",
        f"- Unidade: {group['unidade'].iloc[0]}",
        *([f"- Atenção: {note}"] if note else []),
        f"- Observações: {len(group)}, de {group['periodo_ref'].iloc[0]} "
        f"a {group['periodo_ref'].iloc[-1]}",
        "- Fontes: "
        + "; ".join(
            f"{source} ({url})"
            for source, url in dict.fromkeys(zip(group["fonte"], group["url_fonte"]))
        ),
        f"- Data de acesso: {', '.join(_unique(group['data_acesso']))}",
        f"- Primeiro valor: {describe(group.iloc[0])}; último valor: "
        f"{describe(group.iloc[-1])}",
        f"- Menor valor: {describe(by_value.iloc[0])}; maior valor: "
        f"{describe(by_value.iloc[-1])}",
        "- Tipos de dado: "
        + ", ".join(f"{data_type} ({count})" for data_type, count in type_counts.items()),
        "- Anos-rótulo sem observação entre o primeiro e o último: "
        + (", ".join(str(year) for year in missing_years) if missing_years else "nenhum"),
    ]
    if has_governments:
        for column, label in (
            ("troca_de_presidente", "Períodos com troca de presidente"),
            ("periodo_misto", "Períodos com mais de um mandato (inclui reeleição e interinidade)"),
        ):
            periods = group[group[column] == "sim"]["periodo_ref"].tolist()
            lines.append(f"- {label}: " + (", ".join(periods) if periods else "nenhum"))

    header = "| Ano | Período de referência | Valor | Tipo |"
    separator = "|---|---|---|---|"
    if has_governments:
        header += " Governos em exercício no período |"
        separator += "---|"
    lines += ["", header, separator]
    for _, row in group.iterrows():
        line = (
            f"| {row['ano']} | {row['periodo_ref']} | {format_number(row['valor'])} "
            f"| {row['tipo_dado']} |"
        )
        if has_governments:
            line += f" {row['governos_no_periodo']} |"
        lines.append(line)
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Valida uma tabela CSV documentada e gera gráficos, tabela e "
            "resumos separados por indicador/série."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("dados/indicadores.csv"),
        help="Caminho do CSV preenchido (padrão: dados/indicadores.csv).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("saida"),
        help="Pasta de saída para gráficos, tabela e resumos (padrão: saida).",
    )
    parser.add_argument(
        "--governos",
        type=Path,
        default=Path("dados/governos.csv"),
        help="CSV de períodos presidenciais (padrão: dados/governos.csv).",
    )
    parser.add_argument(
        "--sem-governos",
        action="store_true",
        help="Gera os gráficos sem faixas e colunas de governo.",
    )
    parser.add_argument(
        "--dicionario",
        type=Path,
        default=Path("dados/dicionario_indicadores.csv"),
        help="Dicionário com a nota de contexto de cada indicador.",
    )
    parser.add_argument(
        "--sem-notas",
        action="store_true",
        help="Gera sem notas de contexto (só para testes; não publicar).",
    )
    parser.add_argument(
        "--recorte",
        default=",".join(FOCUS_GOVERNMENTS),
        help="Governos do gráfico principal, separados por vírgula "
        f"(padrão: {','.join(FOCUS_GOVERNMENTS)}).",
    )
    parser.add_argument(
        "--previa",
        action="store_true",
        help=(
            "Aceita linhas não conferidas e grava em 'previa/', com marca "
            "d'água de não publicação. Nunca grava em 'saida/'."
        ),
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Verifica Python e dependências sem abrir um conjunto de dados.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check_env:
        return check_environment()

    if args.previa:
        if args.output == Path("saida"):
            args.output = Path("previa")
        elif args.output.resolve() == Path("saida").resolve():
            print("Erro: a prévia não pode ser gravada em 'saida/'.", file=sys.stderr)
            return 1

    try:
        governments = None if args.sem_governos else validate_governments(args.governos)
        notes = None if args.sem_notas else load_notes(args.dicionario)
        focus = tuple(name.strip() for name in args.recorte.split(",") if name.strip())
        if governments:
            unknown = set(focus) - {str(g["governo"]) for g in governments}
            if unknown:
                raise DataValidationError(
                    "Governo do recorte ausente em governos.csv: " + ", ".join(sorted(unknown))
                )
        rows = validate_csv(args.input, allow_unvalidated=args.previa)
        generated = create_outputs(rows, args.output, governments, notes, args.previa, focus)
    except (DataValidationError, RuntimeError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    if args.previa:
        pending = sum(row["validada"] != "sim" for row in rows)
        print(f"PRÉVIA: {len(rows)} observações, {pending} ainda não conferidas. Não publicar.")
    else:
        print(f"Validadas {len(rows)} observações.")
    print(f"Arquivos gerados em: {args.output.resolve()}")
    for path in generated:
        print(f"- {path}")
    print(
        "Nota: gráficos mostram evolução temporal; não demonstram causalidade "
        "nem atribuem resultados exclusivamente a um governo."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
