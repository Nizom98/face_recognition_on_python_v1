import face_recognition as fr
import os
import fnmatch
import datetime as dt
import numpy as np
import pickle
import cv2
import multiprocessing as  ml

import faceRecognition as fr
import frameLoader as fl
import calibrateCamera as calibr
import db
import variables as var
import functions as funcs
def getCommandLineArgs(args: list):
    error = ""
    try:
        opts, ar = getopt.getopt(args, 'm:i:f:')
    except getopt.GetoptError as e:
        error = e.msg
        opts = []
    modes = [v for k, v in opts if k == "-m"]
    nicks = [v for k, v in opts if k == "-n"]
    imgs = [v for k, v in opts if k == "-i"]
    files = [v for k, v in opts if k == "-f"]
    return error, modes, nicks, imgs, files
    


import sys 
import getopt
import newFace
if __name__ == '__main__':
    error, modes, nicks, imgs, files = getCommandLineArgs(sys.argv[1:])
    mode = "" if len(modes) == 0 else modes[0]
    nick = "" if len(nicks) == 0 else nicks[0]
    con = db.getConnnection()
    if error != "":
        print(error)
    elif con == None:
        print("\nНе удалось подключиться к базе данных")
    elif mode == var.KEY_MODE_NEW_FACE: #режим добавления данные о новых пользователя с использованием файла
        if len(files) == 0:
            print("\nВведите путь к файлу с данными о новых пользователей (флаг -f)")
            sys.exit(0)
        errs = newFace.newFacesFromJsonFile(str(files[0]), con)
        if len(errs) > 0: print("\nERRORS:", errs)
        else: print("\nDONE")
    elif mode == var.KEY_MODE_RECOGNIZER: #режим распознавания с помощью одной камеры
        cams, count, lastID = db.query(con, "SELECT DISTINCT * FROM cameras c WHERE c.active = 1 LIMIT 1;")
        print("\nДаd", cams)
        if len(cams) < 1:
            print("\nДанные о камерах не обнаружены")
            exit(0)
        frameLoaders = []
        frameReaders = []
        qWrOnError = ml.Queue()
        for cam in cams:
            camData = {}
            camData["cam_id"] = cam.get("id")
            loaderParams = {}
            loaderParams["cam_connect_str"] = cam["connectStr"]
            loaderParams["con"] = con
            qLoaderCmd = ml.Queue()
            qFrame = ml.Queue()
            newLoader = ml.Process(target=fl.startLoadFrames, args=(loaderParams, qFrame, qLoaderCmd, qWrOnError, camData))
            newLoader.daemon = True
            newLoader.start()
            frameLoaders.append({"sub_process" : newLoader, "q_loader_cmd" : qLoaderCmd, "q_frame" : qFrame})
            qReaderCmd = ml.Queue()
            callParams = {}
            callParams["con"] = con
            readerParams = {}
            readerParams["con"] = con
            readerParams["q_frame"] = qFrame
            readerParams["q_loader_cmd"] = qLoaderCmd
            readerParams["q_wr_on_error"] = qWrOnError
            readerParams["q_cmd"] = qReaderCmd
            newReader = ml.Process(target=fl.startReaderRecognizer , args=(readerParams, callParams, fr.allowIn2))
            newReader.daemon = True
            newReader.start()
            frameReaders.append({"sub_process" : newReader, "q_reader_cmd" : qReaderCmd})
        while True:
            if not qWrOnError.empty():
                errData = qWrOnError.get(timeout=1)
                for loader in frameLoaders:
                    loader.get("q_loader_cmd").put({"cmd": "stop"})
                    loader.get("sub_process").join()
                    print("\nLOADER_JOINED")
                for reader in frameReaders:
                    loader.get("q_reader_cmd").put({"cmd": "stop"})
                    loader.get("sub_process").join()
                    print("\nREADER_JOINED")
        print("\nENDED")
    elif mode == var.KEY_MODE_NEW_FACE_FROM_CAM: #режим добавления данные о новых пользователя с использованием камеры
        cams, count, lastID = db.query(con, "SELECT DISTINCT * FROM cameras c WHERE c.active = 1 LIMIT 1;")
        if len(cams) < 1:
            print("\nДанные о камерах не обнаружены")
            exit(0)
        frameLoaders = []
        frameReaders = []
        qWrOnError = ml.Queue()
        for cam in cams:
            camData = {}
            camData["cam_id"] = cam.get("id")
            loaderParams = {}
            loaderParams["cam_connect_str"] = cam["connectStr"]
            loaderParams["con"] = con
            qLoaderCmd = ml.Queue()
            qFrame = ml.Queue()
            newLoader = ml.Process(target=fl.startLoadFrames, args=(loaderParams, qFrame, qLoaderCmd, qWrOnError, camData))
            newLoader.daemon = True
            newLoader.start()
            frameLoaders.append({"sub_process" : newLoader, "q_loader_cmd" : qLoaderCmd, "q_frame" : qFrame})
            qReaderCmd = ml.Queue()
            callParams = {}
            callParams["con"] = con
            readerParams = {}
            readerParams["con"] = con
            readerParams["q_frame"] = qFrame
            readerParams["q_loader_cmd"] = qLoaderCmd
            readerParams["q_wr_on_error"] = qWrOnError
            readerParams["q_cmd"] = qReaderCmd
            fl.startReaderNewFace(readerParams)
        while True:
            if not qWrOnError.empty():
                errData = qWrOnError.get(timeout=1)
                for loader in frameLoaders:
                    loader.get("q_loader_cmd").put({"cmd": "stop"})
                    loader.get("sub_process").join()
                    print("\nLOADER_JOINED")
        print("\nENDED")
    elif mode == var.KEY_MODE_RECOGNIZER_BY_2_CAMS: #режим распознавания с помощью двух камер
        cams, count, lastID = db.query(con, "SELECT DISTINCT * FROM cameras c WHERE c.active = 1 LIMIT 2;")
        if len(cams) < 2:
            print("\nДанные о камерах не обнаружены")
            exit(0)
        frameLoaders = []
        frameReaders = []
        qWrOnError = ml.Queue()

        for cam in cams:
            camData = {}
            camData["cam_id"] = cam.get("id")
            loaderParams = {}
            loaderParams["cam_connect_str"] = cam["connectStr"]
            loaderParams["con"] = con
            qLoaderCmd = ml.Queue()
            qFrame = ml.Queue()
            newLoader = ml.Process(target=fl.startLoadFrames, args=(loaderParams, qFrame, qLoaderCmd, qWrOnError, camData))
            newLoader.daemon = True
            newLoader.start()
            frameLoaders.append({"sub_process" : newLoader, "q_loader_cmd" : qLoaderCmd, "q_frame" : qFrame})
            
        qReaderCmd = ml.Queue()
        callParams = {}
        callParams["con"] = con
        readerParams = {}
        readerParams["con"] = con
        readerParams["q_frame_first"] = frameLoaders[0].get("q_frame")
        readerParams["q_frame_sec"] = frameLoaders[1].get("q_frame")
        readerParams["q_loader_cmd_first"] = frameLoaders[0].get("q_loader_cmd")
        readerParams["q_loader_cmd_sec"] = frameLoaders[1].get("q_loader_cmd")
        readerParams["q_wr_on_error"] = qWrOnError
        readerParams["q_cmd"] = qReaderCmd
        readerParams["first_left"] = cams[0]["fromLeft"]
        readerParams["first_right"] = cams[0]["fromRight"]
        readerParams["sec_left"] = cams[1]["fromLeft"]
        readerParams["sec_right"] = cams[1]["fromRight"]
        newReader = ml.Process(target=fl.startReaderRecognize2cams, args=(readerParams, callParams, fr.allowIn2))
        newReader.daemon = True
        newReader.start()
        
        while True:
            if not qWrOnError.empty():
                errData = qWrOnError.get(timeout=1)
                for loader in frameLoaders:
                    loader.get("q_loader_cmd").put({"cmd": "stop"})
                    loader.get("sub_process").join()
                    print("\nLOADER_JOINED")
                newReader.join()
                print("\nREADER_JOINED")
        print("\nMAIN_END")

    elif mode == var.KEY_MODE_CALIBRATE: #режим калибровки
        cams, count, lastID = db.query(con, "SELECT DISTINCT * FROM cameras c WHERE c.active = 1 LIMIT 2;")
        if len(cams) < 1:
            print("\nДанные о камерe не обнаружены")
            exit(0)
        frameLoaders = []
        frameReaders = []
        qWrOnError = ml.Queue()
        for cam in cams:
            camData = {}
            camData["cam_id"] = cam.get("id")
            loaderParams = {}
            loaderParams["cam_connect_str"] = cam["connectStr"]
            loaderParams["con"] = con
            qLoaderCmd = ml.Queue()
            qFrame = ml.Queue()
            newLoader = ml.Process(target=fl.startLoadFrames, args=(loaderParams, qFrame, qLoaderCmd, qWrOnError, camData))
            newLoader.daemon = True
            newLoader.start()
            frameLoaders.append({"sub_process" : newLoader, "q_loader_cmd" : qLoaderCmd, "q_frame" : qFrame})

            qReaderCmd = ml.Queue()
            callParams = {}
            callParams["con"] = con
            readerParams = {}
            readerParams["con"] = con
            readerParams["from_left"] = cam["fromLeft"]
            readerParams["from_right"] = cam["fromRight"]
            readerParams["q_frame"] = qFrame
            readerParams["q_loader_cmd"] = qLoaderCmd
            readerParams["q_wr_on_error"] = qWrOnError
            readerParams["q_cmd"] = qReaderCmd
            newReader = ml.Process(target=calibr.startCalibrateSingleCamera, args=[readerParams])
            newReader.daemon = True
            newReader.start()
            frameReaders.append({"sub_process" : newReader, "q_reader_cmd" : qReaderCmd})
        while True:
            if not qWrOnError.empty():
                errData = qWrOnError.get(timeout=1)
                for loader in frameLoaders:
                    loader.get("q_loader_cmd").put({"cmd": "stop"})
                    loader.get("sub_process").join()
                    print("\nLOADER_JOINED")
                for reader in frameReaders:
                    loader.get("q_reader_cmd").put({"cmd": "stop"})
                    loader.get("sub_process").join()
                    print("\nREADER_JOINED")
        print("\nENDED")
    else:
        print(var.INSTRUCTION) #вывод инструкции