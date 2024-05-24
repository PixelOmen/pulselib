from rosettapath import RosettaPath

if "mediapulse" not in RosettaPath.input_mount_patterns:
    RosettaPath.input_mount_patterns["mediapulse"] = r"^\\\\sanviewer"
    RosettaPath.input_mount_patterns["mediapulse_forward"] = r"^//sanviewer"
    RosettaPath.input_mount_patterns["mediapulse_noslash"] = r"^sanviewer"


from .import utils, asset, errors
from .trx import trx_requests
from .asset import asset_requests
from .alert import alert_requests
from .resource.model import Linguist
from .fieldmaps import FieldTypeEnum
from .resource import resource_requests
from .alert.alert_requests import simple_alert
from .job import job_requests
from .wo import wo_requests, WorkOrder, WOSource
from .roster import roster_requests, RosterTimeOff