# APRS SSID: http://forum.aprs.pl/index.php?topic=1548.0
# APRS Symbole: http://www.aprs.pl/ikony.htm
# AFSK Python Library: https://github.com/casebeer/afsk
# APRS ramki WX: http://www.aprs.pl/wxparam.htm
# APRS ramki protokolu AX.25: http://www.aprs.pl/teoria.htm
# 'c:\\Python27\\Scripts\\aprs -c SP9TOM -d SR9POD "/101941z3548.38N/08621.53E-Tu sa wszystko komentarze"' - wzorzec z czasem
# 'c:\\Python27\\Scripts\\aprs -c SP9TOM -d SR9POD "!3548.38N/08621.53E-Tu sa wszystko komentarze"' - wzorzec bez czasu

import subprocess
from time import sleep
from datetime import datetime
from random import randint
import winsound
import serial
import os
import re
import ctypes
from ctypes import wintypes


# Klasa odpowiedzialna za strukture danych jednostki zasilania
class SystemPowerData(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', wintypes.BYTE),
        ('BatteryFlag', wintypes.BYTE),
        ('BatteryLifePercent', wintypes.BYTE),
        ('Reserved1', wintypes.BYTE),
        ('BatteryLifeTime', wintypes.DWORD),
        ('BatteryFullLifeTime', wintypes.DWORD),
    ]


# Klasa odpowiedzialna za dane dotyczace typu zasilania i stopnia naladowania (bateria)
class PowerStatus(SystemPowerData):
    SYSTEM_POWER_STATUS_P = ctypes.POINTER(SystemPowerData)
    GetSystemPowerStatus = ctypes.windll.kernel32.GetSystemPowerStatus
    GetSystemPowerStatus.argtypes = [SYSTEM_POWER_STATUS_P]
    GetSystemPowerStatus.restype = wintypes.BOOL

    def __init__(self, *args, **kwargs):
        super(PowerStatus, self).__init__(*args, **kwargs)
        self.status = SystemPowerData()

    def getData(self):
        if not self.GetSystemPowerStatus(ctypes.pointer(self.status)):
            raise ctypes.WinError()
        else:
            return self.status.ACLineStatus, self.status.BatteryLifePercent


# Klasa odpowiedzialna za komunikacje z Arduino
class Arduino():
    def __init__(self, port):
        self.port = port

    def getData(self):
        portSzeregowy = serial.Serial(port=self.port, baudrate=9600,
                                      parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE,
                                      bytesize=serial.EIGHTBITS,
                                      )
        bufor = ""
        rsInput = ''
        while rsInput != '|':
            rsInput = portSzeregowy.read()
            bufor = bufor + rsInput
        portSzeregowy.close()
        return bufor


# Klasa odpowiedzialna za rozglaszanie ramek APRS
class APRSbeacon():
    pathToProgram = "c:\\Python27\\Scripts\\aprs"

    def __init__(self, source, target, lat, lon, symbol):
        self.source = source
        self.target = target
        self.lat = re.findall(r"\d+", lat)[0] + re.findall(r"\d+", lat)[1] + '.' + re.findall(r"\d+", lat)[2] + \
                   re.findall(r"^[a-zA-Z]", lat)[0]
        self.lon = re.findall(r"\d+", lon)[0] + re.findall(r"\d+", lon)[1] + '.' + re.findall(r"\d+", lon)[2] + \
                   re.findall(r"^[a-zA-Z]", lon)[0]
        self.symbol = symbol

    def sendFrame(self, message):
        output = subprocess.check_output('%s -c %s -d %s -o aprs.wav "!%s%s%s%s%s"' % (
            self.pathToProgram, self.source, self.target, self.lat, self.symbol[0], self.lon, self.symbol[1], message),
                                         shell=True)
        if len(output) == 0:
            # konieczne dla komputerow typu "stare pasci"
            winsound.PlaySound('aprs.wav', winsound.SND_FILENAME)
            os.remove("aprs.wav")
            return True
        else:
            return False


# Glowny program - SR9POD
print "APRS Beacon - serwis uruchomiony o %s" % str(datetime.now().strftime("%H:%M:%S"))

domek = APRSbeacon("SP9TOM", "SP3-3", "N50 02.71", "E020 13.39", "/-")
arduino = Arduino("COM6")
zasilanie = PowerStatus()

while True:
    interval = randint(15, 25)
    temperatura = re.findall(r"TEMP:(\d*.\d*)", arduino.getData())[0]
    ac, cap = zasilanie.getData()
    if ac == 1:
        statusZasilania = "AC"
    elif ac == 0:
        statusZasilania = "DC %d proc." % cap
    domek.sendFrame("op. Tomek, QSX: SR9AE, Temp. %s st.C, Zasilanie: %s" % (temperatura, statusZasilania))
    print "-> Ramka APRS wyslana o %s, nastepna za %s minut(y), temp. %s st.C, zasilanie: %s" % (
        str(datetime.now().strftime("%H:%M:%S")), str(interval), temperatura, statusZasilania)
    sleep(interval * 60)
