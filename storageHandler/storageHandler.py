from library.config.peachSharedConfig import get_default_method_name, get_storage_module, get_storage_modules
from importlib import import_module

def get_initial_request(connection):
    initial_request_method_name = get_default_method_name("initialRequest")
    current_module = get_storage_module(int(connection["type"]))

    mod = import_module(current_module)
    met = getattr(mod, initial_request_method_name)
    print(connection["connectionContent"])
    initial_request = met(connection["connectionContent"])
    initial_request["connectionType"] = int(connection["type"])
    return initial_request

def get_response(r):
    initial_request_method_name = get_default_method_name("response")
    mandatory_actions_method_name = get_default_method_name("mandatoryActions")
    if int(r["connectionType"]) < 0:
        r["connectionType"] = get_uri_origin(r["uri"])
        current_module = get_storage_module(int(r["connectionType"]))
        mod = import_module(current_module)
        specific_action = getattr(mod, mandatory_actions_method_name)()[r["action"]]
        r["action"] = specific_action
    else:
        current_module = get_storage_module(int(r["connectionType"]))
        mod = import_module(current_module)
    
    met = getattr(mod, initial_request_method_name)

    return met(r)

def is_temp_file(uri):
    #TODO
    return False

def get_uri_origin(uri):
    check_uri_method_name = get_default_method_name("validUri")
    for i in range(len(get_storage_modules())):
        c_storage_module = get_storage_modules()[i]
        mod = import_module(c_storage_module)
        met = getattr(mod, check_uri_method_name)
        if(met(uri)):
            return i
    return None

def request_download_file(uri):
    id = get_uri_origin(uri)
    mandatory_actions_method_name = get_default_method_name("mandatoryActions")
    current_module = get_storage_module(id)
    mod = import_module(current_module)

    met = getattr(mod, mandatory_actions_method_name)
    mandatory_actions = met()
    download_action = mandatory_actions["download"]
    
    request = {
        "connectionType": str(id),
        "action": download_action,
        "uri": uri,
        "meta": []
    }

    response = get_response(request)
    return response["response"]["contentURL"]