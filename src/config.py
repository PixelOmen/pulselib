from dataclasses import dataclass

@dataclass
class Config:
    USERNAME: str = "xytech"
    PASSWORD: str = "Password1"
    TRX_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmTrxList"
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
    MEDIAINFO_URL: str = "http://10.0.20.96:PORT/api/probe"
    MI_DEBUG: bool = False
    MP_DEBUG: bool = False
    MI_DEBUG_PORT: str = "4020"
    MI_LIVE_PORT: str = "80"
    MP_DEBUG_INFO: tuple[str, str] = ("11001", "REI_TEST")
    MP_LIVE_INFO: tuple[str, str] = ("11000", "REI_LIVE")

    def __post_init__(self) -> None:
        mp_port = self.MP_DEBUG_INFO[0] if self.MP_DEBUG else self.MP_LIVE_INFO[0]
        mp_db = self.MP_DEBUG_INFO[1] if self.MP_DEBUG else self.MP_LIVE_INFO[1]
        mi_port = self.MI_DEBUG_PORT if self.MI_DEBUG else self.MI_LIVE_PORT
        self.TRX_QUERY_URL = self.TRX_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.WO_URL = self.WO_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.WO_QUERY_URL = self.WO_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.ASSET_URL = self.ASSET_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.ASSET_QUERY_URL = self.ASSET_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.ASSET_SESSION_URL = self.ASSET_SESSION_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.ASSET_SESSION_QUERY_URL = self.ASSET_SESSION_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.ALERT_URL = self.ALERT_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.RESOURCE_URL = self.RESOURCE_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.RESOURCE_QUERY_URL = self.RESOURCE_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.ROSTER_URL = self.ROSTER_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.ROSTER_QUERY_URL = self.ROSTER_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.SCHGROUP_URL = self.SCHGROUP_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.QUALIFICATION_URL = self.QUALIFICATION_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        self.MEDIAINFO_URL = self.MEDIAINFO_URL.replace("PORT", mi_port)

CONFIG = Config()