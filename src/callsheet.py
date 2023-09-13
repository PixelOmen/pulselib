import uuid
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

from .trx import trx_requests
from .callsheetlib import ReportEnum, report_block
from .callsheetlib.sorting import ResourceGroups
from . import PDFDIR, DEFAULT_PDFPATH

if TYPE_CHECKING:
    from logging import Logger

PDF_THREAD_ACTIVE = False
PDF_LOCK = threading.Lock()

REPORT_TYPES = {
    "scheduling": report_block.scheduling_pdf,
    "operations": report_block.operations_pdf
}

def _cleanup_pdf(pdfpath: Path) -> None:
    time.sleep(10)
    if pdfpath.is_file():
        pdfpath.unlink()

def _log_pdf_generation( onrequest: bool=True, printlog: bool=False, logger: "Logger"=...) -> None:
    if onrequest and printlog:
        if logger is not ...:
            logger.info(f"{datetime.now()}: Generating PDF on request...")
        else:
            print(f"{datetime.now()}: Generating PDF on request...", flush=True)
    elif printlog:
        if logger is not ...:
            logger.info(f"{datetime.now()}: Generating PDF on timer...")
        else:
            print(f"{datetime.now()}: Generating PDF on timer...", flush=True)

def callsheet_by_date(daterange: tuple[str, str]=..., pdfpath: Path=...,
                        report_type: str="scheduling", onhold: bool=True, invoiced: bool=True,
                        proposed: bool=True, onrequest: bool=True, printlog: bool=False, logger: "Logger"=...) -> Path:
    if pdfpath is ...:
        pdfpath = DEFAULT_PDFPATH
    pdf_func = REPORT_TYPES.get(report_type)
    if pdf_func is None:
        raise NotImplementedError(f"Callsheet type has not been implemented. Requested: {report_type}")
    _log_pdf_generation(onrequest, printlog, logger)
    response = trx_requests.by_date(daterange, onhold=onhold, invoiced=invoiced, proposed=proposed, raw=False)
    groups = ResourceGroups(response).roomgroups()
    pdf_func(groups, pdfpath, daterange=daterange)
    if pdfpath != DEFAULT_PDFPATH:
        threading.Thread(target=_cleanup_pdf, args=(pdfpath,), daemon=True).start()
    return pdfpath

def query_handler(userjson: dict) -> Path:
    pdfpath = PDFDIR / f"report_{str(uuid.uuid4())}.pdf"
    daterange = (userjson["date"]["from"], userjson["date"]["to"])
    if daterange[1] == "":
        daterange = (daterange[0], daterange[0])
    if userjson["type"] == ReportEnum.scheduling:
        requested_date = datetime.strptime(daterange[0], "%Y-%m-%d")
        today = datetime.strptime(str(datetime.today().date()), "%Y-%m-%d")
        invoiced = True if requested_date < today else False
        return callsheet_by_date(daterange=daterange, pdfpath=pdfpath, report_type=ReportEnum.scheduling,
                                    onhold=False, invoiced=invoiced, proposed=False, onrequest=True, printlog=True)
    elif userjson["type"] == ReportEnum.operations:
        return callsheet_by_date(daterange=daterange, pdfpath=pdfpath, report_type=ReportEnum.operations,
                                    onhold=True, invoiced=True, onrequest=True, printlog=True)
    raise NotImplementedError(f"Callsheet type has not been implemented. Requested: {userjson['type']}")