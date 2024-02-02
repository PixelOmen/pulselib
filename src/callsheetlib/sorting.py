import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import TypeVar, TYPE_CHECKING, Union

from . import ReportEnum
from ..job import job_requests
from ..trx import Transaction, Personnel, Room, SAN, Equipment
from .. import PERSONNEL_GROUPS, ROOM_GROUPS, SAN_GROUPS, SAG_GROUPS, SAG_GROUPS_ROOMS

if TYPE_CHECKING:
    from ..roster import RosterTimeOff

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
    is_maintenance: bool = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, WorkOrderBlock):
            return (self.header_rows == other.header_rows and
                    self.data_rows == other.data_rows)
        return False
    
    def __lt__(self, other: "WorkOrderBlock") -> bool:
        if isinstance(other, WorkOrderBlock):
            row_a = 0 if self.is_maintenance else 1
            row_b = 0 if other.is_maintenance else 1
            return self.header_rows[row_a] < other.header_rows[row_b]
        raise TypeError(f"Cannot compare WorkOrderBlock to {type(other)}")

class TopLevelBlock:
    def __init__(self, data: Union["RoomGroup", "RosterTimeOff"]):
        self.data = data

    @property
    def name(self) -> str:
        if isinstance(self.data, RoomGroup):
            return self.data.room_trx.name
        else:
            return self.data.name

    def blocks(self, blocktype: str) -> list[WorkOrderBlock]:
        if isinstance(self.data, RoomGroup):
            return self.data.blocks(blocktype)
        else:
            return RoomGroup.roster_time_off_blocks([self.data])

@dataclass
class WorkorderGroup:
    wo_num: str
    personnel: list[Transaction]
    sans: list[Transaction]
    equipment: list[Transaction]
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
        if self.personnel:
            self.personnel.sort(key=lambda x: x.begin)

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
    job_jdict = {}
    project_manager: str | None = None

    def __post_init__(self):
        for wo, trxs in self.actors_by_wo.items():
            self.actorgroups.append(
                WorkorderGroup(
                    wo_num=wo,
                    personnel=trxs,
                    sans=[],
                    equipment=[],
                    room_trx=None,
                    is_actors=True
                )
            )

    def pull_project_manager(self, refresh: bool=False) -> None:
        if self.project_manager is not None and not refresh:
            return
        job_jdict = job_requests.get(self.job_num)
        sales_office_dict = job_jdict.get("sale_office_no")
        if sales_office_dict is None:
            raise ValueError(f"Job does not have a sales office dict in json response: {self.job_num}")
        pm_no = sales_office_dict.get("sale_office_no")
        if pm_no is None:
            raise ValueError(f"Sales office dict does not have a sale_office_no in Job: {self.job_num}")
        self.project_manager = job_requests.get_project_manager_desc(pm_no)


class RoomGroup:

    @staticmethod
    def format_date(datestr: str, fulldate: bool=False) -> str:
        date = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")
        if fulldate:
            return date.strftime("%m/%d/%Y %I:%M%p").lower()
        else:
            return date.strftime("%I:%M%p").lower()

    @staticmethod
    def roster_time_off_blocks(roster_time_offs: list["RosterTimeOff"]) -> list[WorkOrderBlock]:
        blocks: list[WorkOrderBlock] = []
        if not roster_time_offs:
            return blocks
        for timeoff in roster_time_offs:
            header_row1 = ["Maintenance",  RoomGroup.format_date(timeoff.start, fulldate=True), "", ""]
            header_rows = [DataRow(header_row1, is_wo_header=True)]
            begin = RoomGroup.format_date(timeoff.start)
            end = RoomGroup.format_date(timeoff.end)
            datestr = f"{begin} - {end}"
            datarow = DataRow(["", datestr, "", ""], is_actor=False)
            blocks.append(WorkOrderBlock(header_rows, [datarow], is_maintenance=True))
        return blocks
    
    def __init__(self, room_trx: Transaction, jobgroups: list[JobGroup],
                 table_headers: list[str] | None = None):
        # Duplicates are removed in table_data() and block_data() due to separate billing trxs
        self.room_trx = room_trx
        self.jobgroups: list[JobGroup] = jobgroups
        if table_headers is None:
            self.table_headers = ["Workorder", "Begin", "End", "Personnel", "Title", "Company", "SAN", "Notes"]
        else:
            self.table_headers = table_headers
        self.block_types = {
            ReportEnum.scheduling: self._scheduling_block,
            ReportEnum.operations: self._operations_block,
            ReportEnum.it: self._it_block
        }
        self._roster_time_offs: list[RosterTimeOff] = []

    def _get_datetime(self, date: str) -> datetime:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")

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
    
    def _format_adr_name(self, name: str) -> str:
        if name.startswith("ADR"):
            digit_str = name.split(" ")[1]
            if not digit_str.isdigit():
                return name
            no_padding = str(int(digit_str))
            return f"ADR {no_padding}"
        return name

    def _is_adr_match(self, room: str, desc: str) -> bool:
        """
        Check if the room name matches the ADR number in the actor wo description. 
        The job the actor transaction/workorder belongs to could contain
        multiple ADR rooms, so we need to check the description to make sure
        we are correctly matching the ADR room to the actor.
        """
        formatted_room = self._format_adr_name(room)
        match = re.search(r"ADR \d+", desc)
        if match:
            desc_room = match.group(0)
            if desc_room == room or desc_room == formatted_room:
                return True

        match = re.search(room, desc, re.IGNORECASE)
        if match:
            desc_room = match.group(0)
            if desc_room.lower().strip() == room.lower().strip():
                return True
        
        return False
    
    def _personnel_table_rows(self, workgroup: WorkorderGroup) -> list[list[str]]:
        cleandata = self._remove_duplicates(workgroup.personnel)
        san = workgroup.sans[0].name if workgroup.sans else ""
        rows = []
        for person in cleandata:
            begin = self.format_date(person.begin)
            end = self.format_date(person.end)
            rows.append([person.wo, begin, end, person.name, person.job_desc,
                         person.company, san, person.frontdeskinfo])
        return rows

    # ----- Deprecated -----
    # def _single_table_row(self, trx: Transaction, san: str="", is_room: bool=False) -> list[str]:
    #     begin = self._format_date(trx.begin)
    #     end = self._format_date(trx.end)
    #     person = "" if is_room else trx.name
    #     return [trx.wo, begin, end, person, trx.job_desc,
    #             trx.company, san, trx.frontdeskinfo]

    def _scheduling_block(self, jobgroup: JobGroup, workgroup: WorkorderGroup, room_trx: Transaction | None=None) -> WorkOrderBlock:
        if room_trx is None:
            room_trx = workgroup.get_room_trx()

        if jobgroup.project_manager is not None:
            rep = f"Project Manager: {jobgroup.project_manager}"
        else:
            rep = ""

        if self.room_trx.group in SAG_GROUPS_ROOMS and room_trx.dubbingdir:
            dubbingdir = f"Dubbing Director: {room_trx.dubbingdir}"
        else:
            dubbingdir = ""

        if workgroup.is_actors:
            job_desc = workgroup.personnel[0].job_desc
            wo = workgroup.wo_num
            wo_desc = workgroup.personnel[0].wo_desc
            date = self.format_date(workgroup.personnel[0].wo_begin, fulldate=True)
        else:
            job_desc = room_trx.job_desc
            wo = room_trx.wo
            wo_desc = room_trx.wo_desc
            date = self.format_date(room_trx.wo_begin, fulldate=True)

        if room_trx.frontdeskinfo:
            frontdesk = f"Front Desk Info: <br/>{room_trx.frontdeskinfo}"
        else:
            frontdesk = ""

        header_row1 = [job_desc, f"Order No: {wo}", "", wo_desc]
        header_row2 = [room_trx.company, date, room_trx.phase_desc, frontdesk]
        header_row3 = [rep, "", "", ""]
        header_row4 = [dubbingdir, "", "", ""]
        header_rows = [
            DataRow(header_row1, is_wo_header=True),
            DataRow(header_row2, is_wo_header=True),
            DataRow(header_row3, is_wo_header=True),
            DataRow(header_row4, is_wo_header=True)
        ]
        if dubbingdir:
            header_rows.append(DataRow(["", "", "", ""], is_wo_header=True))

        data_rows = []
        if workgroup.room_only:
            begin = self.format_date(room_trx.begin)
            end = self.format_date(room_trx.end)
            data_rows.append(DataRow(["", f"{begin} - {end}", "", ""]))
        else:
            for person in workgroup.personnel:
                begin = self.format_date(person.begin)
                end = self.format_date(person.end)
                datestr = f"{begin} - {end}"
                desc = f"{person.group}: {person.name}"
                note = self._parse_html_note(person.note)
                datarow = DataRow([desc, datestr, "", note], workgroup.is_actors)
                data_rows.append(datarow)

        for san in workgroup.sans:
            begin = self.format_date(san.begin)
            end = self.format_date(san.end)
            datestr = f"{begin} - {end}"
            desc = f"{san.group}: {san.name}"
            datarow = DataRow([desc, datestr, "", ""], is_actor=False)
            data_rows.append(datarow)

        for equip in workgroup.equipment:
            begin = self.format_date(equip.begin)
            end = self.format_date(equip.end)
            datestr = f"{begin} - {end}"
            desc = f"{equip.group}: {equip.name}"
            datarow = DataRow([desc, datestr, "", ""], is_actor=False)
            data_rows.append(datarow)

        return WorkOrderBlock(header_rows, data_rows)

    def _operations_block(self, jobgroup: JobGroup, workgroup: WorkorderGroup, room_trx: Transaction | None=None) -> WorkOrderBlock:
        if room_trx is None:
            room_trx = workgroup.get_room_trx()

        if jobgroup.project_manager is not None:
            rep = f"Project Manager: {jobgroup.project_manager}"
        else:
            rep = ""

        if self.room_trx.group in SAG_GROUPS_ROOMS and room_trx.dubbingdir:
            dubbingdir = f"Dubbing Director: {room_trx.dubbingdir}"
        else:
            dubbingdir = ""

        if workgroup.is_actors:
            job_desc = workgroup.personnel[0].job_desc
            wo = workgroup.wo_num
            wo_desc = workgroup.personnel[0].wo_desc
            date = self.format_date(workgroup.personnel[0].wo_begin, fulldate=True)
        else:
            job_desc = room_trx.job_desc
            wo = room_trx.wo
            wo_desc = room_trx.wo_desc
            date = self.format_date(room_trx.wo_begin, fulldate=True)

        if room_trx.frontdeskinfo:
            frontdesk = f"Front Desk Info: <br/>{room_trx.frontdeskinfo}"
        else:
            frontdesk = ""

        header_row1 = [job_desc, f"Order No: {wo}", "", wo_desc]
        header_row2 = [room_trx.company, date, room_trx.phase_desc, frontdesk]
        header_row3 = [rep, "", "", ""]
        header_row4 = [dubbingdir, "", "", ""]
        header_rows = [
            DataRow(header_row1, is_wo_header=True),
            DataRow(header_row2, is_wo_header=True),
            DataRow(header_row3, is_wo_header=True),
            DataRow(header_row4, is_wo_header=True)
        ]
        if dubbingdir:
            header_rows.append(DataRow(["", "", "", ""], is_wo_header=True))

        data_rows = []
        if workgroup.room_only:
            begin = self.format_date(room_trx.begin)
            end = self.format_date(room_trx.end)
            data_rows.append(DataRow(["", f"{begin} - {end}", "", ""]))
        else:
            for person in workgroup.personnel:
                begin = self.format_date(person.begin)
                end = self.format_date(person.end)
                datestr = f"{begin} - {end}"
                desc = f"{person.group}: {person.name}"
                note = self._parse_html_note(person.note)
                datarow = DataRow([desc, datestr, "", note], workgroup.is_actors)
                data_rows.append(datarow)

        for san in workgroup.sans:
            begin = self.format_date(san.begin)
            end = self.format_date(san.end)
            datestr = f"{begin} - {end}"
            desc = f"{san.group}: {san.name}"
            datarow = DataRow([desc, datestr, "", ""], is_actor=False)
            data_rows.append(datarow)

        for equip in workgroup.equipment:
            begin = self.format_date(equip.begin)
            end = self.format_date(equip.end)
            datestr = f"{begin} - {end}"
            desc = f"{equip.group}: {equip.name}"
            datarow = DataRow([desc, datestr, "", ""], is_actor=False)
            data_rows.append(datarow)

        return WorkOrderBlock(header_rows, data_rows)

    def _it_block(self, jobgroup: JobGroup, workgroup: WorkorderGroup, room_trx: Transaction | None=None) -> WorkOrderBlock:
        if room_trx is None:
            room_trx = workgroup.get_room_trx()

        if jobgroup.project_manager is not None:
            rep = f"Project Manager: {jobgroup.project_manager}"
        else:
            rep = ""

        if self.room_trx.group in SAG_GROUPS_ROOMS and room_trx.dubbingdir:
            dubbingdir = f"Dubbing Director: {room_trx.dubbingdir}"
        else:
            dubbingdir = ""

        if workgroup.is_actors:
            job_desc = workgroup.personnel[0].job_desc
            wo = workgroup.wo_num
            wo_desc = workgroup.personnel[0].wo_desc
            date = self.format_date(workgroup.personnel[0].wo_begin, fulldate=True)
        else:
            job_desc = room_trx.job_desc
            wo = room_trx.wo
            wo_desc = room_trx.wo_desc
            date = self.format_date(room_trx.wo_begin, fulldate=True)

        if room_trx.frontdeskinfo:
            frontdesk = f"Front Desk Info: <br/>{room_trx.frontdeskinfo}"
        else:
            frontdesk = ""

        header_row1 = [job_desc, f"Order No: {wo}", "", wo_desc]
        header_row2 = [room_trx.company, date, room_trx.phase_desc, frontdesk]
        header_row3 = [rep, "", "", ""]
        header_row4 = [dubbingdir, "", "", ""]
        header_rows = [
            DataRow(header_row1, is_wo_header=True),
            DataRow(header_row2, is_wo_header=True),
            DataRow(header_row3, is_wo_header=True),
            DataRow(header_row4, is_wo_header=True)
        ]
        if dubbingdir:
            header_rows.append(DataRow(["", "", "", ""], is_wo_header=True))

        data_rows = []
        if workgroup.room_only:
            begin = self.format_date(room_trx.begin)
            end = self.format_date(room_trx.end)
            data_rows.append(DataRow(["", f"{begin} - {end}", "", ""]))
        else:
            for person in workgroup.personnel:
                begin = self.format_date(person.begin)
                end = self.format_date(person.end)
                datestr = f"{begin} - {end}"
                desc = f"{person.group}: {person.name}"
                note = self._parse_html_note(person.note)
                datarow = DataRow([desc, datestr, "", note], workgroup.is_actors)
                data_rows.append(datarow)

        for san in workgroup.sans:
            begin = self.format_date(san.begin)
            end = self.format_date(san.end)
            datestr = f"{begin} - {end}"
            desc = f"{san.group}: {san.name}"
            datarow = DataRow([desc, datestr, "", ""], is_actor=False)
            data_rows.append(datarow)

        for equip in workgroup.equipment:
            begin = self.format_date(equip.begin)
            end = self.format_date(equip.end)
            datestr = f"{begin} - {end}"
            desc = f"{equip.group}: {equip.name}"
            datarow = DataRow([desc, datestr, "", ""], is_actor=False)
            data_rows.append(datarow)

        return WorkOrderBlock(header_rows, data_rows)

    def pull_project_managers(self) -> None:
        for jobgroup in self.jobgroups:
            jobgroup.pull_project_manager()
    
    def add_roster_time_offs(self, roster_time_offs: list["RosterTimeOff"]) -> None:
        self._roster_time_offs += roster_time_offs

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
                blocks.append(block_method(jobgroup, workgroup))
            if self.room_trx.group in SAG_GROUPS_ROOMS:
                for actorgroup in jobgroup.actorgroups:
                    if self.room_trx.name.lower().startswith("adr"):
                        wo_desc = actorgroup.personnel[0].wo_desc
                        if not self._is_adr_match(self.room_trx.name, wo_desc):
                            continue
                    blocks.append(block_method(jobgroup, actorgroup, self.room_trx))
        blocks.extend(self.roster_time_off_blocks(self._roster_time_offs))
        blocks.sort()
        return self._remove_duplicates(blocks)
    
    # ----- Deprecated -----
    # def table_data(self) -> list[DataRow]:
    #     rows: list[DataRow] = []
    #     for jobgroup in self.jobgroups:
    #         for workgroup in jobgroup.workordergroups:
    #             if workgroup.room_trx is None or workgroup.room_trx.name != self.room_trx.name:
    #                 continue
    #             if workgroup.room_only:
    #                 san = workgroup.sans[0].name if workgroup.sans else ""
    #                 rows.append(DataRow(self._single_table_row(workgroup.room_trx, san, is_room=True), is_wo_header=True))
    #             else:
    #                 personnel = self._personnel_table_rows(workgroup)
    #                 if personnel:
    #                     rows.extend([DataRow(row, is_actor=False) for row in personnel])
    #         if self.room_trx.group in SAG_GROUPS_ROOMS:
    #             for actorlist in jobgroup.actors_by_wo.values():
    #                 rows.extend([DataRow(self._single_table_row(actor), is_actor=True) for actor in actorlist])
    #     rows.sort()
    #     return self._remove_duplicates(rows)
    


class ResourceGroups:
    def __init__(self, transactions: list[Transaction]):
        self.trxlist = transactions
        self.personnel: list[Personnel] = []
        self.sag_actors: list[Personnel] = []
        self.rooms: list[Room] = []
        self.sans: list[SAN] = []
        self.equipment: list[Equipment] = []
        self.other: dict[str, list[Transaction]] = {}
        self._split_into_groups()

    # def _filter_equipment(self) -> tuple[list[Transaction], list[Transaction]]:
    #     equipment: list[Transaction] = []
    #     non_equipment: list[Transaction] = []
    #     for trx in self.trxlist:
    #         resource = trx.get_resource()
    #         if resource is None:
    #             raise ValueError(f"Transaction does not have a resource: {trx.name}")
    #         if resource.type.lower() == "equipment":
    #             equipment.append(trx)
    #         else:
    #             non_equipment.append(trx)
    #     return equipment, non_equipment


    def _split_into_groups(self) -> None:
        # temp dicts to avoid multiple objects with same name
        personnel: dict[str, list[Transaction]] = {}
        actors: dict[str, list[Transaction]] = {}
        rooms: dict[str, list[Transaction]] = {}
        sans: dict[str, list[Transaction]] = {}
        equipment: dict[str, list[Transaction]] = {}

        for trx in self.trxlist:
            resource = trx.get_resource()
            if resource is None:
                raise ValueError(f"Transaction does not have a resource: {trx.name}")
            if resource.type.lower() == "equipment":
                equipment.setdefault(trx.name, []).append(trx)
                continue

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
        self.equipment = [Equipment(name, trxlist) for name, trxlist in equipment.items()]

    def _search_equipment(self, wo_or_job: str, byjob:bool = False) -> list[Transaction]:
        equipment: list[Transaction] = []
        for equip in self.equipment:
            for trx in equip.trxlist:
                if byjob and trx.job == wo_or_job:
                    equipment.append(trx)
                elif not byjob and trx.wo == wo_or_job:
                    equipment.append(trx)
        return equipment

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
                equipment = self._search_equipment(wo)
                jobdict.setdefault((job_info, job_desc), []).append(WorkorderGroup(wo, personnel, sans, equipment, room_trx))

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