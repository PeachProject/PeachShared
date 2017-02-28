from kafka import KafkaConsumer
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import avro.schema
import avro.io
import io
import argparse
import json

def start(kafka_address, event, tempFile, schema):
    """
    Will start a kafak consumer that regulary receives the "event" event and
    then fills in the "tempFile" with the json representation of the (with "schema" parsed) sent content.

    This will for example be needed for the service list update. But it can also be used for other temp file solutions.

    @param kafka_address The server address for the kafka server
    @param event the event / topic to listen for
    @param tempFile the file location to write the parsed json representation to
    @param schema the schema file with which the sent content should be parsed to serialize it to a json string
    """    
    consumer = KafkaConsumer(event, bootstrap_servers=kafka_address)
    schema = avro.schema.parse(open(schema).read())

    for msg in consumer:
        print("==> Updating the temporary service list file <==")
        
        bytes_raw = msg.value
        bytes_reader = io.BytesIO(bytes_raw)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(schema)
        allServices = []
        
        while True:
            #TODO: Check API if there is a better solution
            try:
                result = reader.read(decoder)
                allServices.append(result)
            except:
                break

        serialized = json.dumps(allServices, ensure_ascii=False)
        print(serialized)
        temp_file_real = open(tempFile, "w")
        temp_file_real.write(serialized)
        temp_file_real.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script should be used to start a kafka consumer that receives the service list and writes it into a temp folder.')
    parser.add_argument("-kafkaaddress", "--ka", type=str, help="The address to the kafka server that forwards the service list event.")
    parser.add_argument("-event", "--ev", type=str, help="The kafka topic to listen to. Probably 'Service_serviceListUpdated'")
    parser.add_argument("-tempfile", "--temp", help="This script will save the service list as json into a temp file. Where is this temp file?", type=str)
    parser.add_argument("-schema", "--s", help="Where can the script find the service schema?", type=str)
    args = parser.parse_args()
    start(args.ka, args.ev, args.temp, args.s)