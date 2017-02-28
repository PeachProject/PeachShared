import library.config.peachSharedConfig
import os.path


def get_schema(theSchema):
    endPath = library.config.peachSharedConfig.schema_file(theSchema)
    if os.path.isfile(endPath): 
        with open(endPath, 'r') as myfile:
            data=myfile.read().replace('\n', '')
    else:
        data = ""
    return data