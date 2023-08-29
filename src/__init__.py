from pathlib import Path
from dataclasses import dataclass

PDFDIR = Path(__file__).parent.parent / "pdfdir"
DEFAULT_PDFPATH = PDFDIR / "callsheet.pdf"

@dataclass
class PhaseCode:
    code: str
    desc: str

class PhaseEnum:
    accrual_approved = PhaseCode("AAPV", "Accrual Approved")
    accrual_bill = PhaseCode("ABIL", "Accrual Bill")
    accrual_hold = PhaseCode("ACCH", "Accrual Hold")
    accrual = PhaseCode("ACCR", "Accrual")
    ad_mix_proposed = PhaseCode("ADM", "AD Mix Proposed")
    ad_voice_proposed = PhaseCode("ADP", "AD Voice Proposed")
    accrual_posted = PhaseCode("AINV", "Accrual Posted")
    batched = PhaseCode("Aprv", "Batched")
    accrual_void = PhaseCode("AVD", "Accrual Void")
    bid = PhaseCode("Bid", "Bid")
    ready_to_bill = PhaseCode("Bill", "Ready to Bill")
    confirmed = PhaseCode("Conf", "Confirmed")
    firm = PhaseCode("Firm", "Firm")
    hold = PhaseCode("Hold", "HOLD")
    invoiced = PhaseCode("Inv", "07 Invoiced")
    internal_complete = PhaseCode("INVX", "Internal Complete")
    in_progress = PhaseCode("MO1", "In Progress")
    needs_attention = PhaseCode("MO2", "Needs Attention")
    pending_approval = PhaseCode("PA", "Pending Approval")
    pending_po = PhaseCode("PPO", "Pending PO")
    proposed = PhaseCode("PROP", "Proposed")
    redo = PhaseCode("REDO", "REDO")
    shipped = PhaseCode("Ship", "Shipped")
    sent_to_billing = PhaseCode("STB", "Sent To Billing")
    completed = PhaseCode("Upd", "Completed")
    void_needed = PhaseCode("VDND", "VOID Needed")
    void = PhaseCode("Void", "VOID")

    @classmethod
    def get_desc(cls, code: str) -> str:
        code = code.lower()
        for phase in cls.__dict__.values():
            if not isinstance(phase, PhaseCode):
                continue
            if phase.code.lower() == code:
                return phase.desc
        return ""
    
    @classmethod
    def get_code(cls, desc: str) -> str:
        desc = desc.lower()
        for phase in cls.__dict__.values():
            if not isinstance(phase, PhaseCode):
                continue
            if phase.desc.lower() == desc:
                return phase.code
        return ""


PERSONNEL_GROUPS = [
    "Mixers",
    "QC Operators",
    "Mix Technicians",
    "Encoding & Packaging",
    "Colorists",
    "Recordists",
    "Editors",
    "Localization Ops",
    "Dubbing Editorial",
    "Foley Artists"
]

ROOM_GROUPS = [
    "Audio Stages",
    "Dub QC Rooms",
    "Dub Edit Rooms",
    "QC Rooms (per hour)",
    "Color Rooms",
    "ADR Stages",
    "QC Rooms (per length of program)",
    "Editorial Rooms",
    "Encoding Rooms",
    "Foley Room"
]

SAN_GROUPS = ["SAN Volumes"]

SAG_GROUPS = ["SAG Actors", "Set Teachers"]
SAG_GROUPS_ROOMS = ["ADR Stages"]

WO_TYPES = ["ADR Recording"]