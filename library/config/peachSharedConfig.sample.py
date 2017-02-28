##########################################
##########################################
###### MANDATORY CONFIG SETTINGS #########
##########################################
##########################################

schema_folder = "<PeachClient_Git_Repo>/PeachShared/schemas"

temp_locations = {
    "workflow_temp": "<peach_temp_data>/workflow_temp",
    "download_workflow_temp": "<peach_temp_data>/download_temp/workflows",
    "download_files_temp": "<peach_temp_data>/download_temp/files"
}

servers = {
    "kafka" : "<kafka_server>"
}

##########################################
##########################################
###### Secondary CONFIG SETTINGS #########
##########################################
##########################################

schema_files = {
    "service" : "serviceSchema.avsc",
    "queue": "queueItem.avsc",
    "workflow": "workflow.avsc"
}

events = {
    "serviceList" : "Service_serviceListUpdated",
    "sendWorkflow": "Worfklow_ExecuteWorkflow"
}

storage_modules = [
    "library.xnatAgent.xnatQuery"
]

method_names = {
    "response": "get_response",
    "initialRequest": "get_initial_request",
    "validUri": "valid_uri",
    "mandatoryActions": "get_mandatory_actions"
}


##########################################
##########################################
####### Don't change this part! ##########
##########################################
##########################################


def schema_file(id):
    return schema_folder + "/" + schema_files.get(id, "-")
    
def getTempFolder():
    return '<<<TEMP FOLDER>>>'


def get_server_address(id):
    return servers.get(id)


def get_event(id):
    return events.get(id)

def get_service_temp_file():
    return getTempFolder() + "/services.avro"

def get_ldap_server():
    return "ldap1.dkfz-heidelberg.de"

def get_default_method_name(key):
    return method_names[key]

def get_storage_module(connection_type):
    return storage_modules[connection_type]

def get_storage_modules():
    return storage_modules


def get_temp_location(temp_role):
    return temp_locations[temp_role]