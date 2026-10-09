# -*- coding: utf-8 -*-
#
# Copyright 2024 Kevin Lindemark
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
import gc
gc.collect()
import network
from machine import reset, Pin
from time import ticks_ms
import secrets
import requests
import socket

ssid = secrets.SSID
password = secrets.PASSWORD

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    print('WLAN status:', wlan.status())
    wlan.active(True)
    try:
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(ssid, password)
            print('WLAN status:', wlan.status())
            start = ticks_ms()
            while not wlan.isconnected():
                if ticks_ms() - start > 10000:
                    print("Could not connect to wifi!")
                    break

    except Exception as e:
        print(f"WiFi error '{e}' occured, rebooting system")
        reset()
    finally:
        if wlan.isconnected():
            print("Connected to wifi!")
            print(f"wifi statuscode {wlan.status()}")
    return wlan    
    
wlan = do_connect()

if ssid == 'EK-PUBLIC' and wlan.isconnected():
    req = '''POST /index.php?zone=guest HTTP/1.1
Host: 192.168.200.1:8002
User-Agent: curl/8.21.0
Accept: */*
Content-Length: 12
Content-Type: application/x-www-form-urlencoded

accept=Login
'''
    print('[+] Connected to WiFi', wlan.ifconfig())
    print('[+] Network test')
    addr_info = socket.getaddrinfo('192.168.200.1', 8002)
    addr = addr_info[0][-1]

    s = socket.socket()
    print('[+] Connecting to',addr)
    s.connect(addr)
    req_text = req.replace('\n','\r\n')
    s.send(req_text.encode('utf-8'))
    while True:
        data = s.recv(1024) # Adjust buffer size as needed
        if not data:
            break
        print(data.decode('utf-8'), end="")
    s.close()
    gc.collect()
    print('[+] Testing internet connection...')
    res = requests.get('https://www.ek.dk/')
    if res.status_code == 200:
        print('[+] Succesfully connected to the entaweb-machine')
    else:
        print('[-] Some error happend', res.status_code)
    gc.collect()
elif wlan.isconnected():
    print('[+] Connected to', ssid)
else:
    print('[-] Error connecting. Try again')
    reset()
    
