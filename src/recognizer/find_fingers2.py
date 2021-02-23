import face_recognition as fr
import os
import fnmatch
import datetime as dt
import numpy as np
import pickle
import cv2
import threading
import multiprocessing as  ml
import math
from  src import functions as funcs
from src.storage import storage as st

#DIR_UNKNOWN_FACES = os.path.abspath(os.getcwd()) + "/../../storage/unknown_faces/"

def start(q, cmd_stop):
    next_face_num = 0
    while True:
        if not cmd_stop.empty(): break
        if q.empty(): continue
        frame = q.get()
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) 
        _, the = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
        cv2.imshow('thresh',the)
        print("f2:", the)
        cpy = the.copy()
        _, contours, _ = cv2.findContours(the, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        hull = [cv2.convexHull(c) for c in contours]
        final = cv2.drawContours(frame, hull, -1, (255,0,0))
        cv2.imshow('original',frame)
        cv2.imshow('hull',final)
        if cv2.waitKey(1) == ord('q'):
            break
cv2.destroyAllWindows()
        
