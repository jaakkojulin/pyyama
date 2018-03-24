#!/usr/bin/env python3
""" Yama control module
    Copyright (C) 2018 Jaakko Julin

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    See file "LICENSE" for details.
"""

__author__ = 'Jaakko Julin'

import requests

class YamaError(Exception):
    """Generic"""
    pass


class YamaConnectionError(YamaError):
    """Connection related error"""
    pass


class Yama:
    _ALLOWED_ZONES = ('main', 'zone2', 'zone3', 'zone4')
    _ALLOWED_ZONE_COMMANDS = ('getStatus', 'getSoundProgramList', 'setPower', 'setSleep', 'setVolume', 'setMute',
                              'setInput', 'setSoundProgram', 'prepareInputChange')
    _ALLOWED_OTHERS = ('system', 'netusb', 'tuner', 'cd')
    _ALLOWED_SYSTEM_COMMANDS = (
    'getDeviceInfo', 'getFeatures', 'getNetworkStatus', 'getFuncStatus', 'setAutoPowerStandby', 'getLocationInfo',
    'sendIrCode')
    _ALLOWED_TUNER_COMMANDS = (
    'getPresetInfo', 'getPlayInfo', 'setFreq', 'recallPreset', 'switchPreset', 'storePreset', 'setDabService')
    _ALLOWED_NETUSB_COMMANDS = (
    'getPresetInfo', 'getPlayInfo', 'setPlayback', 'toggleRepeat', 'toggleShuffle', 'getListInfo', 'setListControl',
    'setSearchString', 'recallPreset', 'storePreset', 'getAccountStatus', 'switchAccount', 'getServiceInfo')
    _ALLOWED_CD_COMMANDS = ('getPlayInfo', 'setPlayback', 'toggleTray', 'toggleRepeat', 'toggleShuffle')

    def __init__(self, host: str):
        """Connect to and communicate with a device over HTTP

        Args:
            host: Hostname of the device (or IP address)
        """
        assert isinstance(host, str)
        self.host = host
        self.headers = dict()
        response = self.make_request('system', 'getDeviceInfo')
        if 'model_name' not in response:
            raise YamaConnectionError("Could not get device info.")
        self._model_name = response['model_name']
        self._device_id = response['device_id']
        response = self.make_request('system', 'getFeatures')
        self._input_list={}
        self._volume_max = {}
        self._volume_min = {}
        self._volume_step = {}

        try:
            #self.input_list = [input['id'] for input in response['system']['input_list']]
            self.zones = response['distribution']['server_zone_list']
            for zone in response['zone']:
                self.set_input_list(zone['id'], zone['input_list'])
                for rangesettings in zone['range_step']:
                    if rangesettings['id'] == 'volume':
                        self._volume_max[zone['id']] = int(rangesettings['max'])
                        self._volume_min[zone['id']] = int(rangesettings['min'])
                        self._volume_step[zone['id']] = int(rangesettings['step'])
        except KeyError as error:
            raise YamaConnectionError("Response from device doesn't contain the information I need: " + str(error))

    @property
    def device_id(self):
        return self._device_id
    @device_id.setter
    def device_id(self, id):
        assert isinstance(id, str)
        self._device_id=id

    @property
    def model_name(self):
            return self._model_name
    @model_name.setter
    def model_name(self, name):
            assert isinstance(name, str)
            self._model_name=name

    def get_current_input(self, zone: str) -> str:
        """Get the name of the current input

        Args:
            zone: name of the zone

        Returns:
            str: name of the current input of zone

        """
        input=""
        response=self.make_request(zone, 'getStatus')
        try:
            input=response['input']
        except KeyError:
            raise YamaConnectionError("Response from device doesn't contain the information I need")
        return input

    def get_input_list(self, zone):
        return self._input_list[zone]

    def set_input_list(self, zone, list):
        """

        :type list: list of input names, e.g. ['spotify', 'optical', ...]
        ;
        """
        self._input_list[zone] = list

    def play(self):
        """ Start playback of network/USB sources"""
        self.make_request('netusb', 'setPlayback', {'playback': 'play'})

    def pause(self):
        """Pause playback of network/USB sources"""
        self.make_request('netusb', 'setPlayback', {'playback': 'pause'})

    def stop(self):
        """Stop playback of network/USB sources"""
        self.make_request('netusb', 'setPlayback', {'playback': 'stop'})

    def previous(self):
        """Previous track (only on netusb source)"""
        self.make_request('netusb', 'setPlayback', {'playback': 'previous'})

    def next(self):
        self.make_request('netusb', 'setPlayback', {'playback': 'next'})

    def mute(self, zone):
        self.make_request(zone, 'setMute', {'enable': 'true'})

    def unmute(self, zone):
        self.make_request(zone, 'setMute', {'enable': 'false'})

    def change_input(self, zone, input):
        self.make_request(zone, 'setInput', {'input': input})

    def power_on(self, zone):
        self.make_request(zone, 'setPower', {'power': 'on'})

    def standby(self, zone):
        self.make_request(zone, 'setPower', {'power': 'standby'})

    def set_volume_dB(self, zone: str, volumedB):
        volume=self.get_volume_max(zone)+int(volumedB/0.5)
        if volume < 0:
            volume = 0
        #print("About to set the volume to " + str(volume))
        self.make_request(zone, 'setVolume', {'volume': str(volume)})

    def get_volume(self, zone: str):
        response=self.make_request(zone, 'getStatus')
        volume=int(response['volume'])
        if volume > self.get_volume_max(zone):
            raise YamaError("Volume above known maximum. Impossible.")
        else:
            return volume

    def get_volume_dB(self, zone: str): # Don't use this function, use get_status instead
        response=self.make_request(zone, 'getStatus')
        volume=int(response['volume'])
        maxvolume=self.get_volume_max(zone)
        print("Volume as reported by device is " + str(volume) + " and in dB this probably is " + str((volume-maxvolume)*0.5))
        return (volume-maxvolume) * 0.5

    def get_volume_max(self, zone: str) -> int:
        return self._volume_max[zone]

    def get_volume_min(self, zone):
        return self._volume_min[zone]

    def get_volume_step(self, zone):
        return self._volume_step[zone]

    def get_status(self, zone):  # TODO: store this status stuff somewhere and replace methods like get_volume() by returning members of that data structure
        response=self.make_request(zone, 'getStatus')
        out = {'mute': bool(response['mute']),
               'volume': int(response['volume']),
               'power': (response['power'] == 'on'),
               'input': response['input']
        }
        return out

    def get_nowplaying(self):
        input='netusb'
        if True: #TODO: if current input is something...
            response=self.make_request(input, 'getPlayInfo')
            return response
        else:
            return {}

    def make_request(self, zone, command, params=None):
        if params is None:
            params = {}
        if not (zone in self._ALLOWED_ZONES or zone in self._ALLOWED_OTHERS):
            raise ValueError("Wrong zone or API: " + zone)
        if zone in self._ALLOWED_ZONES and command not in self._ALLOWED_ZONE_COMMANDS:
            raise ValueError("Zone command not allowed")
        if zone == "system" and command not in self._ALLOWED_SYSTEM_COMMANDS:
            raise ValueError("System command not allowed")
        if zone == "netusb" and command not in self._ALLOWED_NETUSB_COMMANDS:
            raise ValueError("Net/USB command not allowed")
        if zone == "tuner" and command not in self._ALLOWED_TUNER_COMMANDS:
            raise ValueError("Tuner command not allowed")
        if zone == "cd" and command not in self._ALLOWED_CD_COMMANDS:
            raise ValueError("CD command not allowed")
        url = "http://" + self.host + "/YamahaExtendedControl/v1/" + zone + "/" + command
        try:
            r = requests.get(url, params=params, timeout=3.0, headers=self.headers)
        except ConnectionError as error:
            raise YamaError("Connection error." + str(error))
        except requests.exceptions.Timeout as error:
            raise YamaError("Connection timeout.")
        except Exception as error:
            raise YamaError("Error: " + str(error))
        if r.status_code != 200:
            raise YamaError("HTTP Error")
        response = r.json()
        if 'response_code' not in response:
            raise YamaError("Malformed reply from device.")
        else:
            if response['response_code'] != 0:
                raise YamaError("Response code was: " + str(response['response_code']))
        print("REQUEST: " + url + "\nPARAMS: " + str(params) + "\nHEADERS: " + str(self.headers) + "\nRESPONSE: " + r.text + "\n")
        return (response)

    def set_listener_port(self, listener_port: int):
        self.listener_port = listener_port
        self.headers = {'X-AppName': 'MusicCast/1.40(PyYama)', 'X-AppPort': str(listener_port)}
