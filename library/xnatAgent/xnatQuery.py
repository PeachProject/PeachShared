from pyxnat import Interface
import argparse
import json
import time
import hashlib
from library.config.peachSharedConfig import get_temp_location

def valid_uri(uri_json):
    """
    Evalutes a given uri and returns if it can handle the uri
    @param uri_json uri as json to be evaluted
    @return true if the uri can be handled by this module
    """
    return URI.from_json(uri_json).is_valid()

def get_mandatory_actions():
    actions_dict = {
        "download" : "view"
        }
    return actions_dict

def get_initial_response(user, password, server, root):
    """
    Creates the initial response
    @param user as string
    @param password as string
    @param server as string (e.g. http://localhost:8080/xnat)
    @param root as string, entry point to xnat (e.g. /projects/projectname)
    @return response as dict
    """
    connection_dict = { "user" : user, "password" : password, "server" : server, "root" : root }
    initial_request = get_initial_request(connection_dict)
    return get_response(initial_request)

def get_initial_request(connection_dict):
    """
    Creates the initial request
    @param connection_dict as dict containing user, password, server
    @return request as dict
    """
    user = connection_dict.get("user")
    password = connection_dict.get("password")
    server = connection_dict.get("server")
    action = "open"
    meta = []
    root = connection_dict.get("root")
    if root == "" or root == "/":
        root = "/projects"
    return Request(user, password, server, action, meta, root).as_dict()

def get_response(request_dict):
    """
    Returns a response
    @param request_dict as dict containing action, uri, meta
    uri is something that is generated in the initial request by this and can be parsed by this
    @return a Response
    """
    action = request_dict.get("action")
    uri = request_dict.get("uri")
    meta = request_dict.get("meta")
    if Actions().is_valid_action(action):
        return getattr(Actions(), "do_action")(action, uri, meta).as_dict()
    else:
        return ErrorResponse(0, "I'm an incapable developer who has no idea what he is doing. Sorry.").as_dict()

def unique_string(something):
    """
    Creates a unique string that is intended to be used as prefix for files written locally
    @param something that can be hashed
    @return a string
    """
    return str(hashlib.sha256(something).hexdigest()) + str(time.time()).replace(".", "")

def as_local_filepath(filename, something_to_hash):
    something_unique = unique_string(something_to_hash)
    abs_path = get_temp_location("download_files_temp")
    temp_filename = something_unique + "_" + filename
    local_file_path = abs_path + "/" + temp_filename
    return local_file_path, temp_filename

def get_extension(filename):
    name_split = filename.split(".")
    if len(name_split) > 1:
         return name_split[-1]
    else:
        return None

class Meta:
    def __init__(self, meta_arr):
        self.meta_arr = meta_arr
    
    def get_value(self, key):
        for m in self.meta_arr:
            if m.get("key") == key:
                return m.get("value")
        return None

class Response:
    def __init__(self):
        self.response = None

    def as_json(self):
        return json.dumps(self.response)

    def as_dict(self):
        return self.response

class ErrorResponse(Response):
    def __init__(self, error_code, error_message):
        Response.__init__(self)
        self.response = {
            "type" : 2,
            "response": {
                "errorCode" : error_code,
                "errorMsg" : error_message
            }
        }

class ContentResponse(Response):
     def __init__(self, temp_filename, overwrite_action, uri):
        Response.__init__(self)
        self.response = {
            "type" : 1,
            "response": {
                "tempPath" : temp_filename,
                "overwriteAction" : overwrite_action,
                "uri" : uri,
                "extension" : get_extension(temp_filename)
            }
        }

class StorageItemsResponse(Response):
    def __init__(self, storage_items, current_uri, actions, hierarchy):
        Response.__init__(self)
        self.response = {
            "type" : 0,
            "response": {
                "storageItems" : storage_items,
                "currentURI" : current_uri,
                "actions" : actions,
                "hierarchy" : hierarchy
            }
        }

class StorageItem:
    def __init__(self, stype, uri, rights, name):
            self.item = {
                "type" : stype,
                "uri" : uri,
                "rights" : rights,
                "name" : name
            }
            self.__init_extension()

    def __init_extension(self):
        self.item["extension"] = get_extension(self.item["name"])

    def as_json(self):
        return json.dumps(self.item)

    def as_dict(self):
        return self.item
    
    def __str__(self):
        rights = ""
        for r in self.item.get("rights")[:-1]:
            rights += r + ", "
        else:
            rights += self.item.get("rights")[-1]
        return self.item.get("type") + " " + self.item.get("uri") + " " + rights + " " + self.item.get("name")

class Action:
    def __init__(self, name):
        self.name = name

    def get_response(self, uri_json, meta):
        uri_dict = URI.from_json(uri_json).as_dict()
        return self.execute(uri_dict, meta)

class XNATDBOperator(Action):
    def __init__(self, name, mode):
        Action.__init__(self, name)
        self.mode = mode
        
    def execute(self, uri_dict, meta):
        return getattr(self, self.mode)(uri_dict, meta)
 
    def delete(self, uri_dict, meta):
        xnat_data = XNATConnection(uri_dict.get("user"), uri_dict.get("password"), uri_dict.get("server")).select(uri_dict.get("root"))
        print xnat_data
        print dir(xnat_data)
        if xnat_data.exists():
            xnat_data.delete()
            return XNATNavigator("XNATNavigator", "parent").get_response(URI.from_dict(uri_dict).as_json(), meta)
        else:
            #TODO Error code
            return ErrorResponse(0, "Tried to delete none existing data.\nYou may want to check if the actions are displayed and set properly or the data has been deleted by another process.")       

    def upload(self, uri_dict, meta):
        meta_obj = Meta(meta)
        filename = meta_obj.get_value("filename")
        if filename is None:
            return ErrorResponse(0, "Given meta data is faulty. No filename given.")
        uri_dict["root"] = uri_dict.get("root") + "/files/" + filename
        try:
           self.__upload_file(uri_dict, meta)
        except Exception as e:
            return ErrorResponse(0, "We are sorry but the file you wanted to store could not be stored.\nDetails:{}".format(str(e)))  
        return XNATNavigator("XNATNavigator", "parent").get_response(URI.from_dict(uri_dict).as_json(), meta)
    
    def __upload_file(self, uri_dict, meta):
        xnat_path = uri_dict.get("root")
        xnat_data = XNATConnection(uri_dict.get("user"), uri_dict.get("password"), uri_dict.get("server")).select(xnat_path)
        meta_obj = Meta(meta)
        content = meta_obj.get_value("content")
        local_filepath, temp_filename = as_local_filepath(xnat_path.split("/")[-1], xnat_path)
        #TODO Currently we assume that we will get a string
        with open(local_filepath, "w") as local_file:
            local_file.write("{}".format(content))
        xnat_data.insert(local_filepath, overwrite=True)
        return temp_filename
    
    def upload_file(self, uri_dict, meta):
        try:
           return ContentResponse(self.__upload_file(uri_dict, meta), "upload_file", URI.from_dict(uri_dict).as_json())
        except Exception as e:
            return ErrorResponse(0, "We are sorry but the file you wanted to store could not be stored.\nDetails:{}".format(str(e)))

class XNATDownloader(Action):
    def __init__(self, name):
        Action.__init__(self, name)
    
    def execute(self, uri_dict, meta):
        return getattr(self, "download")(uri_dict, meta)
    
    def download(self, uri_dict, meta):
        xnat_path = uri_dict.get("root")
        keyword =  xnat_path[1:len(xnat_path)].split("/")[-2]
        xnat_data = XNATConnection(uri_dict.get("user"), uri_dict.get("password"), uri_dict.get("server")).select(xnat_path)
        overwrite_action = "upload_file"
        if keyword == "resources":
            return ContentResponse(self.__download_resource(xnat_data, xnat_path), overwrite_action, URI.from_dict(uri_dict).as_json())           
        elif keyword == "files":
            return ContentResponse(self.__download_file(xnat_data, xnat_path), overwrite_action, URI.from_dict(uri_dict).as_json())
        else:
            #TODO Error code
            return ErrorResponse(0, "Action view/download called for invalid selection.")

    def __download_resource(self, xnat_data, xnat_path):
        filepath_download_location = xnat_data.get(get_temp_location("download_files_temp"))
        filename = filepath_download_location[1:len(filepath_download_location)].split("/")[-1]
        local_filepath_target, temp_filename = as_local_filepath(filename, xnat_path)
        import os
        os.rename(filepath_download_location, local_filepath_target)
        return temp_filename

    def __download_file(self, xnat_data, xnat_path):
        filename = xnat_path[1:len(xnat_path)].split("/")[-1]
        local_filepath, temp_filename = as_local_filepath(filename, xnat_path)
        xnat_data.get_copy(local_filepath)
        return temp_filename

class XNATNavigator(Action):
    """
    Class that is able to navigate forwards and backwards in an xnat hierarchy
    """
    def __init__(self, name, mode):
        """
        Creates an instance of this class.
        @param name a human readable name
        @param mode allowed modes are "parent" or "open"
        """
        Action.__init__(self, name)
        self.mode = mode 
        self.__global_type = {
            "None" : "file",
            "xnat:abstractResource" : "folder",
            "xnat:projectData" : "project",
            "xnat:subjectData" : "subject",
            "xnat:ctSessionData" : "stack",
            "xnat:ctScanData" : "image_stack"
        }
    
    def __copy_uri_append_sub_to_root(self, uri_dict, subfolder):
         uri_dict_copy = uri_dict.copy()
         uri_dict_copy["root"] = uri_dict.get("root") + "/" + subfolder
         return URI.from_dict(uri_dict_copy)
        
    def __copy_uri_replace_root(self, uri_dict, replaced_root):
        uri_dict_copy = uri_dict.copy()
        uri_dict_copy["root"] = replaced_root
        return URI.from_dict(uri_dict_copy)
    
    def __parse_hierarchy(self, path):
        return path[1:len(path)].split("/")

    def collection_storage_items(self, xnat_collection, uri_dict, peach_type, peach_actions):
        items = []
        #TODO detrmine rights and set them properly
        for element in xnat_collection:
            resource_sub_id = ""
            if peach_type is not None:
                resource_sub_id = peach_type + "/"
            resource_sub_id = resource_sub_id + element.id()
            items.append(StorageItem(self.__global_type.get(str(element.datatype())), self.__copy_uri_append_sub_to_root(uri_dict, resource_sub_id).as_json(), peach_actions, element.label()).as_dict())
        return items

    def open(self, uri_dict, meta):
        data = XNATConnection(uri_dict.get("user"), uri_dict.get("password"), uri_dict.get("server")).select(uri_dict.get("root"))
        storage_items = []
        try:
            if not hasattr(data, '__iter__'):
                files = []
                resources = []
                subjects = []
                if hasattr(data, "files"):        
                    storage_items = storage_items + self.collection_storage_items(data.files(), uri_dict, "files", ["view", "delete"])
                if hasattr(data, "resources"):
                    storage_items = storage_items + self.collection_storage_items(data.resources(), uri_dict, "resources", ["open", "delete", "view"])
                if hasattr(data, "subjects"):
                    storage_items = storage_items + self.collection_storage_items(data.subjects(), uri_dict, "subjects", ["open", "delete"])
                if type(data).__name__ == "Subject":
                    if hasattr(data, "experiments"):
                        storage_items = storage_items + self.collection_storage_items(data.experiments(), uri_dict, "experiments", ["open", "delete"])
                if hasattr(data, "scans"):
                    storage_items = storage_items + self.collection_storage_items(data.scans(), uri_dict, "scans", ["open", "delete"])     
            else:
                storage_items = storage_items + self.collection_storage_items(data, uri_dict, None, ["open", "delete"])            
            return StorageItemsResponse(storage_items, URI.from_dict(uri_dict).as_json(), ["parent", "upload"], self.__parse_hierarchy(uri_dict.get("root")))
        except Exception as e:
            #TODO meaningful error code
            return ErrorResponse(0, str(e))
    
    def __build_parent_uri(self, uri_dict):
        """
        Creates an uri that is on one level lower than the given one (e.g. /projects/yourproject -> /projects)
        @param uri_dict as dict
        @return a new uri as uri dict with a differing root
        """
        root_arr = self.__parse_hierarchy(uri_dict.get("root"))
        blacklist = ["resources", "subjects", "experiments", "scans", "files"]
        del root_arr[-1]
        if root_arr and root_arr[-1] in blacklist:
            del root_arr[-1]
        parent_root = "/"
        if not root_arr:
            #In case this might happen for some odd reason
            parent_root = parent_root + "projects"
        else:
            parent_root = parent_root + "/".join(root_arr)
        return self.__copy_uri_replace_root(uri_dict, parent_root).as_dict()

    def parent(self, uri_dict, meta):
        try:
            return self.open(self.__build_parent_uri(uri_dict), meta)
        except Exception as e:
            #TODO meaningful error code
            return ErrorResponse(0, str(e))

    def execute(self, uri_dict, meta):
        return getattr(self, self.mode)(uri_dict, meta)   

class URI():
    def __init__(self, user, password, server, root):
        self.user = user
        self.password = password
        self.server = server
        self.root = root

    @classmethod
    def from_json(cls, uri_json):
        return cls.from_dict(json.loads(uri_json))
    
    @classmethod
    def from_dict(cls, uri_dict):
        return cls(uri_dict.get("user"), uri_dict.get("password"), uri_dict.get("server"), uri_dict.get("root"))
    
    def as_dict(self):
        return {
            "user" : self.user,
            "password" : self.password,
            "server" : self.server,
            "root" : self.root
            }

    def as_json(self):
        return json.dumps(self.as_dict())

    def __str__(self):
        return self.user + " " + self.password + " " + self.server + " " + self.root
    
    def is_valid(self):
        return self.user is not None and self.password is not None and self.server is not None and self.root is not None

class Request():
    def __init__(self, user, password, server, action, meta, root):
        self.meta = meta
        self.action = action
        self.uri = URI(user, password, server, root).as_json()
    
    def as_dict(self):
        return {
            "action" : self.action,
            "uri" : self.uri,
            "meta" : self.meta
        }
    
    def as_json(self):
        return json.dumps(self.as_dict())

class Actions:
    def __init__(self):
        self.actions = ["open", "parent", "view", "delete", "upload", "upload_file"]     
         
    def is_valid_action(self, action):
        return action in self.actions and hasattr(self, action)

    def do_action(self, action, uri_json, meta):
        return getattr(self, action)(uri_json, meta)

    def open(self, uri_json, meta):
        return XNATNavigator("XNATNavigator", "open").get_response(uri_json, meta)
    
    def parent(self, uri_json, meta):
        return XNATNavigator("XNATNavigator", "parent").get_response(uri_json, meta)
    
    def delete(self, uri_json, meta):
        return XNATDBOperator("XNATDBOperator", "delete").get_response(uri_json, meta)
    
    def view(self, uri_json, meta):
        if not URI.from_json(uri_json).is_valid():
            #TODO error code
            return ErrorResponse(0, "The entered URI is not valid.").as_dict()
        else:
            return XNATDownloader("Downloader").get_response(uri_json, meta)
     
    def upload(self, uri_json, meta):
        return XNATDBOperator("XNATDBOperator", "upload").get_response(uri_json, meta)
    
    def upload_file(self, uri_json, meta):
        return XNATDBOperator("XNATDBOperator", "upload_file").get_response(uri_json, meta)

class XNATConnection:
    def __init__(self, user, password, server):
        self.connection = None
        self.user = user
        self.password = password
        self.server = server

    def __del__(self):
        if self.connection is not None:
            self.connection.disconnect()
    def __connect(self):
        if self.connection == None:
                    self.connection = Interface(
                            server = self.server,
                            user = self.user,
                            password = self.password,
                            cachedir = '/tmp'
                            )
        return self.connection

    def select(self, xnat_path):
        return self.__connect().select(xnat_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connects to xnat and does stuff.')
    parser.add_argument('-s', '--server', type=str, help="Xnat server")
    parser.add_argument('-u', '--user', type=str, help="User")
    parser.add_argument('-p','--password', type=str, help="Password")
    parser.add_argument('-r', '--root_dir', type=str, help="Root dir")
    args = parser.parse_args()
    response = get_initial_response(args.user, args.password, args.server, args.root_dir)
    print "__main__", response