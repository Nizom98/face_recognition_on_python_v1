
import functions as funcs
import storage as st
from urllib.request import urlopen
import cv2
import db
import variables as var
import os
import imghdr
import pathlib
import json
import cv2

def newFacesFromJsonFile(path2file: str, con):
    try:
        if not os.path.isfile(path2file):
            return [{"error" : "Параметр не является файлом"}]
        elif pathlib.Path(path2file).suffix != ".json":
            print(pathlib.Path(path2file).suffix)
            return [{"error" : "Файл должен быть типа json"}]
        file = open(path2file, 'r')
        fileData = file.read()
        data = json.loads(fileData)
    except FileNotFoundError as e:
        return [{"error" : e}]
    except json.decoder.JSONDecodeError as e:
        return [{"error" : e}]
    return newFacesFromData(data, con)

def newFacesFromData(data: dict, con):
    """Добавление даннах о новом лице в файловую систему и в бд"""
    errs = []
    for faceData in data.get("new_faces", []):
        nick = str(faceData.get("nick", "")) #никнейм нового лица
        if nick == "":
            errs.append({"error": "Имя не может быть пустым", "data": str(faceData)})
            continue
        print("NICK:", nick)
        paths = faceData.get("paths", []) #список путей до изображения лица
        imgs = faceData.get("imgs", []) #список изображений с лицами
        if type(paths) != list:
            errs.append({"error": "Не обнаружили список фотографий", "data": faceData})
            continue
        elif len(paths) == 0 and len(imgs) == 0:
            errs.append({"error": "Пустой список фотографий", "data": faceData})
            continue
        print("PATHS:", paths)
        faceImgs = []
        faceEncs = []
        for path in paths:
            if not os.path.isfile(path):
                print("ERROR: фотография не найдена:", path)
                continue
            elif imghdr.what(path) != "jpeg":
                print("ERROR: некорректный тип файла:", path)
                continue
            #print("PATHS_ITEM:", path)
            img  = cv2.imread(path)
            encs, locs = funcs.getAllEncodingsAndLocationsFromImg(img)
            faceCount = len(encs)
            #print("faceCount:", faceCount)
            if faceCount != 1:
                print("ERROR: количество лиц на фотографии не равно 1:", faceCount, path)
                continue
            faceImgs.append(funcs.getFaceImage(img, locs[0]))
            faceEncs.append(encs[0])
        #print("IMGS00:", len(imgs))
        for img in imgs:
            encs, locs = funcs.getAllEncodingsAndLocationsFromImg(img)
            faceCount = len(encs)
            print("IMGS:", faceCount)
            #print("faceCount:", faceCount)
            if faceCount != 1:
                print("ERROR: количество лиц на фотографии не равно 1:", faceCount, path)
                continue
            faceImgs.append(funcs.getFaceImage(img, locs[0]))
            faceEncs.append(encs[0])
        if len(faceEncs) == 0:
            errs.append({"error": "Количество корректных фотографий равно нулю", "data": faceData})
            continue
        elif len(faceEncs) > 1 and funcs.isSameFaceEncodings(faceEncs[1:], faceEncs[0]) == False:
            errs.append({"error": "Лица на фотографиях не пренадлежат одному человеку", "data": faceData})
            continue
        #print("ENCS_LEN:", len(faceEncs))
        count, newUserID = db.insertInto(con, "users", {"nick" : nick})
        if count < 1 or newUserID == -1:
            #print("INS:", count, newUserID)
            errs.append({"error": "Не удалось сохранить данные пользователя в БД", "data": faceData})
            continue
        dirSt, dirFace, dirEncs, dirImgs = db.getStorageParams(con)
        for enc, img in zip(faceEncs, faceImgs):
            st.newFaceEncode(dirSt, dirFace, dirEncs, dirImgs, str(newUserID), enc, img)
    return errs

#print("ERR:", newFacesFromJsonFile("data.json", db.getConnnection()))


# con = db.getConnnection()
# print(newFace(con, "nick--3", ["./p1.jpg", "./p2.jpg", "./p3.jpg"]))
    
