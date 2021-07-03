import os
import fnmatch
import pickle
import cv2

def getUserFaceEncodings(dirNameStorage, dirNameFaces, dirNameEncodings):
    """Из файловой системы извлекаются дескрипторы и идентификаторы лиц"""
    encodings = []
    IDs = []
    pathFaces = f"{dirNameStorage}/{dirNameFaces}"
    if not os.path.isdir(pathFaces): 
        print("ERROR: ", "Переданный параметр не является директорией", pathFaces)
        return encodings, IDs
    for dirNameFace in fnmatch.filter(os.listdir(pathFaces), '*'):
        pathEncodings = f"{pathFaces}/{dirNameFace}/{dirNameEncodings}"
        if not os.path.isdir(pathEncodings): 
            print("ERROR: ", "Переданный параметр не является директорией", pathEncodings)
            continue
        for encodeFile in fnmatch.filter(os.listdir(pathEncodings), '*.pkl'):
            encodings.append(pickle.load(open(f"{pathEncodings}/{encodeFile}", "rb")))
            IDs.append(''.join([i for i in dirNameFace if i.isdigit()]))
    print("INFO: ", "Количество знакомых лиц:", len(encodings))
    return encodings, IDs

def newFaceEncode(dirNameStorage, dirNameFaces, dirNameEncodings, dirNameImgs, id, encode, img):
    """Сохранение нового изображения лица в файловой системе"""
    print("newFaceEncode:", dirNameStorage, "=>", dirNameFaces,"=>", dirNameEncodings, "=>",dirNameImgs)
    facePath = f"{dirNameStorage}/{dirNameFaces}"
    if not os.path.isdir(dirNameStorage): 
        print("ERROR: ", "Переданный параметр не является директорией", dirNameStorage)
        return 
    elif not os.path.isdir(facePath):
        os.mkdir(facePath)
        print("INFO: ", "Создана директория: ", facePath)
    facePath = f"{facePath}/face{id}"
    encodingsPath = f"{facePath}/{dirNameEncodings}"
    imgsPath = f"{facePath}/{dirNameImgs}"
    if not os.path.isdir(facePath):
        os.mkdir(facePath)
        os.mkdir(encodingsPath)
        os.mkdir(imgsPath)
        print("INFO: ", "Созданы директории: ", facePath, ",", encodingsPath, ",", imgsPath)
    elif not os.path.isdir(encodingsPath):
        os.mkdir(encodingsPath)
        print("INFO: ", "Создана директория: ", encodingsPath)
    encodingsCount = len(os.listdir(encodingsPath))
    newEncodeFile = encodingsPath + "/" + str(encodingsCount) + ".pkl"
    pickle.dump(encode, open(newEncodeFile, "wb"))
    #сохраняем изображение лица
    if not os.path.isdir(imgsPath):
        os.mkdir(imgsPath)
        print("INFO: ", "Создана директория: ", imgsPath)
    imgsCount = len(os.listdir(imgsPath))
    cv2.imwrite(f"{imgsPath}/{imgsCount}.jpg", img)
