import re
from typing import TypeVar
from datetime import datetime
from dataclasses import dataclass, field

from . import ReportEnum
from ..trx import Transaction, Personnel, Room, SAN
from .. import PERSONNEL_GROUPS, ROOM_GROUPS, SAN_GROUPS, SAG_GROUPS, SAG_GROUPS_ROOMS

T = TypeVar("T")

CALLSHEET_ROOMS = ROOM_GROUPS[:]
CALLSHEET_ROOMS.remove("Encoding Rooms")
CALLSHEET_ROOMS.remove("Dub QC Rooms")
CALLSHEET_ROOMS.remove("QC Rooms (per hour)")
CALLSHEET_ROOMS.remove("QC Rooms (per length of program)")

CALLSHEET_PERSONNEL = PERSONNEL_GROUPS[:]
CALLSHEET_PERSONNEL.remove("QC Operators")
CALLSHEET_PERSONNEL.remove("Encoding & Packaging")


@dataclass
class DataRow:
    data: list[str]
    is_actor: bool = False
    is_wo_header: bool = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DataRow):
            return self.data == other.data
        return False
    
    def __lt__(self, other: "DataRow") -> bool:
        if isinstance(other, DataRow):
            if self.is_wo_header:
                format = "%m/%d/%Y %I:%M%p"
            else:
                format = "%I:%M%p"
            date1 = datetime.strptime(self.data[1], format)
            date2 = datetime.strptime(other.data[1], format)
            return date1 < date2
        raise TypeError(f"Cannot compare DataRow to {type(other)}")

@dataclass
class WorkOrderBlock:
    header_rows: list[DataRow]
    data_rows: list[DataRow]
    is_actors: bool = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, WorkOrderBlock):
            return (self.header_rows == other.header_rows and
                    self.data_rows == other.data_rows)
        return False
    
    def __lt__(self, other: "WorkOrderBlock") -> bool:
        if isinstance(other, WorkOrderBlock):
            return self.header_rows[1] < other.header_rows[1]
        raise TypeError(f"Cannot compare WorkOrderBlock to {type(other)}")

@dataclass
class WorkorderGroup:
    wo_num: str
    personnel: list[Transaction]
    sans: list[Transaction]
    room_trx: Transaction | None = None
    is_actors: bool = False
    room_only: bool = field(init=False)

    def __post_init__(self):
        self.room_only = True if not self.personnel else False
        if self.room_only and not self.room_trx:
            raise ValueError(f"Room group must have a room transaction: {self.wo_num}")
        if self.room_only and self.is_actors:
            raise ValueError(f"Room group cannot be actors: {self.wo_num}")
        if self.is_actors and not self.personnel:
            raise ValueError(f"Actor group must have personnel: {self.wo_num}")
        if self.is_actors and self.room_trx:
            raise ValueError(f"Actor group cannot have room transaction: {self.wo_num}")

    def get_room_trx(self) -> Transaction:
        if self.room_trx is None:
            raise AttributeError(f"Workorder group does not have room transaction: {self.wo_num}")
        return self.room_trx

@dataclass
class JobGroup:
    job_num: str
    job_desc: str
    workordergroups: list[WorkorderGroup]
    actors_by_wo: dict[str, list[Transaction]] = field(default_factory=dict)
    actorgroups: list [WorkorderGroup] = field(default_factory=list)

    def __post_init__(self):
        for wo, trxs in self.actors_by_wo.items():
            self.actorgroups.append(WorkorderGroup(
                wo_num=wo,
                personnel=trxs,
                sans=[],
                room_trx=None,
                is_actors=True
            ))

class RoomGroup:
    def __init__(self, room_trx: Transaction, jobgroups: list[JobGroup], table_headers: list[str]=...):
        # Duplicates are removed in table_data() and block_data() due to separate billing trxs
        self.room_trx = room_trx
        self.jobgroups: list[JobGroup] = jobgroups
        if table_headers is ...:
            self.table_headers = ["Workorder", "Begin", "End", "Personnel", "Title", "Company", "SAN", "Notes"]
        else:
            self.table_headers = table_headers
        self.block_types = {
            ReportEnum.scheduling: self._scheduling_block,
            ReportEnum.operations: self._operations_block,
        }

    def _get_datetime(self, date: str) -> datetime:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    
    def _format_date(self, datestr: str, fulldate: bool=False) -> str:
        date = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")
        if fulldate:
            return date.strftime("%m/%d/%Y %I:%M%p").lower()
        else:
            return date.strftime("%I:%M%p").lower()

    def _remove_duplicates(self, data: list[T]) -> list[T]:
        no_dupes = []
        for item in data:
            if item not in no_dupes:
                no_dupes.append(item)
        return no_dupes

    def _parse_html_note(self, notestr: str) -> str:
        if not notestr:
            return ""
        intag = False
        contents = ""
        for char in notestr:
            if char == "<":
                intag = True
            elif char == ">":
                intag = False
            if not intag and char != "<" and char != ">":
                contents += char
        return contents
    
    def _personnel_table_rows(self, workgroup: WorkorderGroup) -> list[list[str]]:
        cleandata = self._remove_duplicates(workgroup.personnel)
        san = workgroup.sans[0].name if workgroup.sans else ""
        rows = []
        for person in cleandata:
            begin = self._format_date(person.begin)
            end = self._format_date(person.end)
            rows.append([person.wo, begin, end, person.name, person.job_desc,
                         person.company, san, person.frontdeskinfo])
        return rows

    def _single_table_row(self, trx: Transaction, san: str="", is_room: bool=False) -> list[str]:
        begin = self._format_date(trx.begin)
        end = self._format_date(trx.end)
        person = "" if is_room else trx.name
        return [trx.wo, begin, end, person, trx.job_desc,
                trx.company, san, trx.frontdeskinfo]

    def _scheduling_block(self, workgroup: WorkorderGroup, room_trx: Transaction | None=None) -> WorkOrderBlock:
        if room_trx is None:
            room_trx = workgroup.get_room_trx()

        if self.room_trx.group in SAG_GROUPS_ROOMS and room_trx.dubbingdir:
            dubbingdir = f"Dubbing Director: {room_trx.dubbingdir}"
        else:
            dubbingdir = ""

        if workgroup.is_actors:
            job_desc = workgroup.personnel[0].job_desc
            wo = workgroup.wo_num
            wo_desc = workgroup.personnel[0].wo_desc
            date = self._format_date(workgroup.personnel[0].wo_begin, fulldate=True)
        else:
            job_desc = room_trx.job_desc
            wo = room_trx.wo
            wo_desc = room_trx.wo_desc
            date = self._format_date(room_trx.wo_begin, fulldate=True)

        if room_trx.frontdeskinfo:
            frontdesk = f"Front Desk Info: <br/>{room_trx.frontdeskinfo}"
        else:
            frontdesk = ""

        header_row1 = [job_desc, f"Order No: {wo}", "", wo_desc]
        header_row2 = [dubbingdir, date, room_trx.phase_desc, frontdesk]
        header_rows = [DataRow(header_row1, is_wo_header=True), DataRow(header_row2, is_wo_header=True)]

        data_rows = []
        if workgroup.room_only:
            begin = self._format_date(room_trx.begin)
            end = self._format_date(room_trx.end)
            data_rows.append(DataRow(["", f"{begin} - {end}", "", ""]))
        else:
            for person in workgroup.personnel:
                begin = self._format_date(person.begin)
                end = self._format_date(person.end)
                datestr = f"{begin} - {end}"
                desc = f"{person.group}: {person.name}"
                note = self._parse_html_note(person.note)
                datarow = DataRow([desc, datestr, "", note], workgroup.is_actors)
                data_rows.append(datarow)

        for san in workgroup.sans:
            begin = self._format_date(san.begin)
            end = self._format_date(san.end)
            datestr = f"{begin} - {end}"
            desc = f"{san.group}: {san.name}"
            datarow = DataRow([desc, datestr, "", ""], is_actor=False)
            data_rows.append(datarow)

        return WorkOrderBlock(header_rows, data_rows)

    def _operations_block(self, workgroup: WorkorderGroup, room_trx: Transaction | None=None) -> WorkOrderBlock:
        if room_trx is None:
            room_trx = workgroup.get_room_trx()

        if room_trx.wo_rep:
            rep = f"Added by: {room_trx.wo_rep}"
        else:
            rep = ""

        if workgroup.is_actors:
            job_desc = workgroup.personnel[0].job_desc
            wo = workgroup.wo_num
            wo_desc = workgroup.personnel[0].wo_desc
            date = self._format_date(workgroup.personnel[0].wo_begin, fulldate=True)
        else:
            job_desc = room_trx.job_desc
            wo = room_trx.wo
            wo_desc = room_trx.wo_desc
            date = self._format_date(room_trx.wo_begin, fulldate=True)

        if room_trx.frontdeskinfo:
            frontdesk = f"Front Desk Info: <br/>{room_trx.frontdeskinfo}"
        else:
            frontdesk = ""

        header_row1 = [job_desc, f"Order No: {wo}", "", wo_desc]
        header_row2 = [rep, date, room_trx.phase_desc, frontdesk]
        header_rows = [DataRow(header_row1, is_wo_header=True), DataRow(header_row2, is_wo_header=True)]

        data_rows = []
        if workgroup.room_only:
            begin = self._format_date(room_trx.begin)
            end = self._format_date(room_trx.end)
            data_rows.append(DataRow(["", f"{begin} - {end}", "", ""]))
        else:
            for person in workgroup.personnel:
                begin = self._format_date(person.begin)
                end = self._format_date(person.end)
                datestr = f"{begin} - {end}"
                desc = f"{person.group}: {person.name}"
                note = self._parse_html_note(person.note)
                datarow = DataRow([desc, datestr, "", note], workgroup.is_actors)
                data_rows.append(datarow)

        for san in workgroup.sans:
            begin = self._format_date(san.begin)
            end = self._format_date(san.end)
            datestr = f"{begin} - {end}"
            desc = f"{san.group}: {san.name}"
            datarow = DataRow([desc, datestr, "", ""], is_actor=False)
            data_rows.append(datarow)

        return WorkOrderBlock(header_rows, data_rows)

    def table_data(self) -> list[DataRow]:
        rows: list[DataRow] = []
        for jobgroup in self.jobgroups:
            for workgroup in jobgroup.workordergroups:
                if workgroup.room_trx is None or workgroup.room_trx.name != self.room_trx.name:
                    continue
                if workgroup.room_only:
                    san = workgroup.sans[0].name if workgroup.sans else ""
                    rows.append(DataRow(self._single_table_row(workgroup.room_trx, san, is_room=True), is_wo_header=True))
                else:
                    personnel = self._personnel_table_rows(workgroup)
                    if personnel:
                        rows.extend([DataRow(row, is_actor=False) for row in personnel])
            if self.room_trx.group in SAG_GROUPS_ROOMS:
                for actorlist in jobgroup.actors_by_wo.values():
                    rows.extend([DataRow(self._single_table_row(actor), is_actor=True) for actor in actorlist])
        rows.sort()
        return self._remove_duplicates(rows)
    
    def blocks(self, blocktype: str) -> list[WorkOrderBlock]:
        block_method = self.block_types.get(blocktype)
        if block_method is None:
            raise ValueError(f"Invalid block type: {blocktype}")
        blocks: list[WorkOrderBlock] = []
        for jobgroup in self.jobgroups:
            for workgroup in jobgroup.workordergroups:
                if (workgroup.room_trx is None or
                    workgroup.room_trx.name != self.room_trx.name):
                    continue
                blocks.append(block_method(workgroup))
            if self.room_trx.group in SAG_GROUPS_ROOMS:
                for actor in jobgroup.actorgroups:
                    blocks.append(self._scheduling_block(actor, self.room_trx))
        blocks.sort()
        return self._remove_duplicates(blocks)



class ResourceGroups:
    def __init__(self, transactions: list[Transaction]):
        self.trxlist = transactions
        self.personnel: list[Personnel] = []
        self.sag_actors: list[Personnel] = []
        self.rooms: list[Room] = []
        self.sans: list[SAN] = []
        self.other: dict[str, list[Transaction]] = {}
        self._split_into_groups()

    def _split_into_groups(self) -> None:
        # temp dicts to avoid multiple objects with same name
        personnel: dict[str, list[Transaction]] = {}
        actors: dict[str, list[Transaction]] = {}
        rooms: dict[str, list[Transaction]] = {}
        sans: dict[str, list[Transaction]] = {}

        for trx in self.trxlist:
            if trx.group in CALLSHEET_PERSONNEL:
                personnel.setdefault(trx.name, []).append(trx)
            elif trx.group in SAG_GROUPS:
                actors.setdefault(trx.name, []).append(trx)
            elif trx.group in CALLSHEET_ROOMS:
                rooms.setdefault(trx.name, []).append(trx)
            elif trx.group in SAN_GROUPS:
                sans.setdefault(trx.name, []).append(trx)
            else:
                self.other.setdefault(trx.name, []).append(trx)

        self.personnel = [Personnel(name, trxlist) for name, trxlist in personnel.items()]
        self.sag_actors = [Personnel(name, trxlist) for name, trxlist in actors.items()]
        self.rooms = [Room(name, trxlist) for name, trxlist in rooms.items()]
        self.sans = [SAN(name, trxlist) for name, trxlist in sans.items()]

    def _search_sans(self, wo_or_job: str, byjob:bool = False) -> list[Transaction]:
        sans: list[Transaction] = []
        for san in self.sans:
            for trx in san.trxlist:
                if byjob and trx.job == wo_or_job:
                    sans.append(trx)
                elif not byjob and trx.wo == wo_or_job:
                    sans.append(trx)
        return sans

    def _search_personnel(self, wo_or_job: str, byjob:bool = False, actors: bool=False) -> list[Transaction]:
        personlist = self.sag_actors if actors else self.personnel
        personnel: list[Transaction] = []
        for person in personlist:
            for trx in person.trxlist:
                if byjob and trx.job == wo_or_job:
                    personnel.append(trx)
                elif not byjob and trx.wo == wo_or_job:
                    personnel.append(trx)
        return personnel
    
    def jobgroups(self) -> list[JobGroup]:
        jobdict: dict[tuple[str, str], list[WorkorderGroup]] = {}
        for room in self.rooms:
            for room_trx in room.trxlist:
                wo = room_trx.wo
                job_info = room_trx.job
                job_desc = room_trx.job_desc
                sans = self._search_sans(wo)
                personnel = self._search_personnel(wo)
                jobdict.setdefault((job_info, job_desc), []).append(WorkorderGroup(wo, personnel, sans, room_trx))

        joblist: list[JobGroup] = []
        for job_info, workorders in jobdict.items():
            job_num = job_info[0]
            job_desc = job_info[1]
            actors = self._search_personnel(job_num, byjob=True, actors=True)
            actors_by_wo: dict[str, list[Transaction]] = {}
            for actor in actors:
                actors_by_wo.setdefault(actor.wo, []).append(actor)
            joblist.append(JobGroup(job_num, job_desc, workorders, actors_by_wo))
        return joblist

    def roomgroups(self) -> list[RoomGroup]:
        jobgroups = self.jobgroups()
        roomdict: dict[str, tuple[Transaction, list[JobGroup]]] = {}
        for jobgroup in jobgroups:
            for workgroup in jobgroup.workordergroups:
                if workgroup.room_trx is None:
                    raise ValueError(f"Workorder group must have a room transaction: {workgroup.wo_num}")
                jobgroups_by_room = roomdict.setdefault(workgroup.room_trx.name, (workgroup.room_trx, []))
                if jobgroup not in jobgroups_by_room[1]:
                    jobgroups_by_room[1].append(jobgroup)
        room_groups = [RoomGroup(trx, jobgroups) for trx, jobgroups in roomdict.values()]
        room_groups.sort(key=lambda x: x.room_trx.name)
        return room_groups