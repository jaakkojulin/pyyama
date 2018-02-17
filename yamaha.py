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
    _ALLOWED_ZONE_COMMANDS = ('getStatus', 'getSoundProgramList', 'setPower', 'setSleep', 'setVolume', 'setMute', 'setInput', 'setSoundProgram','prepareInputChange')
    _ALLOWED_OTHERS = ('system', 'netusb', 'tuner', 'cd')
    _ALLOWED_SYSTEM_COMMANDS = ('getDeviceInfo', 'getFeatures', 'getNetworkStatus', 'getFuncStatus', 'setAutoPowerStandby', 'getLocationInfo', 'sendIrCode')
    _ALLOWED_TUNER_COMMANDS=('getPresetInfo', 'getPlayInfo', 'setFreq', 'recallPreset', 'switchPreset', 'storePreset','setDabService')
    _ALLOWED_NETUSB_COMMANDS=('getPresetInfo', 'getPlayInfo', 'setPlayback', 'toggleRepeat', 'toggleShuffle', 'getListInfo', 'setListControl', 'setSearchString', 'recallPreset', 'storePreset', 'getAccountStatus', 'switchAccount', 'getServiceInfo')
    _ALLOED_CD_COMMANDS = ('getPlayInfo', 'setPlayback', 'toggleTray', 'toggleRepeat', 'toggleShuffle')
    def __init__(self, host):
        self.host=host
        response=self.make_request('system', 'getDeviceInfo')
        if 'response_code' not in response and 'model_name' not in response:
            raise YamahaConnectionError("Could not get device info.")
        self.model_name=response['model_name']

    def get_model_name(self):
        if self.model_name:
            return self.model_name
        else:
            return ''
    def pause(self):
        self.make_request('netusb', 'setPlayback', {'playback': 'pause'})

    def mute(self, zone='main'):
        self.make_request(zone, 'setMute', {'enable': 'true'})

    def unmute(self, zone='main'):
        self.make_request(zone, 'setMute', {'enable': 'false'})

    def make_request(self, zone, command, params={}):
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
        try:
            r = requests.get("http://"+self.host+"/YamahaExtendedControl/v1/"+zone+"/"+command, params=params, timeout=5.0)
        except ConnectionError as error:
            raise YamahaError("Connection error." + str(error))
        except requests.exceptions.Timeout as error:
            raise YamahaError("Connection timeout.")
        except Exception as error:
            raise YamahaError("Some error in connecting: " + str(error))
        if r.status_code != 200:
            raise YamahaError("HTTP Error")
        response=r.json()
        if 'response_code' not in response:
            raise YamahaError("Malformed reply from device.")
        else:
            if response['response_code'] != 0:
                raise YamahaError("Response code was: "+str(response['response_code']))
        return(response)
