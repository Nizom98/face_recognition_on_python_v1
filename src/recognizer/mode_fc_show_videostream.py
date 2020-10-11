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

ENCODINGS_FACES = []
ENCODINGS_KEYS = []

def faceExist(face_encode):
    k = 0
    for face_encodings  in ENCODINGS_FACES:
        if len(face_encodings) > 0:
            results = fr.compare_faces(face_encodings, face_encode, 0.6)
            if True in results:
                return k #results.index(True)
        k += 1
    return -1

def start(q, cmd_stop):
    global ENCODINGS_FACES 
    global ENCODINGS_KEYS
    ENCODINGS_FACES, ENCODINGS_KEYS = [], []
    win_name = "window"
    next_face_num = 0
    
    while True:
        if not cmd_stop.empty():
            break
        if q.empty(): continue
        img = q.get() 
        im_copy = img.copy()
        face_encoded, face_location = funcs.getFirstEncodedAndLocationFromImg(img)
        if len(face_encoded) > 0:
            funcs.drawFaceFrame(img, face_location) 
            index = faceExist(face_encoded)
            if index == -1:
                print("NEW")
                st.newFace(str(next_face_num), face_encoded, funcs.getFaceImage(im_copy, face_location))
                next_face_num += 1
            else:
                print("MATCH")
            funcs.drawLegendFrame(img, face_location, str(index))
        cv2.imshow(win_name, img)
        if cv2.waitKey(1) == ord('q'):
            break
    print("FaceConroller: завершил работу!")
    cv2.destroyAllWindows()
    sys.exit("FaceConroller: end")