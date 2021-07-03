import functions as funcs
import storage as st
import variables as var
import switchControl as sc
import db
import time
import datetime
import multiprocessing as mlp
import cv2
import sys

def startCalibrateSingleCamera(inpParams):
    """Функция для калибровки потока одной камеры"""
    con = inpParams.get("con", None) #объект для соеденения с бд
    qFrameLoaderCmd: mlp.Queue = inpParams.get("q_loader_cmd", None) #очередь для подачи команд загрузчику видеопотока
    qFrame: mlp.Queue = inpParams.get("q_frame", None) #очередь, откуда извлекаются кадры для анализа
    qCmd: mlp.Queue = inpParams.get("q_cmd", None) #очередь для принятия команд (например, команда на остановку работы)
    qWrOnError: mlp.Queue = inpParams.get("q_wr_on_error", None)
    db.newEvent(con, "startCalibrateSingleCamera начал работу", -1, -1)
    print("CALIBRATE:", inpParams)
    fromLeft = inpParams.get("from_left", None) #текущий отсутп слева (в процентах)
    fromRight = inpParams.get("from_right", None) #текущий отступ справа (в процентах)
    if con == None or qFrame == None or qFrameLoaderCmd == None or qCmd == None or qWrOnError == None or fromLeft == None or fromRight == None:
        qWrOnError.put({"source": "calibrate"})
        return
    step = 10 #шаг движения вертикальной линии (в процентах)
    while True:
        if not qCmd.empty(): #если поступила команда
            cmd = qCmd.get()
            if cmd["cmd"] == "stop": break #если поступила команда на остановку работу
        try:
            frameData = qFrame.get(timeout=1) #данные о кадре
            img = funcs.draw2verticalLines(frameData["img"], fromLeft, fromRight)
            camID = frameData["params"]["cam_id"] #ID камеры, с которого был получен кадр
            #img = funcs.getSubImage(img, fromLeft,fromRight, 10, 10)
            cv2.imshow("CALIBRATE CAMERA " + str(camID), img)
            res = cv2.waitKey(1)
            if res == ord('q'):
                nextVal = fromLeft - step
                fromLeft = nextVal if nextVal > 0 else 1
            elif res == ord('w'):
                nextVal = fromLeft + step
                fromLeft = nextVal if nextVal < 100 else 99
            elif res == ord('a'):
                nextVal = fromRight + step
                fromRight = nextVal if nextVal < 100 else 99
            elif res == ord('s'):
                nextVal = fromRight - step
                fromRight = nextVal if nextVal > 0 else 1
            elif res == 13: #При нажатии Enter сохраняем данные о новых отсупах слева и справа
                db.updateWhere(con, "cameras", {"fromLeft" : fromLeft, "fromRight" : fromRight}, {"id" : camID})
                print("\nLines position SAVED")
                break
        except mlp.queues.Empty:
            if qFrameLoaderCmd.empty():
                qFrameLoaderCmd.put({"cmd": "get_new_frame"})
    db.newEvent(con, "startCalibrateSingleCamera завершил работу", -1, -1)
    print("INFO", "startCalibrateSingleCamera завершил работу")

