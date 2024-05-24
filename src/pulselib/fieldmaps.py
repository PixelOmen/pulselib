from typing import Any

class FieldTypeEnum:
    STRING = 0
    NUMBER = 1
    CHECKMARK = 2
    MPULSE_ENUM = 3
    DICT = 4
    LIST = 5

    def __init__(self):
        raise NotImplementedError("FieldTypeEnum cannot be instantiated")

    @classmethod
    def name(cls, value: int) -> str:
        for k, v in cls.__dict__.items():
            if v == value:
                return k
        return ""

class SimpleFieldMap:
    def __init__(self, name: str, ftype: int, keys: Any, nestedcheckmark: bool=False, enumdict: dict[str, int] | None = None) -> None:
        if 0 > ftype > 4:
            raise ValueError(f"SimpleFieldMap: invalid ftype: {ftype}")
        if ftype == FieldTypeEnum.MPULSE_ENUM and enumdict is None:
            raise ValueError(f"SimpleFieldMap: BUILTIN_ENUM requires a enumdict")
        self.name = name
        self.ftype = ftype
        self.keys = keys
        self.nestedcheckmark = nestedcheckmark
        self.enumdict = enumdict if enumdict is not None else {}

    def read(self, jdict: dict[str, Any]) -> Any:
        match self.ftype:
            case FieldTypeEnum.STRING | FieldTypeEnum.NUMBER | FieldTypeEnum.LIST:
                return self._read_single(jdict)
            case FieldTypeEnum.CHECKMARK:
                value = self._read_single(jdict)
                return True if value == "Y" else False
            case FieldTypeEnum.DICT | FieldTypeEnum.MPULSE_ENUM:
                return self._read_dict(jdict)
            case _:
                raise NotImplementedError(f"SimpleFieldMap.read: {self.ftype}")

    def patch_op(self, value: Any) -> dict[str, Any]:
        match self.ftype:
            case FieldTypeEnum.STRING:
                return self._patch_single(str(value))
            case FieldTypeEnum.NUMBER:
                parsedvalue = float(value)
                parsedvalue = int(parsedvalue) if parsedvalue.is_integer() else parsedvalue
                return self._patch_single(parsedvalue)
            case FieldTypeEnum.CHECKMARK:
                if not isinstance(value, bool):
                    raise ValueError(f"SimpleFieldMap ftype of CHECKMARK requires a bool value: {value}")
                return self._patch_single("Y" if value else "N")
            case FieldTypeEnum.MPULSE_ENUM:
                return self._patch_enum(value)
            case FieldTypeEnum.DICT:
                return self._patch_single(value, self.keys[0])
            case _:
                raise NotImplementedError(f"SimpleFieldMap.patch: {self.ftype}")

    def makejdict(self, value: Any) -> dict[str, Any]:
        match self.ftype:
            case FieldTypeEnum.STRING | FieldTypeEnum.NUMBER | FieldTypeEnum.LIST:
                return self._jdict_single(value)
            case FieldTypeEnum.CHECKMARK:
                return self._jdict_single("Y" if value else "N")
            case FieldTypeEnum.DICT:
                return self._jdict_dict(value)
            case FieldTypeEnum.MPULSE_ENUM:
                return self._jdict_enum(value)
            case _:
                raise NotImplementedError(f"SimpleFieldMap.jdict_op: {self.ftype}")
        
    def _read_single(self, jdict: dict[str, Any]) -> Any:
        if not isinstance(self.keys, str):
            raise ValueError(f"SimpleFieldMap key must be a string: {self.keys}")
        return jdict[self.keys]

    def _read_dict(self, jdict: dict[str, Any]) -> Any:
        if not isinstance(self.keys, list):
            raise ValueError(f"SimpleFieldMap key must be a list of strings: {self.keys}")
        if len(self.keys) < 2:
            raise ValueError(f"SimpleFieldMap ftype of dict needs at least 2 keys: {self.keys}")
        try:
            lastresult: Any = jdict[self.keys[0]]
            for key in self.keys[1:]:
                lastresult = lastresult[key]
        except (KeyError, TypeError):
            return None
        if self.nestedcheckmark:
            return True if lastresult == "Y" else False
        return lastresult
    
    def _patch_single(self, value: Any, writekey: str | None = None) -> dict[str, Any]:
        key = writekey if writekey is not None else self.keys
        if not isinstance(key, str):
            raise ValueError(f"SimpleFieldMap key must be a string: {key}")
        return {
            "op": "replace",
            "path": key,
            "value": value
        }
    
    def _patch_enum(self, value: str) -> dict[str, Any]:
        if value not in self.enumdict:
            raise ValueError(f"SimpleFieldMap - {self.name} - enum value not in enumdict: {value}")
        return self._patch_single(self.enumdict[value], self.keys[0])

    def _jdict_single(self, value: Any, writekey: str | None = None) -> dict[str, Any]:
        key = writekey if writekey is not None else self.keys
        if not isinstance(key, str):
            raise ValueError(f"SimpleFieldMap key must be a string: {key}")
        return {key: value}

    def _jdict_dict(self, value: Any) -> dict[str, Any]:
        if not isinstance(self.keys, list):
            raise ValueError(f"SimpleFieldMap key must be a list of strings: {self.keys}")
        if len(self.keys) < 2:
            raise ValueError(f"SimpleFieldMap ftype of dict needs at least 2 keys: {self.keys}")
        lastresult = {self.keys[-1]: value}
        # backwards loop
        for key in reversed(self.keys[:-1]):
            lastresult = {key: lastresult}
        return lastresult

    def _jdict_enum(self, value: Any) -> dict[str, Any]:
        if not isinstance(self.keys, list):
            raise ValueError(f"SimpleFieldMap key must be a list of strings: {self.keys}")
        if not value:
            return self._jdict_single("", self.keys[0])
        if value not in self.enumdict:
            raise ValueError(f"SimpleFieldMap - {self.name} - enum value not in enumdict: {value}")
        return self._jdict_single(self.enumdict[value], self.keys[0])