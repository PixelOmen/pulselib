from rosettapath import RosettaPath

if "mediapulse" not in RosettaPath.input_mount_patterns:
    RosettaPath.input_mount_patterns["mediapulse"] = r"^\\\\sanviewer"
    RosettaPath.input_mount_patterns["mediapulse_forward"] = r"^//sanviewer"
    RosettaPath.input_mount_patterns["mediapulse_noslash"] = r"^sanviewer"


from .src import utils
from .src import asset
from .src import errors
from .src.trx import trx_requests
from .src.asset import asset_requests
from .src.alert import alert_requests
from .src.resource.model import Linguist
from .src.fieldmaps import FieldTypeEnum
from .src.resource import resource_requests
from .src.alert.alert_requests import simple_alert
from .src.wo import wo_requests, WorkOrder, WOSource