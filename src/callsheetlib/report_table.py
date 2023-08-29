# ----------------------
# ----- DEPRECATED -----
# ----------------------

from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, KeepTogether

if TYPE_CHECKING:
    from reportlab.platypus import Flowable
    from .sorting import RoomGroup, DataRow

# Divde by 255 to get a value between 0 and 1
CELL_COLOR = colors.Color(198 / 255, 217 / 255, 240 / 255, 1)  # type: ignore (reportlab bug)
HEADER_COLOR = colors.lightgrey

PAGE_SIZE = landscape(letter)
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
FONT_SIZE = 10

COLUMN_WIDTHS = [
    PAGE_WIDTH * 0.065,
    PAGE_WIDTH * 0.06,
    PAGE_WIDTH * 0.06,
    PAGE_WIDTH * 0.13,
    PAGE_WIDTH * 0.22,
    PAGE_WIDTH * 0.20,
    PAGE_WIDTH * 0.06,
    PAGE_WIDTH * 0.14
]

TABLE_WIDTH = sum(COLUMN_WIDTHS)
TABLE_SPACING = 20

PARA_PAGEHEADER_STYLE = ParagraphStyle(
    'PageHeader',
    fontSize=24,
    leading=24 * 1.2,
    alignment=0
)

PARA_PAGEDATE_STYLE = ParagraphStyle(
    'PageDate',
    fontSize=24,
    leading=24 * 1.2,
    alignment=2
)

PARA_LABEL_STYLE = ParagraphStyle(
    'GroupLabel',
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=18 * 1.2,
    alignment=0
)

PARA_CELL_STYLE = ParagraphStyle(
    "Cell",
    fontSize=FONT_SIZE,
    leading=FONT_SIZE * 1.2,
    alignment=1
)

PARA_CELL_ACTOR_STYLE = ParagraphStyle(
    "ActorCell",
    fontSize=FONT_SIZE,
    leading=FONT_SIZE * 1.2,
    alignment=1,
    textColor=colors.red
)

TABLE_PAGEHEADER_STYLE = TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
])

TABLE_COLUMNHEADER_STYLE = TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ("BACKGROUND", (0, 0), (-1, 0), HEADER_COLOR),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
])

TABLE_CELL_STYLE = TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("BACKGROUND", (0, 0), (-1, -1), CELL_COLOR),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
])

def _create_paragraph(text: str, style: ParagraphStyle=PARA_CELL_STYLE) -> Paragraph:
    if not text:
        return Paragraph("", style)
    return Paragraph(text, style)

def _create_data(data_rows: list["DataRow"]) -> list[list[str | Paragraph]]:
    trx_rows: list[list[str | Paragraph]] = []
    for row in data_rows:
        if row.is_actor:
            trx_rows.append([_create_paragraph(item, PARA_CELL_ACTOR_STYLE) for item in row.data])
        else:
            trx_rows.append([_create_paragraph(item, PARA_CELL_STYLE) for item in row.data])
    return trx_rows

def _create_table(data: list[list[str | Paragraph]], style: TableStyle, colWidths: list[float]=COLUMN_WIDTHS) -> Table:
    table = Table(data, colWidths=colWidths)
    table.setStyle(style)
    return table

def _verify_uniform_headers(groups: list["RoomGroup"]) -> list[str]:
    headers = groups[0].table_headers
    for group in groups:
        if group.table_headers != headers:
            raise ValueError("All groups must have the same headers")
    return headers

def _group_tables(groups: list["RoomGroup"]) -> list["Flowable"]:
    flowables: list["Flowable"] = []
    if not groups:
        return flowables
    headers = _verify_uniform_headers(groups)
    for group in groups:
        data = _create_data(group.table_data())
        room_table = _create_table(data, TABLE_CELL_STYLE)
        group_para = _create_paragraph(group.room_trx.name, PARA_LABEL_STYLE)
        group_header_table = _create_table([[group_para]], TABLE_PAGEHEADER_STYLE, [PAGE_WIDTH * 0.9])
        header_table = _create_table([[_create_paragraph(header) for header in headers]], TABLE_COLUMNHEADER_STYLE)
        spacer = Spacer(0, TABLE_SPACING)
        flowables.append(KeepTogether([group_header_table, header_table, room_table, spacer]))
    return flowables

def _header_date(daterange: tuple[str, str]=...) -> str:
    if daterange is ...:
        return datetime.now().strftime('%m/%d/%Y')
    if daterange[0] == daterange[1]:
        return datetime.strptime(daterange[0], '%Y-%m-%d').strftime('%m/%d/%Y')
    start = datetime.strptime(daterange[0], '%Y-%m-%d').strftime('%m/%d/%Y')
    end = datetime.strptime(daterange[1], '%Y-%m-%d').strftime('%m/%d/%Y')
    return f"{start} - {end}"

def _report_header(pageheader: str, daterange: tuple[str, str]=...) -> Table:
    callsheet = _create_paragraph(pageheader, PARA_PAGEHEADER_STYLE)
    datestr = _header_date(daterange)
    datepara = _create_paragraph(datestr, PARA_PAGEDATE_STYLE)
    return _create_table([[callsheet, datepara]], TABLE_PAGEHEADER_STYLE, [PAGE_WIDTH * 0.46, PAGE_WIDTH * 0.46])

def create_pdf(groups: list["RoomGroup"], outputpath: Path, daterange: tuple[str, str]=..., debug: bool=False) -> None:
    doc = SimpleDocTemplate(str(outputpath), pagesize=PAGE_SIZE, topMargin=20, bottomMargin=20)
    if debug:
        first_group = groups[0]
        tables = _group_tables(groups=[first_group])
    tables = _group_tables(groups)
    report_header = _report_header("Call Sheet Report", daterange=daterange)
    header_padding = Spacer(0, 30)
    doc.build([report_header, header_padding, *tables])