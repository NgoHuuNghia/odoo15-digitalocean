# -*- coding: utf-8 -*-
#? this __init__ file must import everything from module folder
from . import patient
from . import patient_tag
from . import appointment
from . import my_playground
#?115? model to learn about [_log_access] to remove base fields (Create, Write)
from . import operation
#?107? to enable ability for settings in the UI import the [res_config_settings] file from the fleet module
from . import res_config_settings