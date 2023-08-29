from pathlib import Path
from xml.etree import ElementTree as ET

from src import utils, PhaseEnum
from src.trx import trx_requests

# today = utils.today()
# trxs = trx_requests.by_date(daterange=(today, today))
# utils.print_transactions(trxs)

# TEST_XML = Path(__file__).parent / "examples" / "test.xml"

# root = ET.parse(TEST_XML).getroot()
# phases = root.iterfind("{http://tempuri.org/JmPhaseDataSet.xsd}" + "jm_phase")
# for phase in phases:
#     code = list(phase.iterfind("{http://tempuri.org/JmPhaseDataSet.xsd}" + "phase_code"))[0]
#     desc = list(phase.iterfind("{http://tempuri.org/JmPhaseDataSet.xsd}" + "phase_desc"))[0]
#     final_str = f"{desc.text.replace(' ', '_').lower()} = PhaseCode(\"{code.text}\", \"{desc.text}\")" #type:ignore
#     print(final_str)

print(PhaseEnum.get_desc("upd"))