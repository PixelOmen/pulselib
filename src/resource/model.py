import re
from copy import deepcopy
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass, field

from . import resource_requests
from .resourcefiledmaps import LINGUIST_MAPS, LINGUIST_TEMPLATE

if TYPE_CHECKING:
    from .resourcefiledmaps import SimpleFieldMap

@dataclass
class Resource:
    pass

@dataclass
class Linguist(Resource):
    name: str
    email: str
    transrate: str
    qcrate: str
    notes: str
    feedback: str
    location: str
    languages: list[str] = field(default_factory=list)
    phone: str = field(init=False)
    code: str = field(init=False)
    fieldmaps: dict[str, "SimpleFieldMap"] = field(init=False)

    def __post_init__(self):
        self.name = self._cleanup_name(self.name)
        self.phone = ""
        self.fieldmaps = LINGUIST_MAPS
        self.qcrate = self.qcrate.strip()[:127]
        self.transrate = self.transrate.strip()[:127]
        self._set_code()
        self._cleanup_email()

    def _cleanup_name(self, name: str) -> str:
        name = name.strip()
        clean = ""
        in_para = False
        for char in name:
            if char == "(":
                in_para = True
            elif char == ")":
                in_para = False
            elif not in_para:
                clean += char
        return clean.strip()

    def _is_clean_name(self, name: str) -> bool:
        if len(name) == 2:
            return False
        if "(" in name or ")" in name:
            return False
        return True

    def _set_code(self):
        clean_name = self.name.replace(".", "").replace(",", "").replace("'", "").replace("\"", "").strip()
        split_name = clean_name.split(" ")
        clean_split_name = [part for part in split_name if self._is_clean_name(part)]
        if not clean_split_name:
            raise ValueError(f"Unable to generate code: {self.name}")
        try:
            if len(clean_split_name) < 2:
                self.code = clean_split_name[0].upper()
            elif len(clean_split_name) > 2:
                self.code = clean_split_name[0][:3].upper() + clean_split_name[0][0].upper() + clean_split_name[-1].upper()
            else:
                self.code = clean_split_name[0][:3].upper() + clean_split_name[1].upper()
        except IndexError:
            raise ValueError(f"Unable to split: {clean_name}")
        else:
            self.code = self.code[:8]

    def _cleanup_email(self):
        stripped_text = self.email.strip()
        email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
        phone_pattern = re.compile(r'(?<!\d)(\+\d{1,2}\s?)?1?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?![a-zA-Z0-9@])')
        is_phone = phone_pattern.search(stripped_text)
        is_email = email_pattern.search(stripped_text)
        if is_phone:
            self.phone = is_phone.group(0).strip()
        if is_email:
            self.email = is_email.group(0).strip()

    def _add_qualifications(self) -> dict[str, list[dict]]:
        # {
        #     "sch_resource_qual": [
        #         {
        #             "qualification_no": {
        #                 "qualification_desc": "German",
        #                 "qualification_no": 10
        #             },
        #             "resource_code": "AEL-SAYED"
        #         }
        #     ]
        # }
        self.languages = list(set(self.languages))
        qualifications = {}
        qualifications["sch_resource_qual"] = []
        dsp = 1
        for lang in self.languages:
            qual = resource_requests.query_qualifications({"qualification_desc": lang})
            if not qual:
                resource_requests.post_qualification({"qualification_desc": lang})
                qual = resource_requests.query_qualifications({"qualification_desc": lang})
                if not qual:
                    raise RuntimeError(f"Unable to add qualification: {lang}")
            qual_no = qual[0]["qualification_no"]
            qualifications["sch_resource_qual"].append({
                "dsp_seq": dsp,
                "qualification_no": {
                    "qualification_desc": lang,
                    "qualification_no": qual_no
                },
                "resource_code": self.code
            })
            dsp += 1
        return qualifications

    def post_new(self, jdict_only: bool = False) -> dict:
        jdict: dict[str, Any] = deepcopy(LINGUIST_TEMPLATE)
        for key in self.fieldmaps:
            value = getattr(self, key)
            if key == "languages":
                value = ";".join(value)
            jdict.update(self.fieldmaps[key].makejdict(value))
        jdict["resource_code"]["resource_code"] = self.code
        jdict.update(self._add_qualifications())
        if not jdict_only:
            resource_requests.post(jdict)
        return jdict