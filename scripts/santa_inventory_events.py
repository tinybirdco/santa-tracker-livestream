import click
import json
import ndjson
from datetime import datetime
import random
import requests
import random
import csv
from time import sleep
from confluent_kafka import Producer

CONFLUENT_SERVER = 'your-confluent-server'
CONFLUENT_KEY = 'your-confluent-key'
CONFLUENT_SECRET = 'your-confluent-secret'


def restock_inventory(uuids, state):
    print("Restocking with 50 to 500 of each toy")
    data_list = []
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Add between 50 and 500 of each toy
    for toy_id in uuids:

        data = {
            'toy_id': toy_id,
            'timestamp': timestamp,
            'inventory': random.randint(50, 500)
        }

        data_list.append(data)

        state[toy_id] = {
            'inventory': data['inventory']
        }

    return data_list


def increment_inventory(state, speed):

    total_inventory = sum(value['inventory'] for key, value in state.items())
    if not state or total_inventory == 0:
        print("No existing inventory. Please use --restock to restock Santa's inventory")
        return
    data_list = []
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Randomly choose between 5 and 100 toys to subtract state
    kid_count = random.randint(100, 300) * speed

    for _ in range(kid_count):

        available_toys = [key for key,
                          value in state.items() if value['inventory'] > 0]
        toy_id = random.choice(available_toys)

        data = {
            'toy_id': toy_id,
            'timestamp': timestamp,
            'inventory': state[toy_id]['inventory'] - 1
        }
        data_list.append(data)

        state[toy_id]['inventory'] -= 1

    return data_list


def drop_inventory(uuids, state):
    print("Dropping all inventory")
    data_list = []
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Set inventory to 0 for all toys
    for toy_id in uuids:

        data = {
            'toy_id': toy_id,
            'timestamp': timestamp,
            'inventory': 0
        }

        data_list.append(data)

        state[toy_id] = {
            'inventory': 0
        }

    return data_list


def get_state_from_tinybird():

    with open('../data-project/.tinyb') as tinyb:
        tinyb_data = json.load(tinyb)
        TB_HOST = tinyb_data['host']
        TB_TOKEN = tinyb_data['token']

    params = {
        'token': TB_TOKEN
    }

    url = f'{TB_HOST}/v0/pipes/santa_current_inventory.json'
    response = requests.get(url, params=params)

    json_data = response.json()['data']

    state = {item['toy_id']: {'inventory': item['inventory']}
             for item in json_data}

    return state


def send_to_confluent(producer, data):
    for row in data:
        producer.produce("santa_inventory_cdc", value=json.dumps(row))
    producer.flush()
    print(f'Sent {len(data)} rows to Confluent')


def create_kafka_producer():
    # Required connection configs for Kafka producer, consumer, and admin
    config = {
        'bootstrap.servers': CONFLUENT_SERVER,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': CONFLUENT_KEY,
        'sasl.password': CONFLUENT_SECRET
    }

    return Producer(config)


def send_to_tinybird(data):
    print(f'Sending {len(data)} rows to Tinybird')

    # Get Tinybird host and token from .tinyb files
    with open('../data-project/.tinyb') as tinyb:
        tinyb_data = json.load(tinyb)
        TB_HOST = tinyb_data['host']
        TB_TOKEN = tinyb_data['token']

    # Send data to Tinybird Events API
    r = requests.post(f'{TB_HOST}/v0/events',
                      params={
                          'name': 'santa_inventory_cdc_test',
                          'token': TB_TOKEN
                      },
                      data=ndjson.dumps(data))

    # Print response
    print(r.status_code)
    print(r.text)


@click.command
@click.option('--restock', is_flag=True, help='Triggers a restock to add inventory to Santa')
@click.option('--drop', is_flag=True, help='Triggers a drop to remove all inventory from Santa')
@click.option('--speed', default=1, help='The rate at which Santa inventory depletes.')
def generate(restock, drop, speed):

    uuids = []
    producer = create_kafka_producer()

    # Get UUIDs from local toy list
    with open('toys.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            try:
                uuids.append(row[0].strip())  # Parse and append ID as UUID
            except ValueError:
                print(f"Error parsing ID '{row[0]}': invalid UUID")

        # Try to get state from Tinybird API
        try:
            state = get_state_from_tinybird()
        except:
            print("Could not fetch state from Tinybird API")
            # Initialize an empty state
            state = {}

        if restock:
            data = restock_inventory(uuids, state)
            if data:
                send_to_confluent(producer, data)

        elif drop:
            data = drop_inventory(uuids, state)
            if data:
                send_to_confluent(producer, data)
        else:
            while True:
                data = increment_inventory(state, speed)
                sleep(1)
                # send_to_tinybird(data)
                if data:
                    send_to_confluent(producer, data)
                else:
                    break


generate()
