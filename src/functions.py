import face_recognition as fr
import os
import fnmatch
import numpy as np
import pickle
import cv2

def getFirstEncodedAndLocation(encodings, locations):
    if len(encodings) == 0 or len(locations) == 0:
        return [], []
    return encodings[0], locations[0]

def getFirstEncodedAndLocationFromImg(img):
    locations = fr.face_locations(img)
    encodings = fr.face_encodings(img, locations)
    return getFirstEncodedAndLocation(encodings, locations)

def getFaceImage(img, loc):
    top, right, bottom, left = loc
    return img[top:bottom, left:right]

def drawFaceFrame(img, loc):
    top, right, bottom, left = loc
    line_len = 20
    thikness = 2
    img = cv2.line(img, (left, top), (left + line_len, top), (0, 255, 0), thikness) #левая верхняя горизонтальная линия
    img = cv2.line(img, (left, top), (left, top + line_len), (0, 255, 0), thikness) #левая верхняя вертикальная линия
    img = cv2.line(img, (left, bottom), (left, bottom - line_len), (0, 255, 0), thikness) #левая нижняя вертикальная линия
    img = cv2.line(img, (left, bottom), (left + line_len, bottom), (0, 255, 0), thikness) #левая нижняя горизонтальная линия
    img = cv2.line(img, (right, bottom), (right - line_len, bottom), (0, 255, 0), thikness) #правая нижняя горизонтальная линия
    img = cv2.line(img, (right, bottom), (right, bottom - line_len), (0, 255, 0), thikness) #правая нижняя вертикальная линия
    img = cv2.line(img, (right, top), (right, top + line_len), (0, 255, 0), thikness) #правая верхняя вертикальная линия
    img = cv2.line(img, (right, top), (right - line_len, top), (0, 255, 0), thikness) #правая верхняя горизонтальная линия
    return img

def drawLegendFrame(img, loc, text):
    top, right, bottom, left = loc
    top_left = (left, top)
    bottom_right = (right, bottom + 22)
    cv2.rectangle(img, (left, bottom + 22), (right, bottom), (0, 0, 255), cv2.FILLED)
    #cv2.rectangle(img, top_left, bottom_right, [0, 255, 0], 2)
    cv2.putText(img, text, (left + 6, bottom + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return img

def saveImg(path_plus_name, img):
    cv2.imwrite(path_plus_name, img)

def getNextName(path2dir, type = ".jpg"):
    fcount = len(os.listdir(path2dir)) + 1
    fname = path2dir + str(fcount) + type
    while os.path.exists(fname):
        fcount += 1
        fname = path2dir + str(fcount) + type
    return fname