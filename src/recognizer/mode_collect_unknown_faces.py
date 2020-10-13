import face_recognition as fr
import os
import fnmatch
import datetime as dt
import numpy as np
import pickle
import cv2
import threading
import multiprocessing as  ml
from  src import functions as funcs
from src.storage import storage as st

#DIR_UNKNOWN_FACES = os.path.abspath(os.getcwd()) + "/../../storage/unknown_faces/"

def start(q, cmd_stop):
    next_face_num = 0
    while True:
        if not cmd_stop.empty(): break
        if q.empty(): continue
        img = q.get() 
        """
        face_encoded, face_location = funcs.getFirstEncodedAndLocationFromImg(img)
        if len(face_encoded) > 0:
            print("RECOGNIZER:found")
            face = funcs.getFaceImage(img, face_location)
            #st.saveImg(unknown_faces_dir + str(next_face_num) + ".jpg", face)
            st.saveNewUnkwnFaceImg(face)
        """
        locations = fr.face_locations(img)
        if len(locations) > 0:
            print("\nRECOGNIZER:CUFs->", len(locations))
            for loc in locations:
                face = funcs.getFaceImage(img, loc)
                st.saveNewUnkwnFaceImg(face)

