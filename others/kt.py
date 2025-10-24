from kafka import KafkaProducer
from kafka import KafkaConsumer

producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('test-topic', b'Hello Kafka')
producer.flush()
print("Message sent")

consumer = KafkaConsumer(
    'kvs_updates',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    group_id='test-group'
)

print("waiting")
for message in consumer:
    print(f"Received: {message.value.decode()}")
    break  # stop after first message for test
