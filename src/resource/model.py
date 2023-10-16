import re
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

from . import resource_requests
from .resourcefiledmaps import LINGUIST_MAPS

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
    language: list[str] = field(default_factory=list)
    phone: str = field(init=False)
    code: str = field(init=False)
    fieldmaps: dict[str, "SimpleFieldMap"] = field(init=False)

    def __post_init__(self):
        self.name = self.name.strip()
        self.phone = ""
        self.fieldmaps = LINGUIST_MAPS
        self._set_code()
        self._cleanup_email()

    def _set_code(self):
        split_name = self.name.split(" ")
        if len(split_name) < 2:
            self.code = self.name.upper()
        elif "(" in split_name[1]:
            self.code = split_name[0].upper()
        else:
            try:
                self.code = split_name[0][0].upper() + split_name[1].upper()
            except IndexError:
                raise ValueError(f"Unable to split: {self.name}")

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

    def post_new(self, jdict_only: bool = False) -> dict:
        jdict = {

        }
        if not jdict_only:
            resource_requests.post(jdict)
        return jdict