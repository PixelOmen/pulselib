class Config:
    USERNAME: str = "xytech"
    PASSWORD: str = "Password1"
    TRX_QUERY_URL: str = "http://xytechapp01:11000/api/v1/database/REI_LIVE/JmTrxList"
    WO_URL = "http://xytechapp01:11000/api/v1/database/REI_LIVE/JmWorkOrder"
    WO_QUERY_URL = "http://xytechapp01:11000/api/v1/database/REI_LIVE/JmWorkOrderList"
    ASSET_SESSION_URL = "http://xytechapp01:11000/api/v1/database/REI_LIVE/LibMaster_ImSession_Related"

CONFIG = Config()