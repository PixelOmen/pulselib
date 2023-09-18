from dataclasses import dataclass

@dataclass
class Config:
    USERNAME: str = "xytech"
    PASSWORD: str = "Password1"
    TRX_QUERY_URL: str = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmTrxList"
    WO_URL = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmWorkOrder"
    WO_QUERY_URL = "http://xytechapp01:PORT/api/v1/database/DATABASE/JmWorkOrderList"
    ASSET_URL = "http://xytechapp01:PORT/api/v1/database/DATABASE/LibMaster"
    ASSET_QUERY_URL = "http://xytechapp01:PORT/api/v1/database/DATABASE/LibMasterList"
    ASSET_SESSION_URL = "http://xytechapp01:PORT/api/v1/database/DATABASE/LibMaster_ImSession_Related"
    MEDIAINFO_URL = "http://10.0.20.96:PORT/api/probe"
    MI_DEBUG: bool=False
    MP_DEBUG: bool=False
    MI_DEBUG_PORT = "4020"
    MI_LIVE_PORT = "80"
    MP_DEBUG_INFO = ("11001", "REI_TEST")
    MP_LIVE_INFO = ("11000", "REI_LIVE")

    @classmethod
    def init_urls(cls) -> None:
        mp_port = cls.MP_DEBUG_INFO[0] if cls.MP_DEBUG else cls.MP_LIVE_INFO[0]
        mp_db = cls.MP_DEBUG_INFO[1] if cls.MP_DEBUG else cls.MP_LIVE_INFO[1]
        mi_port = cls.MI_DEBUG_PORT if cls.MI_DEBUG else cls.MI_LIVE_PORT
        cls.TRX_QUERY_URL = cls.TRX_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        cls.WO_URL = cls.WO_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        cls.WO_QUERY_URL = cls.WO_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        cls.ASSET_URL = cls.ASSET_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        cls.ASSET_SESSION_URL = cls.ASSET_SESSION_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        cls.ASSET_QUERY_URL = cls.ASSET_QUERY_URL.replace("PORT", mp_port).replace("DATABASE", mp_db)
        cls.MEDIAINFO_URL = cls.MEDIAINFO_URL.replace("PORT", mi_port)

Config.init_urls()
CONFIG = Config()