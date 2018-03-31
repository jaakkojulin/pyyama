#!/usr/bin/python3

import socket
import requests
import defusedxml.lxml as lxml
from urllib.parse import urlparse
from yama import YamaError


class YamaFinderError(YamaError):
    """Our errors. These are business as usual, failures should be tolerated. We may try to connect to
    unsupported devices etc.
    """
    pass

def find_hostname(url):
    o=urlparse(url)
    return o.netloc.split(':', 1)[0]


def find_location_headers_of_media_renderers_with_ssdp(timeout=5):
    ssdp_request = \
    'M-SEARCH * HTTP/1.1\r\n' \
    'HOST: 239.255.255.250:1900\r\n' \
    'MX: 5\r\n' \
    'Man: "ssdp:discover"\r\n' \
    'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n' \
    '\r\n'
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.settimeout(timeout)
    s.sendto(ssdp_request.encode(), ('239.255.255.250', 1900) )
    
    try:
        while True:
            data, addr = s.recvfrom(65507)
            msg=data.decode()
            #print(addr, '\n', msg)
            lines = msg.split('\r\n')
            if len(lines) == 0:
                continue
            if lines[0] != 'HTTP/1.1 200 OK': 
                continue
            for line in lines[1:]:
                if line == '':
                    break
                try:
                    key, value = line.split(': ', 1)
                    if key == 'Location' and value[0:4] == 'http':
                        yield value
                except ValueError:
                    continue
    except socket.timeout:
        pass

def verify_yama(loc):
    yama = {}
    hostname=find_hostname(loc)
    yama['hostname'] = hostname
    try:
        r = requests.get(loc, timeout=3.0)
        if r.status_code != 200:
            YamaFinderError("HTTP error, status code: " + str(r.status_code))
    except ConnectionError as error:
        YamaFinderError("Connection error: " + str(error))
    root = lxml.fromstring(r.text.encode())
    #Check device tag exists
    device=root.find('device', root.nsmap)
    if device is None:
        YamaFinderError("Device tag not found. This is probably not a device we support.")
    #Check manufacturer tag <manufacturer> is under <device> and the contents are correct
    mf=device.find('manufacturer', root.nsmap)
    if mf is None:
        YamaFinderError("Manufacturer tag not found. This is probably not a device we support.")
    if mf.text != 'Yamaha Corporation':
        YamaFinderError("Manufacturer \"" + mf.text + "\" is not supported.")

    #Load model name, if found.
    model = device.find('modelName', root.nsmap)
    if model is not None:
        yama['model'] = model.text
    #Load friendly name, if found.
    name = device.find('friendlyName', root.nsmap)
    if name is not None:
        yama['name'] = name.text

    xdevice = root.find('yamaha:X_device', root.nsmap) 
    # Check Yamaha tag <yamaha:X_device> exists
    if xdevice is None:
        YamaFinderError("yamaha:X_device tag not found")
    urlbase = xdevice.find('yamaha:X_URLBase', root.nsmap)
    if urlbase is None:
        YamaFinderError("yamaha:X_URLBase tag not found")
    url = urlbase.text
    if find_hostname(url) != hostname:
        YamaFinderError("URL doesn't match the expected host.")
    #print("I think we have a valid dude here: " + url)
    # Check URL <yamaha:X_URLBase> matches IP address
    xservicelist = xdevice.find('yamaha:X_serviceList', root.nsmap)
    if xservicelist is None:
        YamaFinderError("yamaha:X_serviceList tag not found")
    # Check <yamaha:X_yxcControlURL>/YamahaExtendedControl/v1/</yamaha:X_yxcControlURL>
    for xservice in xservicelist.findall('yamaha:X_service', root.nsmap):
        controlurl = xservice.find('yamaha:X_yxcControlURL', root.nsmap)
        if controlurl is None:
            continue
        if controlurl.text == "/YamahaExtendedControl/v1/":
            #Build full url, ensure there is exactly one forward slash between the base URL and control URL
            yama['url'] = url.strip('/') + ('/' if controlurl.text[0] != '/' else '') + controlurl.text
            return yama 
    return

def find_yamas():
    for loc in find_location_headers_of_media_renderers_with_ssdp():
        try:
            yama=verify_yama(loc)
            if yama:
                yield yama
        except YamaFinderError as error:
            print(error)

if __name__ == "__main__":
    for yama in find_yamas():
        print(yama)
