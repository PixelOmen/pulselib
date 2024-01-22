from dataclasses import dataclass

@dataclass
class Config:
    USERNAME: str = "xytech"
    PASSWORD: str = "Password1"
    MI_DEBUG: bool = False
    MI_DEBUG_PORT: str = "4020"
    MI_LIVE_PORT: str = "80"
    MP_DEBUG: bool = False
    MP_DEBUG_INFO: tuple[str, str] = ("11001", "REI_TEST")
    MP_LIVE_INFO: tuple[str, str] = ("11000", "REI_LIVE")
    MEDIAINFO_URL: str = "http://10.0.20.96:PORT/api/probe"
    TRX_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmTrxList"
    JOB_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmJob"
    JOB_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmJobList"
    WO_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmWorkOrder"
    WO_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmWorkOrderList"
    ASSET_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/LibMaster"
    ASSET_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/LibMasterList"
    ASSET_SESSION_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/LibMaster_ImSession_Related"
    ASSET_SESSION_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/ImSessionLibMasterList"
    ALERT_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/XeAlert"
    RESOURCE_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/SchResource"
    RESOURCE_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/SchResourceList"
    ROSTER_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/SchRosterTimeOff"
    ROSTER_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/SchRosterTimeOffList"
    SCHGROUP_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/SchGroup"
    QUALIFICATION_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/SchQualification"
    SALES_OFFICE_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmSalesOffice"

    def __post_init__(self) -> None:
        mp_port = self.MP_DEBUG_INFO[0] if self.MP_DEBUG else self.MP_LIVE_INFO[0]
        mp_db = self.MP_DEBUG_INFO[1] if self.MP_DEBUG else self.MP_LIVE_INFO[1]
        mi_port = self.MI_DEBUG_PORT if self.MI_DEBUG else self.MI_LIVE_PORT
        self.MEDIAINFO_URL = self.MEDIAINFO_URL.replace("PORT", mi_port)
        for k,v in self.__dict__.items():
            if not isinstance(v, str):
                continue
            splitname = k.split("_")
            if splitname[-1] == "URL" and splitname[0] != "MEDIAINFO":
                newvalue = v.replace("PORT", mp_port).replace("DATABASE", mp_db)
                setattr(self, k, newvalue)

CONFIG = Config()