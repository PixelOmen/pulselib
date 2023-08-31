import json

class WorkOrder:
    def __init__(self, jsondict: dict) -> None:
        self.jsondict = jsondict
        self._check_errors()
        try:
            self.wo_num = jsondict["wo_no_seq"]["wo_no_seq"]
            self.wo_po = jsondict["po"]
        except KeyError as e:
            jsonstr = json.dumps(self.jsondict, indent=4, sort_keys=True)
            raise LookupError("Unable to get key from jsondict:\n" + f"{str(e)}\n" + jsonstr)

    def _check_errors(self) -> None:
        if "error" in self.jsondict:
            raise LookupError(self.jsondict["error"])