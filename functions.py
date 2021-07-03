import face_recognition as fr
import os
import fnmatch
import numpy as np
import pickle
import cv2
import json
#import db
import variables as var

def getFirstEncodedAndLocation(encodings, locations):
    """Получаем дескрипторы и координаты первого лица"""
    if len(encodings) == 0 or len(locations) == 0:
        return [], []
    return encodings[0], locations[0]

def isSameFaceEncodings(encodings, standardEncode):
    """Проверяем, принадлежат ли дескрипторы в листе encodings человеку с дескриптором standardEncode"""
    results = fr.compare_faces(encodings, standardEncode, 0.5)
    ret = False
    try:
        count = results.count(True)
        ret = True if count == len(encodings) else False
    except ValueError:
        ret = False
    finally:
        return ret

def getFirstEncodedAndLocationFromImg(img):
    """Получаем дескрипторы и координаты первого лица из кадра"""
    locations = fr.face_locations(img)
    encodings = fr.face_encodings(img, locations)
    return getFirstEncodedAndLocation(encodings, locations)

def getAllEncodingsAndLocationsFromImg(img):
    locations = fr.face_locations(img)
    encodings = fr.face_encodings(img, locations)
    return encodings, locations

def getFaceImage(img, loc):
    """Извлекаем из кадра фото лица"""
    top, right, bottom, left = loc
    return img[top:bottom, left:right]

def getSubImage(img, left, right, top = 1, down = 1):
    """Вырезаем изображение исходя из отступов со всех сторон
        left - отступ слева(в процентах)"""
    height, width = img.shape[:2]
    return img[int(height*top/100.0):int(height - height*down/100.0), int(width*left/100.0):int(width - width*right/100.0)]

def getSquareArea(img, x, y, squareWidth):
    return img[y:y+squareWidth, x:x+squareWidth]

def drawFaceFrame(img, loc):
    """Рисуется прямоугольные линии вокруг лица"""
    top, right, bottom, left = loc
    line_len = 20 #длина стороны прямого угла
    thikness = 2 #толщина линии
    img = cv2.line(img, (left, top), (left + line_len, top), (0, 255, 0), thikness) #левая верхняя горизонтальная линия
    img = cv2.line(img, (left, top), (left, top + line_len), (0, 255, 0), thikness) #левая верхняя вертикальная линия
    img = cv2.line(img, (left, bottom), (left, bottom - line_len), (0, 255, 0), thikness) #левая нижняя вертикальная линия
    img = cv2.line(img, (left, bottom), (left + line_len, bottom), (0, 255, 0), thikness) #левая нижняя горизонтальная линия
    img = cv2.line(img, (right, bottom), (right - line_len, bottom), (0, 255, 0), thikness) #правая нижняя горизонтальная линия
    img = cv2.line(img, (right, bottom), (right, bottom - line_len), (0, 255, 0), thikness) #правая нижняя вертикальная линия
    img = cv2.line(img, (right, top), (right, top + line_len), (0, 255, 0), thikness) #правая верхняя вертикальная линия
    img = cv2.line(img, (right, top), (right - line_len, top), (0, 255, 0), thikness) #правая верхняя горизонтальная линия
    return img

def draw2verticalLines(img, fromLeft: int, fromRight: int):
    """Отрисовывается две вертикальные линии.
        fromLeft - отсутп слева (в процентах)"""
    height, width = img.shape[:2] #длина и ширина изображения
    distanceFromLeftL = int(width * fromLeft/100.0) #определяем расстояние отступа слева до первой линии
    distanceFromLeftR = int(width - width * fromRight/100.0)#определяем расстояние отступа слева до второй линии
    img = cv2.line(img, (distanceFromLeftL, 0), (distanceFromLeftL, height), (0, 255, 0), 2)
    img = cv2.line(img, (distanceFromLeftR, 0), (distanceFromLeftR, height), (255, 0, 0), 2)
    return img

def drawSquareCentered(img, x, y, squareWidth):
    """Отрисовывается квадрат на изображении.
        squareWidth - длина квадрата"""
    img = cv2.rectangle(img, (x, y), (x+squareWidth, y+squareWidth), (0,255,0), 2)
    return img

def outUnderSquareLegend(img, x, y, squareWidth, text = "unknown"):
    temp1 = y + squareWidth
    cv2.rectangle(img, (x, temp1), (x+squareWidth, temp1+40), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, "USER_ID:" + text, (x + 7, temp1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

def getSquareWidth(img):
    """Определяется приемлемая длина стороны квадрата.\n
        squareWidth - длина квадрата.
        x, y - координаты левого верхнего угла"""
    height, width = img.shape[:2]
    squareWidth = 300 #длина квадрата по умоланию
    halfSquare = squareWidth/2.0
    x = int(width/2.0-halfSquare)
    y = int(height/2.0-halfSquare)
    if height < width:
        squareWidth = squareWidth if height > squareWidth else height
    else:
        squareWidth = squareWidth if width > squareWidth else width
    return squareWidth, x, y

def drawLegendFrame(img, loc, text):
    """Выводится текст на изображение."""
    top, right, bottom, left = loc
    top_left = (left, top)
    bottom_right = (right, bottom + 22)
    cv2.rectangle(img, (left, bottom + 22), (right, bottom), (0, 0, 255), cv2.FILLED)
    #cv2.rectangle(img, top_left, bottom_right, [0, 255, 0], 2)
    cv2.putText(img, text, (left + 6, bottom + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return img

def toJsonStr(param):
    return json.dumps(param)

from datetime import datetime

def log(console, type, file_path, line): 
    line = datetime.now().strftime('%Y-%m-%d %H:%M:%S=>') + type + "=>" + str(line)
    if console: print(line)
    with open(file_path, 'a') as file:
        file.write("\n" + line)

def logf(type = "ERROR", line = "NO_MESSAGE"):
    log(False, type, "./log.txt", line)

def logc(type = "ERROR", line = "NO_MESSAGE"):
    log(True, type, "./log.txt", line)

def getFaceIdByEncode(encodings: list, ids: list, encoding: list):
    """Поиск идентификатора исходя из дескриптора."""
    results = fr.compare_faces(encodings, encoding, 0.5)
    try:
        idx = results.index(True)
        return ids[idx]
    except ValueError as e:
        #print("getFaceIdByEncode:error:", e)
        return "-1"

def isListHasKeys(lst: dict = {}, keys: list = [], keyPrefix = '--'):
    ret = {}
    allExist = True
    for key in keys:
        if (keyPrefix + key) in lst:
            ret[key] = lst[keyPrefix + key]
        else: allExist = False
    return ret, allExist

import configparser
 
def createConfigFile(path):
    """Создание конфигурационного файла и заполнение значениями по умолчанию"""
    config = configparser.ConfigParser()
    config.add_section(var.CONFIG_SEC_NAME_DB_CONNECT)
    config.set(var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_HOST, "localhost")
    config.set(var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_USER, "dbUser")
    config.set(var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_PSWD, "123")
    config.set(var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_DB_NAME, "diplom")
    config.set(var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_DB_CHARSET, "utf8mb4")
    with open(path, "w") as config_file:
        config.write(config_file)

def getConfigFileItem(path, section, option):
    """Извекается значение из конфигурационного файла по ключу option"""
    if not os.path.exists(path): #если по этому пути отсутствует файл, то создаем новый файл
        createConfigFile(path)
    config = configparser.ConfigParser()
    config.read(path)
    value = ""
    try:
        value = config.get(section, option)
    except configparser.NoOptionError as e:
        print("functions.py:getConfigFileItem():NoOptionError:", e)
    except configparser.NoSectionError as e:
        print("functions.py:getConfigFileItem():NoSectionError:", e)
    finally:
        return value

def updConfigFileItem(path, section, option, value):
    """Обновляем в конфигурационном файле значение по ключу option"""
    if not os.path.exists(path):
        createConfigFile(path)
    config = configparser.ConfigParser()
    config.read(path)
    config.set(section, option, value)
    with open(path, "w") as config_file:
        config.write(config_file)
