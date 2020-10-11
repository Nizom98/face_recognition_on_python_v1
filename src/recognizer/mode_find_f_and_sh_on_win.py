import face_recognition as fr
import os
import fnmatch
import datetime as dt
import numpy as np
import pickle
import cv2
import sys
import multiprocessing as  ml
from src import functions as funcs
from src.storage import storage as st

def start(q, cmd_stop):
    win_name = "window"    
    while True:
        if not cmd_stop.empty():
            break
        if q.empty(): continue
        img = q.get() 
        locations = fr.face_locations(img)
        index = 1
        for location in locations:
            funcs.drawFaceFrame(img, location) 
            funcs.drawLegendFrame(img, location, str(index))
            index += 1
        cv2.imshow(win_name, img)
        if cv2.waitKey(1) == ord('q'):
            break
    print("FaceConroller: завершил работу!")
    cv2.destroyAllWindows()
    sys.exit("FaceConroller: end")