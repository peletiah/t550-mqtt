import json
import time

import paho.mqtt.client as mqtt

from read_meter import read_heat_meter

OBIS_descriptions = {
    '6.8': {'metric': 'meter_reading', 'name': 'Zählerstand', 'unit': 'kWh', 'device_class': 'energy', 'multiplier': 1000},
    '6.8*01': {'metric': 'meter_reading_2', 'name': 'Zählerstand 2', 'unit': 'kWh', 'device_class': 'energy', 'multiplier': 1000},
    '6.6': {'metric': 'max_heat_output', 'name': 'Max. Heizleistung', 'unit': 'kW', 'device_class': 'energy'},
    '6.26': {'metric': 'throughput', 'name': 'Durchfluss', 'unit': 'm³', 'device_class': 'gas'},
    '6.33': {'metric': 'max_throughput', 'name': 'Max. Durchfluss', 'unit': 'm³/h', 'device_class': 'gas'},
    '9.4': {'metric': 'max_temp_forward_return_flow', 'name': 'Max. Vorlauf-/Rücklauftemperatur',
            'unit': '°C', 'device_class': 'temperature'},
    '6.31': {'metric': 'operating_hours', 'name': 'Betriebsstunden', 'unit': 'h', 'device_class': 'timestamp'},
    '6.32': {'metric': 'downtime', 'name': 'Stillstand', 'unit': 'h', 'device_class': 'timestamp'},
    '9.31': {'metric': 'flowhours', 'name': 'Durchflussstunden', 'unit': 'h', 'device_class': 'timestamp'},
}


base_topic = 'homeassistant/sensor/fernwaerme/'
base_id = 'fernwaerme_'

heat_data = read_heat_meter()

mqtt.Client.connected_flag = False  # create flag in class
client = mqtt.Client('fernwaerme')
mqtt_broker_ip = '10.0.0.30'


state_payload = {}


def publish_config():
    for obis_code in heat_data.keys():
        metric = OBIS_descriptions[obis_code]['metric']
        name = OBIS_descriptions[obis_code]['name']
        unit = OBIS_descriptions[obis_code]['unit']
        unique_id = f'{base_id}{metric}'
        device_class = OBIS_descriptions[obis_code]['device_class']

        config_topic = f'{base_topic}{unique_id}/config'

        payload = {
            'device_class': device_class, 'name': f'{name} Fernwärme',
            'state_topic': state_topic, 'unit_of_measurement': unit,
            'value_template': f'{{{{ value_json.{unique_id}}}}}', 'unique_id': unique_id
        }
        client.publish(config_topic, payload=json.dumps(payload), qos=2)
        metric_value = heat_data[obis_code]
        try:
            metric_value = int(metric_value)
        except ValueError:
            metric_value = float(metric_value)

        if 'multiplier' in OBIS_descriptions[obis_code]:
            multiplier = OBIS_descriptions[obis_code]['multiplier'] 
        else:
            multiplier = 1

        state_payload[unique_id] = metric_value*multiplier
    return state_payload


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True  # set flag
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


if __name__ == "__main__":
    state_topic = f'{base_topic}state'
    client.connect(mqtt_broker_ip)
    client.on_connect = on_connect  # bind call back function
    client.loop_start()
    print("Connecting to mqtt_broker_ip ", mqtt_broker_ip)
    client.connect(mqtt_broker_ip)  # connect to mqtt_broker_ip
    while not client.connected_flag:  # wait in loop
        print("In wait loop")
        time.sleep(1)
    print("in Main Loop")
    state_payload = publish_config()
    client.publish(state_topic, payload=json.dumps(state_payload), qos=2)
    client.loop_stop()
    client.disconnect()
