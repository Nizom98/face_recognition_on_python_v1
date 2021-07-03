import multiprocessing as mlp
import cv2
import functions as funcs
import face_recognition as fr
import storage
import variables as vars
import db
import newFace
import sys

def startLoadFrames(inp_params, qFrame: mlp.Queue, qCmd: mlp.Queue, qWrOnError: mlp.Queue, params: dict):
    """Перехват видеопотока с камеры видеонаблюдения"""
    url = inp_params["cam_connect_str"]
    con = inp_params["con"]
    camID = params["cam_id"]
    if url.isdigit(): url = 0
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print("ERROR", "FrameLoader: не удалось открыть видеопоток! Проверьте правильность url адреса:" + str(url))
        qWrOnError.put({"source": "fl", "cam_id": camID})
        return
    frameData = {}
    frameData["params"] = params
    print("INFO", "FrameLoader начал работу")
    db.newEvent(con, "FrameLoader начал работу, url:" + str(url), -1, camID)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, int(1))
    cap.set(cv2.CAP_PROP_FPS, int(10))
    while True:
        ok, img = cap.read()
        if not qCmd.empty():
            cmd = qCmd.get()
            if ok and cmd["cmd"] == "get_new_frame" and qFrame.empty():
                img = cv2.flip(img, 1)
                frameData["img"] = img
                qFrame.put(frameData)
            elif cmd["cmd"] == "stop": break
    cap.release()
    print("INFO", "FrameLoader завершил работу")
    db.newEvent(con, "FrameLoader завершил работу, url:" + str(url), -1, camID)
    return

def startReaderRecognizer(inpParams, funcParams, nextFunc):
    """Коннтроль доступа с использованием одной камеры"""
    qFrame: mlp.Queue = inpParams.get("q_frame", None)
    con = inpParams.get("con" , None)
    qWrOnError: mlp.Queue = inpParams.get("q_wr_on_error", None)
    qFrameLoaderCmd: mlp.Queue = inpParams.get("q_loader_cmd", None)
    qCmd: mlp.Queue = inpParams.get("q_cmd", None)
    if qFrame == None or con == None or qFrameLoaderCmd == None or qCmd == None or qWrOnError == None:
        print("ERROR: ", "startReaderRecognizer: ", "Отсутсвуют входный параметры")
        qWrOnError.put({"source": "reader_recognizer"})
        return
    db.newEvent(con, "startReaderRecognizer начал работу", -1, -1)
    print("INFO", "startReaderRecognizer: ", "начал работу")

    dirSt, dirFace, dirEncs, _ = db.getStorageParams(con)
    FACES_ENCODINGS, FACES_IDS = storage.getUserFaceEncodings(dirSt, dirFace, dirEncs)
    squareWidth = -1
    x, y = 0, 0
    
    while True:
        analysis = True
        if not qCmd.empty():
            cmd = qCmd.get()
            if cmd["cmd"] == "stop": break
        try:
            frameData = qFrame.get(timeout=1)
            camID = frameData["params"].get("cam_id", "")
            if squareWidth == -1: squareWidth, x, y = funcs.getSquareWidth(frameData["img"])
            img = funcs.drawSquareCentered(frameData["img"], x, y, squareWidth)
            analyzeArea = img[y:y+squareWidth, x:x+squareWidth]
            
            #keyNum = cv2.waitKey(1)
            encs, locs = funcs.getAllEncodingsAndLocationsFromImg(analyzeArea)
            analysis = len(encs) != 0
            faceID = funcs.getFaceIdByEncode(FACES_ENCODINGS, FACES_IDS, encs[0]) if analysis else -1
            if str(faceID) != "-1":
                funcs.outUnderSquareLegend(img, x, y, squareWidth, str(faceID))
                #print("FOUND_FACE_ID22222:", faceID)
                cv2.imshow("CAMERA " + str(camID), img)
                cv2.waitKey(1)
                faceData = {}
                faceData["img"] = analyzeArea
                faceData["face_id"] = faceID 
                faceData["face_locs"] = locs[0]
                faceData["cam_id"] = frameData['params']["cam_id"]
                print("FOUND_FACE_ID:", faceID)
                nextFunc(faceData, funcParams)
            else:
                funcs.outUnderSquareLegend(img, x, y, squareWidth)
                cv2.imshow("CAMERA " + str(camID), img)
                print("NO_ID")
                cv2.waitKey(1)
        except mlp.queues.Empty:
            if qFrameLoaderCmd.empty():
                qFrameLoaderCmd.put({"cmd": "get_new_frame"})
    db.newEvent(con, "startReaderRecognizer завершил работу", -1, -1)
    print("INFO", "startReaderRecognizer: ", "завершил работу")

def startReaderRecognize2cams(inpParams, funcParams, nextFunc):
    """Контроль доступа с использованием двух камер"""
    qFrameFirst: mlp.Queue = inpParams.get("q_frame_first", None)
    qFrameSec: mlp.Queue = inpParams.get("q_frame_sec", None)
    con = inpParams.get("con", None)
    firstLeft = inpParams.get("first_left", 1)
    firstRight = inpParams.get("first_right", 1)
    secLeft = inpParams.get("sec_left", 1)
    secRight = inpParams.get("sec_right", 1)
    qFrameLoaderCmdFirst: mlp.Queue = inpParams.get("q_loader_cmd_first", None)
    qFrameLoaderCmdSec: mlp.Queue = inpParams.get("q_loader_cmd_sec", None)
    qCmdListen: mlp.Queue = inpParams.get("q_cmd", None)
    qWrOnError: mlp.Queue = inpParams.get("q_wr_on_error", None)
    if qFrameFirst == None or con == None or qFrameLoaderCmdFirst == None or qCmdListen == None or qFrameSec == None or qFrameLoaderCmdSec == None:
        print("ERROR: ", "startReaderRecognize2cams: ", "Отсутсвуют входные параметры")
        qWrOnError.put({"source": "reader_recognizer2cams"})
        return

    db.newEvent(con, "startReaderRecognize2cams начал работу", -1, -1)
    print("INFO: ", "startReaderRecognize2cams: ", "начал работу",)

    dirSt, dirFace, dirEncs, _ = db.getStorageParams(con)
    FACES_ENCODINGS, FACES_IDS = storage.getUserFaceEncodings(dirSt, dirFace, dirEncs)

    while True:
        analysis = True
        if not qCmdListen.empty():
            cmd = qCmdListen.get()
            if cmd["cmd"] == "stop": break
        try:
            frameDataFirst = qFrameFirst.get(timeout=1)
            frameDataSec = qFrameSec.get(timeout=1)
            img1 = funcs.getSubImage(frameDataFirst["img"], firstLeft, firstRight)
            img2 = funcs.getSubImage(frameDataSec["img"], secLeft, secRight)
            encs1, locs1 = funcs.getAllEncodingsAndLocationsFromImg(img1)
            #analysis = len(encs1) == 1
            encs2, _ = funcs.getAllEncodingsAndLocationsFromImg(img2)
            analysis = len(encs1) == 1 and len(encs2) == 1
            print("FACE_FOUND", len(encs1), len(encs2))
            if analysis and not funcs.isSameFaceEncodings(encs1, encs2[0]): analysis = False
            img1line = funcs.draw2verticalLines(frameDataFirst["img"], firstLeft, firstRight)
            img2line = funcs.draw2verticalLines(frameDataSec["img"], secLeft, secRight)
            cv2.imshow("CAMERA " + str(frameDataFirst['params']["cam_id"]), img1line)
            cv2.imshow("CAMERA " + str(frameDataSec['params']["cam_id"]), img2line)
            res = cv2.waitKey(1)
            faceID = "-1"
            if analysis:
                faceID = funcs.getFaceIdByEncode(FACES_ENCODINGS, FACES_IDS, encs1[0]) 
            if str(faceID) != "-1":
                faceData = {}
                faceData["img"] = img1
                faceData["face_id"] = faceID
                faceData["face_locs"] = locs1[0]
                faceData["cam_id"] = frameDataFirst['params']["cam_id"]
                print("FOUND_FACE_ID:", faceID)
                nextFunc(faceData, funcParams)
        except mlp.queues.Empty:
            while not qFrameFirst.empty(): qFrameFirst.get()
            while not qFrameSec.empty(): qFrameSec.get()
            if qFrameLoaderCmdFirst.empty(): qFrameLoaderCmdFirst.put({"cmd": "get_new_frame"})
            if qFrameLoaderCmdSec.empty(): qFrameLoaderCmdSec.put({"cmd": "get_new_frame"})
    db.newEvent(con, "startReaderRecognize2cams завершил работу", -1, -1)
    print("INFO: ", "startReaderRecognize2cams: ", "завершил работу")

def startReaderNewFace(inpParams):
    """Добавление данных о новом пользователе с использованием одной камеры"""
    qFrame: mlp.Queue = inpParams.get("q_frame", None)
    con = inpParams.get("con" , None)

    qFrameLoaderCmd: mlp.Queue = inpParams.get("q_loader_cmd", None)
    qCmd: mlp.Queue = inpParams.get("q_cmd", None)
    if qFrame == None or con == None or qFrameLoaderCmd == None or qCmd == None:
        print("ERROR: ", "startReaderNewFace: ", "Отсутсвуют входные параметры")
        exit(0)        
    db.newEvent(con, "startReaderNewFace начал работу", -1, -1)
    print("INFO", "startReaderNewFace: ", "начал работу")
    squareWidth = -1
    x, y = 0, 0
    while True:
        if not qCmd.empty():
            cmd = qCmd.get()
            if cmd["cmd"] == "stop": break
        try:
            frameData = qFrame.get(timeout=1)
            camID = frameData["params"].get("cam_id", "")
            if squareWidth == -1: squareWidth, x, y = funcs.getSquareWidth(frameData["img"])
            img = funcs.drawSquareCentered(frameData["img"], x, y, squareWidth)
            cv2.imshow("CAMERA " + str(camID), img)
            keyNum = cv2.waitKey(1)
            if keyNum == 13:
                encs, _ = funcs.getAllEncodingsAndLocationsFromImg(img)
                if len(encs) != 1:
                    print("\nДопустимое количество лиц в кадре: 1")
                    continue
                nick = ""
                while nick == "":
                    nick = input("\nВведите никнейм пользователя:")
                    print("\nNICK:", nick)
                data = {
                    "new_faces" : [  
                        {
                            "nick" : nick,
                            "imgs" : [img]
                        }
                    ]
                }
                errs = newFace.newFacesFromData(data, con)
                if len(errs) > 0: print("\nERRORS:", errs)
                else: print("\nDONE")
        except mlp.queues.Empty:
            if qFrameLoaderCmd.empty():
                qFrameLoaderCmd.put({"cmd": "get_new_frame"})
    db.newEvent(con, "startReaderNewFace завершил работу", -1, -1)
    print("INFO", "startReaderNewFace: ", "завершил работу")