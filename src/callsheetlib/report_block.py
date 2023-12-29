from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, KeepTogether

from . import ReportEnum

if TYPE_CHECKING:
    from reportlab.platypus import Flowable
    from .sorting import WorkOrderBlock, TopLevelBlock

# Divde by 255 to get a value between 0 and 1
# CELL_COLOR = colors.Color(198 / 255, 217 / 255, 240 / 255, 1)  # type: ignore (reportlab bug)
CELL_COLOR = (239, 245, 255)
CELL_COLOR = colors.Color(*(color/255 for color in CELL_COLOR))  # type: ignore (reportlab bug)
HEADER_COLOR = colors.lightgrey

PAGE_SIZE = landscape(letter)
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
TOP_MARGIN = 20
BOTTOM_MARGIN = 20
FONT_SIZE = 10

COLUMN_WIDTHS = [
    PAGE_WIDTH * 0.34,
    PAGE_WIDTH * 0.145,
    PAGE_WIDTH * 0.08,
    PAGE_WIDTH * 0.39,
]

TABLE_WIDTH = sum(COLUMN_WIDTHS)
TABLE_SPACING = 20

PARA_PAGEHEADER_STYLE = ParagraphStyle(
    'PageHeader',
    fontSize=24,
    leading=24 * 1.2,
    alignment=1
)

PARA_PAGEDATE_STYLE = ParagraphStyle(
    'PageDate',
    fontSize=24,
    leading=24 * 1.2,
    alignment=0
)

PARA_LABEL_STYLE = ParagraphStyle(
    'GroupLabel',
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=18 * 1.2,
    alignment=0
)

PARA_BLOCKHEADER_STYLE = ParagraphStyle(
    "BlockHeader",
    fontName="Helvetica-Bold",
    fontSize=FONT_SIZE + 1,
    leading=(FONT_SIZE + 1) * 1.2,
    alignment=0
)

PARA_ITEM_STYLE = ParagraphStyle(
    "Cell",
    fontSize=FONT_SIZE,
    leading=FONT_SIZE * 1.2,
    alignment=0
)

PARA_PHASE_STYLE = ParagraphStyle(
    "PhaseCell",
    fontName="Helvetica-Oblique",
    fontSize=FONT_SIZE,
    leading=FONT_SIZE * 1.2,
    alignment=0,
    textColor=colors.blue
)

PARA_ACTOR_STYLE = ParagraphStyle(
    "ActorCell",
    fontSize=FONT_SIZE,
    leading=FONT_SIZE * 1.2,
    alignment=0,
    textColor=colors.red
)

TABLE_PAGEHEADER_STYLE = TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
])

TABLE_BLOCKHEADER_STYLE = TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ("BACKGROUND", (0, 0), (-1, 0), HEADER_COLOR),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
])

TABLE_CELL_STYLE = TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("BACKGROUND", (0, 0), (-1, -1), CELL_COLOR),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOX', (0, 0), (-1, -1), 1, colors.black)
])

TABLE_CELL_STYLE_DEBUG = TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("BACKGROUND", (0, 0), (-1, -1), CELL_COLOR),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOX', (0, 0), (-1, -1), 1, colors.red)
])

TABLE_SPACER_STYLE = TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("BACKGROUND", (0, 0), (-1, -1), CELL_COLOR),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOX', (0, 0), (-1, -1), 2, colors.black)
])

def _scheduling_data(blocks: list["WorkOrderBlock"]) -> list[list["Flowable"]]:
    block_rows: list[list["Flowable"]] = []
    for block in blocks:
        for row in block.header_rows:
            header_row = []
            for index, item in enumerate(row.data):
                style = PARA_PHASE_STYLE if index == 2 else PARA_BLOCKHEADER_STYLE
                header_row.append(_create_paragraph(item, style))
            block_rows.append(header_row)
        for row in block.data_rows:
            if row.is_actor:
                block_rows.append([_create_paragraph(item, PARA_ACTOR_STYLE) for item in row.data])
            else:
                rowitems = []
                for index, item in enumerate(row.data):
                    style = PARA_BLOCKHEADER_STYLE if index == 0 else PARA_ITEM_STYLE
                    rowitems.append(_create_paragraph(item, style))
                block_rows.append(rowitems)
    return block_rows

def _operations_data(blocks: list["WorkOrderBlock"]) -> list[list["Flowable"]]:
    block_rows: list[list["Flowable"]] = []
    for block in blocks:
        for row in block.header_rows:
            header_row = []
            for index, item in enumerate(row.data):
                style = PARA_PHASE_STYLE if index == 2 else PARA_BLOCKHEADER_STYLE
                header_row.append(_create_paragraph(item, style))
            block_rows.append(header_row)
        for row in block.data_rows:
            if row.is_actor:
                block_rows.append([_create_paragraph(item, PARA_ACTOR_STYLE) for item in row.data])
            else:
                rowitems = []
                for index, item in enumerate(row.data):
                    style = PARA_ITEM_STYLE
                    rowitems.append(_create_paragraph(item, style))
                block_rows.append(rowitems)
    return block_rows

BLOCK_TYPES = {
    ReportEnum.scheduling: _scheduling_data,
    ReportEnum.operations: _operations_data
}



def _create_paragraph(text: str, style: ParagraphStyle=PARA_ITEM_STYLE) -> Paragraph:
    if not text:
        return Paragraph("", style)
    return Paragraph(text, style)

def _create_table(data: list[list["Flowable"]], style: TableStyle, colWidths: list[float]=COLUMN_WIDTHS) -> Table:
    table = Table(data, colWidths=colWidths)
    table.setStyle(style)
    return table

def _group_tables(groups: list["TopLevelBlock"], blocktype:str) -> list["Flowable"]:
    data_func = BLOCK_TYPES.get(blocktype)
    if data_func is None:
        raise ValueError(f"Invalid blocktype: {blocktype}")
    flowables: list["Flowable"] = []
    if not groups:
        return flowables
    for group in groups:
        group_para = _create_paragraph(group.name, PARA_LABEL_STYLE)
        group_header_table = _create_table([[group_para]], TABLE_PAGEHEADER_STYLE, [PAGE_WIDTH * 0.9])
        room_tables = []
        for index, block in enumerate(group.blocks(blocktype=blocktype)):
            block_data = data_func([block])
            if index == 0:
                room_tables.append(KeepTogether([group_header_table, _create_table(block_data, TABLE_CELL_STYLE)]))
            else:
                room_tables.append(KeepTogether(_create_table(block_data, TABLE_CELL_STYLE)))
        if not room_tables:
            return []
        spacer = Spacer(0, TABLE_SPACING)
        flowables.extend([*room_tables, spacer])
    return flowables

def _header_date(daterange: tuple[str, str] | None = None) -> str:
    if daterange is None:
        return datetime.now().strftime('%m/%d/%Y')
    if daterange[0] == daterange[1]:
        return datetime.strptime(daterange[0], '%Y-%m-%d').strftime('%m/%d/%Y')
    start = datetime.strptime(daterange[0], '%Y-%m-%d').strftime('%m/%d/%Y')
    end = datetime.strptime(daterange[1], '%Y-%m-%d').strftime('%m/%d/%Y')
    return f"{start} - {end}"

def _report_header(pageheader: str, daterange: tuple[str, str] | None = None) -> Table:
    datestr = _header_date(daterange)
    header = _create_paragraph(f"{pageheader} {datestr}", PARA_PAGEHEADER_STYLE)
    return _create_table([[header]], TABLE_PAGEHEADER_STYLE, [PAGE_WIDTH])

def scheduling_pdf(groups: list["TopLevelBlock"], outputpath: Path, daterange: tuple[str, str] | None = None, debug: bool=False) -> None:
    doc = SimpleDocTemplate(str(outputpath), pagesize=PAGE_SIZE, topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN)
    if debug:
        first_group = groups[0]
        tables = _group_tables(groups=[first_group], blocktype=ReportEnum.scheduling)
    else:
        tables = _group_tables(groups, blocktype=ReportEnum.scheduling)
    report_header = _report_header("Room Schedule", daterange=daterange)
    header_padding = Spacer(0, 30)
    doc.build([report_header, header_padding, *tables])

def operations_pdf(groups: list["TopLevelBlock"], outputpath: Path, daterange: tuple[str, str] | None = None, debug: bool=False) -> None:
    doc = SimpleDocTemplate(str(outputpath), pagesize=PAGE_SIZE, topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN)
    if debug:
        first_group = groups[0]
        tables = _group_tables(groups=[first_group], blocktype=ReportEnum.operations)
    else:
        tables = _group_tables(groups, blocktype=ReportEnum.operations)
    report_header = _report_header("Operations Schedule", daterange=daterange)
    header_padding = Spacer(0, 30)
    doc.build([report_header, header_padding, *tables])