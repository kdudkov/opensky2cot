#!/usr/bin/env python3

import requests
import sys
import time
import socket
import xml.etree.ElementTree as ET
import argparse

latmin, lonmin = 59.277491, 29.066558
latmax, lonmax = 60.293171, 32.255798

TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def state2cot(s):
    cot = ET.Element('event')
    cot.set('version', '2.0')
    cot.set('uid', 'icao24-' + s[0].lower())
    if s[8]:
        cot.set('type', 'a-f-G-C-F')
    else:
        cot.set('type', 'a-f-A-C-F')
    cot.set('how', 'm-g')
    cot.set('time', time.strftime(TIME_FORMAT, time.gmtime()))
    cot.set('start', time.strftime(TIME_FORMAT, time.gmtime()))
    cot.set('stale', time.strftime(TIME_FORMAT, time.gmtime(time.time() + 120)))

    point = ET.SubElement(cot, 'point')
    point.set('lat', str(s[6]))
    point.set('lon', str(s[5]))
    point.set('hae', str(s[13]) if s[13] is not None else str(s[7]))
    point.set('ce', '9999999.0')
    point.set('le', '9999999.0')

    det = ET.SubElement(cot, 'detail')
    ET.SubElement(det, 'contact', attrib={'callsign': s[1].strip()})
    ET.SubElement(det, 'remarks').text = '%s, icao24: %s, country: %s, trans: %s' % (s[1].strip(), s[0], s[2], s[14])
    track = ET.SubElement(det, 'track')
    track.set('course', str(s[10]))
    track.set('speed', str(s[9]))

    return ET.tostring(cot)

def send_broadcast(addr, port, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(data, (addr, port))
    s.close()

def send_udp(addr, port, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(data, (addr, port))
    s.close()

def send_tcp(addr, port,data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addr, port))
    s.send(data)
    s.close()

"""
0 	icao24 	string 	Unique ICAO 24-bit address of the transponder in hex string representation.
1 	callsign 	string 	Callsign of the vehicle (8 chars). Can be null if no callsign has been received.
2 	origin_country 	string 	Country name inferred from the ICAO 24-bit address.
3 	time_position 	int 	Unix timestamp (seconds) for the last position update. Can be null if no position report was received by OpenSky within the past 15s.
4 	last_contact 	int 	Unix timestamp (seconds) for the last update in general. This field is updated for any new, valid message received from the transponder.
5 	longitude 	float 	WGS-84 longitude in decimal degrees. Can be null.
6 	latitude 	float 	WGS-84 latitude in decimal degrees. Can be null.
7 	baro_altitude 	float 	Barometric altitude in meters. Can be null.
8 	on_ground 	boolean 	Boolean value which indicates if the position was retrieved from a surface position report.
9 	velocity 	float 	Velocity over ground in m/s. Can be null.
10 	true_track 	float 	True track in decimal degrees clockwise from north (north=0°). Can be null.
11 	vertical_rate 	float 	Vertical rate in m/s. A positive value indicates that the airplane is climbing, a negative value indicates that it descends. Can be null.
12 	sensors 	int[] 	IDs of the receivers which contributed to this state vector. Is null if no filtering for sensor was used in the request.
13 	geo_altitude 	float 	Geometric altitude in meters. Can be null.
14 	squawk 	string 	The transponder code aka Squawk. Can be null.
15 	spi 	boolean 	Whether flight status indicates special purpose indicator.
16 	position_source 	int 	Origin of this state’s position: 0 = ADS-B, 1 = ASTERIX, 2 = MLAT
"""

def get_info():
    url = 'https://opensky-network.org/api/states/all?lamin=%f&lomin=%f&lamax=%f&lomax=%f' % (latmin, lonmin, latmax, lonmax)
    r = requests.get(url)

    if r.status_code != requests.codes.ok:
        print('invalid responce - %d: %s' % (r.status_code, r.text))
        sys.exit(1)

    return r.json()['states']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--proto", help="protocol to send: tcp, udp or broadcast", default="broadcast")
    parser.add_argument("--addr", help="address")
    parser.add_argument("--port", help="port", type=int, default=0)
    parser.add_argument("--debug", help="debug output", action="store_true")
    args = parser.parse_args()

    states = get_info()

    print('got %d planes' % len(states))
    for s in states:
        dat = state2cot(s)
        if args.debug:
            print(str(dat))

        if args.proto.lower() == 'udp':
            addr = args.addr or '127.0.0.1'
            port = args.port or 4242
            print('sending via udp to %s:%d' % (addr, port))
            send_udp(addr, port, dat)
        elif args.proto.lower() == 'tcp':
            addr = args.addr or '127.0.0.1'
            port = args.port or 8099
            print('sending via tcp to %s:%d' % (addr, port))
            send_tcp(addr, port, dat)
        elif args.proto.lower() == 'broadcast':
            addr = args.addr or '239.2.3.1'
            port = args.port or 6969
            print('sending via broadcast to %s:%d' % (addr, port))
            send_broadcast(addr, port, dat)
