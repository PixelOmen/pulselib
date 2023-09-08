from typing import Any

class FieldTypeEnum:
    STRING = 0
    NUMBER = 1
    CHECKMARK = 2
    BUILTIN_ENUM = 3
    DICT = 4

    def __init__(self):
        raise NotImplementedError("FieldTypeEnum cannot be instantiated")

class SimpleFieldMap:
    def __init__(self, ftype: int, keys: Any, nestedcheckmark: bool=False, enumdict: dict[str, int]=...) -> None:
        if 0 > ftype > 4:
            raise ValueError(f"SimpleFieldMap: invalid ftype: {ftype}")
        if ftype == FieldTypeEnum.BUILTIN_ENUM and enumdict is ...:
            raise ValueError(f"SimpleFieldMap: BUILTIN_ENUM requires a enumdict")
        self.ftype = ftype
        self.keys = keys
        self.nestedcheckmark = nestedcheckmark
        self.enumdict = enumdict

    def read(self, jdict: dict[str, Any]) -> Any:
        match self.ftype:
            case FieldTypeEnum.STRING | FieldTypeEnum.NUMBER:
                return self._read_single(jdict)
            case FieldTypeEnum.CHECKMARK:
                value = self._read_single(jdict)
                return True if value == "Y" else False
            case FieldTypeEnum.DICT | FieldTypeEnum.BUILTIN_ENUM:
                return self._read_dict(jdict)
            case _:
                raise NotImplementedError(f"SimpleFieldMap.read: {self.ftype}")

    def write(self, value: Any) -> dict[str, Any]:
        match self.ftype:
            case FieldTypeEnum.STRING:
                return self._write_single(str(value))
            case FieldTypeEnum.NUMBER:
                parsedvalue = float(value)
                parsedvalue = int(parsedvalue) if parsedvalue.is_integer() else parsedvalue
                return self._write_single(parsedvalue)
            case FieldTypeEnum.CHECKMARK:
                if not isinstance(value, bool):
                    raise ValueError(f"SimpleFieldMap ftype of CHECKMARK requires a bool value: {value}")
                return self._write_single("Y" if value else "N")
            case FieldTypeEnum.BUILTIN_ENUM:
                return self._write_enum(value)
            case _:
                raise NotImplementedError(f"SimpleFieldMap.write: {self.ftype}") 
        
    def _read_single(self, jdict: dict[str, Any]) -> Any:
        if not isinstance(self.keys, str):
            raise ValueError(f"SimpleFieldMap key must be a string: {self.keys}")
        return jdict[self.keys]

    def _read_dict(self, jdict: dict[str, Any]) -> Any:
        if not isinstance(self.keys, list):
            raise ValueError(f"SimpleFieldMap key must be a list of strings: {self.keys}")
        if len(self.keys) < 2:
            raise ValueError(f"SimpleFieldMap ftype of dict needs at least 2 keys: {self.keys}")
        lastresult: Any = jdict[self.keys[0]]
        for key in self.keys[1:]:
            lastresult = lastresult[key]
        if self.nestedcheckmark:
            return True if lastresult == "Y" else False
        return lastresult
    
    def _write_single(self, value: Any, writekey: str=...) -> dict[str, Any]:
        key = writekey if writekey is not ... else self.keys
        if not isinstance(key, str):
            raise ValueError(f"SimpleFieldMap key must be a string: {key}")
        return {
            "op": "replace",
            "path": key,
            "value": value
        }
    
    def _write_enum(self, value: str) -> dict[str, Any]:
        if value not in self.enumdict:
            raise ValueError(f"SimpleFieldMap enum value not in enumdict: {value}")
        return self._write_single(self.enumdict[value], self.keys[0])