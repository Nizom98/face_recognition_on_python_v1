import face_recognition as fr
import os
import fnmatch
import datetime as dt
import numpy as np
import pickle
import cv2
import threading
import multiprocessing as  ml

from src.videoloader import videoloader as vl
from src.recognizer import recognizer as r #tt

if __name__ == '__main__':
    q = ml.Queue()
    cmd_stop = ml.Queue()
    url = "d" #input("Type camera address: ")
    if url == 'd':
        url = 'rtsp://admin:123@192.168.0.102:554/live2.sdp'
    loader = ml.Process(target=vl.start, args=(url, q, cmd_stop))
    loader.daemon = True
    loader.start()
    facecont = ml.Process(target=r.start, args=(q, cmd_stop, r.MODE_COLLECT_UNKNOWN_FACES))
    facecont.daemon = True
    facecont.start()
    while True:
        cmd = input("\ntype cmd:")
        if cmd =="s":
            cmd_stop.put(True)
            break
    print("\nMAIN: join")
    loader.join()
    facecont.join(timeout=10)
    #print(f"loader is_alive status: {loader.is_alive()}")
    #print(f"facecont is_alive status: {facecont.is_alive()}")
    print("\nMAIN: end")

