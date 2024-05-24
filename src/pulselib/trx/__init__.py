from typing import Union
from dataclasses import dataclass

from ..errors import TRXUncaughtError
from ..resource.model import Resource
from ..resource import resource_requests


@dataclass()
class Transaction:
    jdict: dict
    name: str
    job: str
    wo: str
    added_by: str
    job_desc: str
    wo_desc: str
    wo_type: str
    wo_begin: str
    dubbingdir: str
    begin: str
    end: str
    row_display: str
    company: str
    note: str
    group: str
    frontdeskinfo: str
    phase_code: str
    phase_desc: str

    @classmethod
    def from_dict(cls, d: dict) -> "Transaction":
        dubbing_director_obj = d.get("job_table1_no")
        if dubbing_director_obj:
            dubbingdir = dubbing_director_obj["job_table1_desc"]
        else:
            dubbingdir = ""
        phase = d.get("phase_code")
        if phase:
            phase_code = phase["phase_code"]
            phase_desc = phase["phase_desc"]
        else:
            phase_code = ""
            phase_desc = ""
        try:
            obj = cls(
                jdict = d,
                name=d["resource_desc"],
                job=d["wo_job_no"]["wo_job_no"],
                wo=d["wo_no_seq"]["wo_no_seq"],
                added_by=d["user_added"]["full_name"],
                job_desc=d["job_desc"],
                wo_desc=d["wo_desc"],
                wo_type=d["wo_type_no"]["wo_type_desc"],
                wo_begin=d["wo_begin_dt"],
                dubbingdir=dubbingdir,
                begin=d["trx_begin_dt"],
                end=d["trx_end_dt"],
                row_display=d["row_display"],
                company=d["customer_name"],
                note=d["note_no_text"],
                group=d["group_desc"],
                frontdeskinfo=d["WO_field_2"],
                phase_code=phase_code,
                phase_desc=phase_desc
            )
        except Exception as e:
            raise TRXUncaughtError(d) from e
        return obj
    
    def get_resource(self) -> Union["Resource", None]:
        results = resource_requests.query({"resource_desc": self.name})
        if results:
            return Resource(results[0])
        else:
            return None
        
    def __str__(self) -> str:
        return f"{self.name} - Job:{self.job} - WO:{self.wo} - ({self.begin} - {self.end})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return False
        return (self.name == other.name and
                self.job == other.job and
                self.wo == other.wo and
                self.begin == other.begin and
                self.end == other.end)
    
    def __hash__(self) -> int:
        return hash(id(self))
    
class TransactionGroup:
    def __init__(self, name: str, trxlist: list["Transaction"]):
        if not trxlist:
            raise ValueError(f"Resource initialized with empty trxlist: {name}")
        self.name = name
        self.trxlist = trxlist

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    def get_job(self) -> str:
        return self.trxlist[0].job
        
class Personnel(TransactionGroup):
    def __init__(self, name: str, trxlist: list["Transaction"]):
        super().__init__(name, trxlist)

class Room(TransactionGroup):
    def __init__(self, name: str, trxlist: list["Transaction"]):
        super().__init__(name, trxlist)

class SAN(TransactionGroup):
    def __init__(self, name: str, trxlist: list["Transaction"]):
        super().__init__(name, trxlist)

class Equipment(TransactionGroup):
    def __init__(self, name: str, trxlist: list["Transaction"]):
        super().__init__(name, trxlist)