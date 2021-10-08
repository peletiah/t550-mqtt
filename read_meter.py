import time

import serial

SERIAL = "/dev/ttyUSB0"
BAUDRATE = 300
READ_BAUDRATE = 2400
BYTESIZE = 7
PARITY = "E"
STOPBITS = 1
TIMEOUT = 10
XONXOFF = 0
RTSCTS = 0
INIT_MSG = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
REQ_MSG = b"/?!\x0D\x0A"
SLEEP_INTERVAL = 0.5

OBIS_codes = [
    '6.8',
    '6.6',
    '6.26',
    '6.33',
    '9.4',
    '6.31',
    '6.32',
    '9.31']


def read_heat_meter():
    """
    based on http: // www.sedelmaier.at / sites / sedelmaier.at / files / uh50.py.txt
    """

    ser = serial.Serial(SERIAL, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS,
                                timeout=TIMEOUT, xonxoff=XONXOFF, rtscts=RTSCTS)

    # send init message
    ser.write(INIT_MSG)
    ser.write(INIT_MSG)

    # send request message
    ser.write(REQ_MSG)
    ser.flush()
    time.sleep(SLEEP_INTERVAL)

    # send read identification message
    identification_msg = ser.readline()

    # change baudrate
    ser.baudrate = READ_BAUDRATE

    raw_heat_data = ''

    try:
        # read data message
        response = ser.readlines()
    finally:
        ser.close()

    raw_heat_data = b''.join(response).decode('utf-8').strip('\x02').replace('\r\n','').replace('\x03m\x00','')

    heat_data = dict()
    for metric in raw_heat_data.split(')'):
        try:
            code, payload = metric.split('(')
        except ValueError:
            print(metric)
        if metric.split('(')[0] in OBIS_codes:
            value = payload.split('*')[0]
            heat_data[code] = value
    print(heat_data)

    return heat_data
