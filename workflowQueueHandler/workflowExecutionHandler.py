import avro.schema
import io
from avro.io import DatumWriter
from kafka import KafkaProducer
import library.config.peachSharedConfig

def sendExecutionCustom(kafka_server_address, workflow_schema_path, kafka_topic, content):
    schema = avro.schema.parse(open(workflow_schema_path, "rb").read())

    producer = KafkaProducer(bootstrap_servers=kafka_server_address)
    topic = kafka_topic

    writer = avro.io.DatumWriter(schema)
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)

    writer.write(content, encoder)

    raw_bytes = bytes_writer.getvalue()
    print(raw_bytes)
    producer.send(topic, raw_bytes)

    producer.flush()

def sendExecution(worklow):
    kafka_server_address = library.config.peachSharedConfig.get_server_address("kafka")
    workflow_schema_path = library.config.peachSharedConfig.schema_file("workflow")
    kafka_topic = library.config.peachSharedConfig.get_event("sendWorkflow")
    content = worklow
    sendExecutionCustom(kafka_server_address, workflow_schema_path, kafka_topic, content)