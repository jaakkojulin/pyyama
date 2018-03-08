#!/usr/bin/env python3
import requests


class YamahaError(Exception):
    """Generic"""
    pass


class YamahaConnectionError(YamahaError):
    """Connection related error"""
    pass


class Yamaha:
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

    def __init__(self, host):
        """Connect to and communicate with Yamaha device over HTTP

        :param host: hostname or IP address of device
        """
        assert isinstance(host, str)
        self.host = host
        self.headers = dict()
        response = self.make_request('system', 'getDeviceInfo')
        if 'model_name' not in response:
            raise YamahaConnectionError("Could not get device info.")
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
            raise YamahaConnectionError("Response from device doesn't contain the information I need: " + str(error))
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

    def get_current_input(self, zone):
        response=self.make_request(zone, 'getStatus')
        try:
            input=response['input']
        except KeyError:
            raise YamahaConnectionError("Response from device doesn't contain the information I need")
        return input

    def get_input_list(self, zone):
        return self._input_list[zone]

    def set_input_list(self, zone, list):
        """

        :type list: list of input names, e.g. ['spotify', 'optical', ...]
        ;
        """
        self._input_list[zone] = list

    def pause(self):
        """Pause playback of network/USB sources"""
        self.make_request('netusb', 'setPlayback', {'playback': 'pause'})

    def mute(self, zone):
        self.make_request(zone, 'setMute', {'enable': 'true'})

    def unmute(self, zone):
        self.make_request(zone, 'setMute', {'enable': 'false'})

    def change_input(self, zone, input):
        self.make_request(zone, 'setInput', {'input': input})


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
            raise YamahaError("Volume above known maximum. Impossible.")
        else:
            return volume

    def get_volume_dB(self, zone: str):
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
            raise YamahaError("Connection error." + str(error))
        except requests.exceptions.Timeout as error:
            raise YamahaError("Connection timeout.")
        except Exception as error:
            raise YamahaError("Some error in connecting: " + str(error))
        if r.status_code != 200:
            raise YamahaError("HTTP Error")
        response = r.json()
        if 'response_code' not in response:
            raise YamahaError("Malformed reply from device.")
        else:
            if response['response_code'] != 0:
                raise YamahaError("Response code was: " + str(response['response_code']))
        print(r.text)
        return (response)

    def set_listener_port(self, listener_port: int):
        self.listener_port = listener_port
        self.headers = {'X-AppName': 'MusicCast/1.40(PyYama)', 'X-AppPort': str(listener_port)}
