import rosettapath

if "mediapulse" not in rosettapath.INPUT_MOUNT_PATTERNS:
    rosettapath.INPUT_MOUNT_PATTERNS["mediapulse"] = r"^\\\\sanviewer"
    rosettapath.INPUT_MOUNT_PATTERNS["mediapulse_forward"] = r"^//sanviewer"
    rosettapath.INPUT_MOUNT_PATTERNS["mediapulse_noslash"] = r"^sanviewer"

from rosettapath import RosettaPath

from .src import utils
from .src import asset
from .src import errors
from .src.trx import trx_requests
from .src.asset import asset_requests
from .src.alert import alert_requests
from .src.alert.alert_requests import simple_alert
from .src.wo import wo_requests, WorkOrder, WOSource
from .src.fieldmaps import FieldTypeEnum