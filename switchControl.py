
import time
from subprocess import Popen, PIPE

UsbRelayPath = 'usbrelay'
NAME_1RELAY = '1_1'
STATE_ON = "1"
STATE_OFF = "0"
TURNED_ON_WAIT = 3
TURNED_OFF_WAIT = 0.5

def getRelayState(relayName = NAME_1RELAY):
    """Получает состояние реле \n
    args:
        relayName: str - Наименование релейного модуля
    return:
        Первый: str - состояние реле("0" или "1", Если не удалось определить, то "-1")
        Второй: str - ошибка(Если нет ошибок, то вернется пустая строка)
    """
    outBytes, err = Popen(UsbRelayPath, shell=True, stdout=PIPE).communicate()
    if err != None:
        return "-1", str(err)
    outStr = outBytes.decode('utf-8')
    relaysAndStates = outStr.split('\n')
    for item in relaysAndStates:
        relayAndState = item.split('=')
        if len(relayAndState) < 2:
            continue
        name, state = relayAndState[0], relayAndState[1]
        if name == relayName:
            return state, ""
    return "-1", "Не нашли релейный модуль с именем " + relayName 

def turnOnRelay(relayName = NAME_1RELAY):
    """Включает релейный модуль\n
    args:
        relayName: str - Наименование релейного модуля
    return:
        Первый: str - ошибка(Если нет ошибок, то вернется пустая строка)
    """
    Popen(UsbRelayPath + " " + relayName + "=" + STATE_ON, shell=True, stdout=PIPE).communicate()
    state, err = getRelayState(relayName)
    if err != "":
        return err
    if state == STATE_ON:
        return ""
    return "Не удалось включить релейный модуль"
    
def turnOffRelay(relayName = NAME_1RELAY):
    """Выключает релейный модуль\n
    args:
        relayName: str - Наименование релейного модуля
    return:
        Первый: str - ошибка(Если нет ошибок, то вернется пустая строка)
    """
    Popen(UsbRelayPath + " " + relayName + "=" + STATE_OFF, shell=True, stdout=PIPE).communicate()
    state, err = getRelayState(relayName)
    if err != "":
        return err
    if state == STATE_OFF:
        return ""
    return "Не удалось выключить релейный модуль"

def sendTurnOnSignal(relayName = NAME_1RELAY, wait = TURNED_ON_WAIT):
    """Отправляет контроллеру команду на открытие двери\n
    args:
        relayName: str - Наименование релейного модуля
    return:
        Первый: str - ошибка(Если нет ошибок, то вернется пустая строка)
    """
    err = turnOnRelay(relayName)
    if err != "":
        return err
    time.sleep(wait)
    return turnOffRelay(relayName)

def sendTurnOffSignal(relayName = NAME_1RELAY, wait = TURNED_OFF_WAIT):
    """Отправляет контроллеру команду на открытие двери\n
    args:
        relayName: str - Наименование релейного модуля
    return:
        Первый: str - ошибка(Если нет ошибок, то вернется пустая строка)
    """
    err = turnOffRelay(relayName)
    if err != "":
        return err
    time.sleep(wait)
    return turnOnRelay(relayName)

#sendTurnOnSignal('1_1', 2)
    


#######################
#import usb
#import hid
#d = hid.Device(0x16c0, 0x05df)
#d.write([hex(0xFF), 0])
#d.send_feature_report([0x41]) #["0x41", "0x01"]
#for dev in usb.core.find(find_all=True):
    #print("DEV::",dev, "\n", hex(dev.idVendor), dev.idProduct)
#    if hex(dev.idVendor) == 0x16c0:
#        print("DEV::",dev, "\n", hex(dev.idVendor), dev.idProduct)
    #h = hid.Device(vid=dev.idVendor, pid=dev.idProduct)
    # dev.c
    # usb.control.set_feature(dev, 1)

# idVendor               : 0x16c0
#idProduct              : 0x05df
