import tarfile
import os
import mysql.connector
import time
import shutil


#TODO one day this should be in a kind of config too
mysql_info = {
    "host": "172.29.1.87",
    "user": "peach",
    "password": "peachuser",
    "database": "peach"
}

temp_locations = {
    "workflow_temp": "/home/henry/peach_temp_data/workflow_temp",
    "download_workflow_temp": "/home/henry/peach_temp_data/download_temp/workflows",
    "download_files_temp": "/home/henry/peach_temp_data/download_temp/files"
}

def grabIndex(many, idx):
    if isinstance(many, list):
        return many[int(idx)]
    elif idx == 0:
        return many
    else:
        return None

def from_uri(uri):
    #do stuff
    return "test"

def update_status(primary_key, status):
    try:
        cnx = mysql.connector.connect(**mysql_info)
        x = cnx.cursor()
        table = "queue"

        query = "UPDATE {} SET status='{}' WHERE id='{}'".format(table, status, primary_key)

        x.execute(query)
        cnx.commit()
    except Exception as e:
        #TODO handle errors somehow
        return

def update_end_time(primary_key):
    try:
        cnx = mysql.connector.connect(**mysql_info)
        x = cnx.cursor()
        table = "queue"
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        query = "UPDATE {} SET finished_date='{}' WHERE id='{}'".format(table, timestamp, primary_key)

        x.execute(query)
        cnx.commit()
    except Exception as e:
        #TODO handle errors somehow
        return

def update_progress(primary_key, progress):
    try:
        cnx = mysql.connector.connect(**mysql_info)
        x = cnx.cursor()
        table = "queue"

        query = "UPDATE {} SET progress='{}' WHERE id='{}'".format(table, progress, primary_key)

        x.execute(query)
        cnx.commit()
    except Exception as e:
        #TODO handle errors somehow
        return


def __get_current_temp_folder(primary_key):
    workflow_folder_relative = "workflow_" + str(primary_key)
    current_temp_directory = os.path.join(temp_locations["workflow_temp"], workflow_folder_relative)
    return current_temp_directory

def create_temp_folder(primary_key):
    current_temp_directory = __get_current_temp_folder(primary_key)    
    if not os.path.exists(current_temp_directory):
        os.makedirs(current_temp_directory)
    
def upload_output(primary_key):
    download_temp = temp_locations["download_files_temp"]
    new_filename = str(time.time()).replace(".", "") + "_workflow_" + str(primary_key) + ".tar"

    current_temp_directory = __get_current_temp_folder(primary_key)

    __create_tar(download_temp, new_filename, current_temp_directory)
    update_myqsl_tar(new_filename, primary_key)

def update_myqsl_tar(new_filename, primary_key):
    cnx = mysql.connector.connect(**mysql_info)
    x = cnx.cursor()
    table = "queue"

    query = "UPDATE {} SET output_file='{}' WHERE id='{}'".format(table, new_filename, primary_key)

    x.execute(query)
    cnx.commit()

def __create_tar(download_temp, new_filename, current_temp_directory):
    output = os.path.join(download_temp, new_filename)

    __make_tarfile(output, current_temp_directory)
    return new_filename

def __make_tarfile(output_filename, source_dir):

    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def make_available(c, all_files):
    print(c)
    temp_folder = __get_current_temp_folder(c[0])
    destinations = []
    for file in all_files:
        new_filename = file[1]
        local_filepath = file[0]
        new_filename = c[1] + "_" + new_filename
        destination = os.path.join(temp_folder, new_filename)
        shutil.copyfile(local_filepath, destination)
        destinations.append(destination)
    return destinations

def from_uri(uri):
    import library.storageHandler.storageHandler
    request = {
        "uri": uri,
        "action": "download",
        "connectionType": -1,
        "meta": []
    }
    response = library.storageHandler.storageHandler.get_response(request)
    print(response["response"])
    temp_file = response["response"]["tempPath"]
    download_temp = temp_locations["download_files_temp"]
    return os.path.join(download_temp, temp_file), temp_file.split("_", 1)[1]

def __log(c, msg, priority):
    priority_string = __priority_table(priority)
    full_msg = "[{}]({}): \"{}\"\n".format(c[1], priority_string, msg)
    temp_folder = __get_current_temp_folder(c[0])
    log_file = "{}.log".format(c[1])
    full_path = os.path.join(temp_folder, log_file)
    with open(full_path, "a") as c_file:
        c_file.write(full_msg)
    print full_msg

def info(c, msg):
    __log(c, msg, 0)

def warning(c, msg):
    __log(c, msg, 1)

def error(c, msg):
    __log(c, msg, 2)


def __priority_table(priority):
    ar = ["info", "warning", "error"]
    return ar[priority]