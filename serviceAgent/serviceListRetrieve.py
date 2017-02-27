import library.config.peachSharedConfig
import json
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import avro.schema
import avro.io
import io

def retrieve_service_list():
    return open(library.config.peachSharedConfig.get_service_temp_file(), "r").read()