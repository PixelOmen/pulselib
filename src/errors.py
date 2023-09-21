class AlertUncaughtError(Exception):
    def __init__(self, err: str):
        super().__init__(f"alert_requests: Uncaught error - {err}")


class AssetNotFoundError(Exception):
    def __init__(self, assetno: str):
        super().__init__(f"asset_requests: Asset not found: {assetno}")

class AssetUncaughtError(Exception):
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
