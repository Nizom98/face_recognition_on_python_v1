import face_recognition as fr
import os
import fnmatch
import datetime as dt
import numpy as np
import pickle
import cv2
import sys

def start(url, q, cmd_stop): 
    video = cv2.VideoCapture(url)
    if not video.isOpened():
        print("\nVideoLoader: не удалось открыть видеопоток! Проверьте правильность url адреса.")
        cmd_stop.put(True);
        return
    print("\nVideoLoader:start")
    while True:
        ok, img = video.read()
        if ok and q.empty():
            q.put(img)
        if not cmd_stop.empty():
            break
    video.release()
    print("\nVideoLoader: завершил работу!")
    sys.exit("VideoLoader: end")
