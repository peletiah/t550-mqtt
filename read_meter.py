#!/usr/bin/python

SERIAL = "/dev/ttyUSB0"
BAUDRATE = 300
READ_BAUDRATE = 2400
BYTESIZE = 7
PARITY = "E"
STOPBITS = 1
TIMEOUT = 2
XONXOFF = 0
RTSCTS = 0
INIT_MSG = "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
REQ_MSG = "/?!\x0D\x0A"
SLEEP_INTERVAL = 0.5

OBIS_codes = {
    '6.8': 'meter_reading',
    '6.6': 'max_heat_output',
    '6.26': 'throughput',
    '6.33': 'max_throughput',
    '9.4': 'max_temp_forward_return_flow',
    '6.31': 'operating_hours',
    '6.32': 'downtime',
    '9.31': 'flowhours'
}

# TODO object for OBIS

def read_heat_meter():
    # based on http://www.sedelmaier.at/sites/sedelmaier.at/files/uh50.py.txt

    #    serial_port = serial.Serial(SERIAL, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS,
    #                                timeout=TIMEOUT, xonxoff=XONXOFF, rtscts=RTSCTS)
    #
    #    # send init message
    #    serial_port.write(INIT_MSG)
    #    serial_port.write(INIT_MSG)
    #
    #    # send request message
    #    serial_port.write(REQ_MSG)
    #    serial_port.flush()
    #    time.sleep(SLEEP_INTERVAL)
    #
    #    # send read identification message
    #    identification_msg = serial_port.readline()
    #
    #    # change baudrate
    #    serial_port.baudrate = READ_BAUDRATE
    #
    #    heat_data = ''
    #
    #    try:
    #        # read data message
    #        while True:
    #            response = serial_port.readline()
    #            print(response, end="")
    #            heat_data = heat_data + response
    #            if "!" in response:
    #                break
    #    finally:
    #        serial_port.close()

    serial_data = """
6.8(0074900*kWh)6.26(04142.48*m3)9.21(66409080)
6.26*01(03957.55*m3)6.8*01(0071925*kWh)
F(0)9.20(66409080)6.35(60*m)
6.6(0016.2*kW)6.6*01(0015.3*kW)6.33(001.608*m3ph)9.4(094.4*C&092.9*C)
6.31(0046124*h)6.32(0000000*h)9.22(R)9.6(000&66409080&0&000&66409080&0)
9.7(60000)6.32*01(0000000*h)6.36(01-01&00:00)6.33*01(001.608*m3ph)
6.8.1()6.8.2()6.8.3()6.8.4()6.8.5()
6.8.1*01()6.8.2*01()6.8.3*01()
6.8.4*01()6.8.5*01()
9.4*01(094.4*C&092.9*C)
6.36.1(2016-01-18)6.36.1*01(2011-07-13)
6.36.2(2015-01-07)6.36.2*01(2015-01-07)
6.36.3(2014-12-23)6.36.3*01(2014-12-23)
6.36.4(2014-03-14)6.36.4*01(2014-03-14)
6.36.5()6.36*02(01&00:00)9.36(2016-02-12&19:36:08)9.24(1.5*m3ph)
9.17(0)9.18()9.19()9.25()
9.1(0&1&0&0000&CECV&CECV&1&5.16&5.16&F&101008&1>1>04&08&0)
9.2(&&)9.29()9.31(0014842*h)
9.0.1(00000000)9.0.2(00000000)9.34.1(000.00000*m3)9.34.2(000.00000*m3)
8.26.1(00000000*m3)8.26.2(00000000*m3)
8.26.1*01(00000000*m3)8.26.2*01(00000000*m3)
6.26.1()6.26.4()6.26.5()
6.26.1*01()6.26.4*01()6.26.5*01()0.0(66409080)
"""
    serial_data = serial_data.replace('\n', '')
    heat_data = dict()
    for metric in serial_data.split(')'):
        try:
            code, payload = metric.split('(')
        except ValueError:
            print(metric)
        if metric.split('(')[0] in OBIS_codes.keys():
            value = payload.split('*')[0]
            heat_data[code] = value

    return heat_data
