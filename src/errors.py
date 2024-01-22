class AlertUncaughtError(Exception):
    def __init__(self, err: str):
        super().__init__(f"alert_requests: Uncaught error - {err}")


class AssetNotFoundError(Exception):
    def __init__(self, assetno: str):
        super().__init__(f"asset_requests: Asset not found: {assetno}")

class AssetUncaughtError(Exception):
    def __init__(self, assetid: str | dict, err: str):
        super().__init__(f"asset_requests: Uncaught error - {assetid} - {err}")

class AssetAudioUncaughtError(Exception):
    def __init__(self, assetid: str | dict, err: str):
        super().__init__(f"asset_requests: Uncaught error - {assetid} - {err}")

class AssetPathNotFoundError(LookupError):
    def __init__(self, origin: str) -> None:
        super().__init__(f"{origin}: unable to get filepath and/or filename")

class AssetRefreshError(LookupError):
    def __init__(self, mpulse_path: str) -> None:
        msg = f"Attemped to refresh non-existent asset: {mpulse_path}"
        super().__init__(msg)

class AssetExistsError(Exception):
    def __init__(self, path: str) -> None:
        super().__init__(f"Asset already exists: {path}")

class MultipleAssetsFoundError(Exception):
    def __init__(self, query: dict, assetdicts: list[dict]) -> None:
        self.assetdicts = assetdicts
        super().__init__(f"Multiple assets found: {query}")


class SessionNotFoundError(Exception):
    def __init__(self, session_no: str):
        super().__init__(f"session_requests: Session not found: {session_no}")

class SessionUncaughtError(Exception):
    def __init__(self, session_no: str | dict, err: str):
        super().__init__(f"session_requests: Uncaught error - {session_no} - {err}")


class ResourceUncaughtError(Exception):
    def __init__(self, res_no: str | dict, err: str):
        super().__init__(f"asset_requests: Uncaught error - {res_no} - {err}")

class ResourceExistsError(Exception):
    def __init__(self, res_no: str | dict, err: str):
        super().__init__(f"asset_requests: Asset exists - {res_no} - {err}")

class ResourceNotFoundError(Exception):
    def __init__(self, res_no: str):
        super().__init__(f"asset_requests: Asset not found: {res_no}")


class TRXUncaughtError(Exception):
    def __init__(self, trx: dict) -> None:
        self.trx = trx
        super().__init__(f"Invalid Transaction: {trx}")


class WorkOrderNotFoundError(Exception):
    def __init__(self, wo_num: str):
        super().__init__(f"wo_requests: Workorder not found: {wo_num}")

class WorkOrderUncaughtError(Exception):
    def __init__(self, wo_num: str | dict, err: str):
        super().__init__(f"wo_requests: Uncaught error - {wo_num} - {err}")


class JobNotFoundError(Exception):
    def __init__(self, job_num: str):
        super().__init__(f"job_requests: Job not found: {job_num}")

class JobUncaughtError(Exception):
    def __init__(self, job_num: str | dict, err: str):
        super().__init__(f"job_requests: Uncaught error - {job_num} - {err}")


class RosterUncaughtError(Exception):
    def __init__(self, query_or_no: str | dict, err: str):
        super().__init__(f"roster_requests: Uncaught error - {query_or_no} - {err}")
