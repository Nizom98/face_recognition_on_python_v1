import face_recognition as fr
import os
import fnmatch
import datetime as dt
import numpy as np
import pickle
import cv2
import threading
import multiprocessing as  ml
import src.recognizer.mode_collect_unknown_faces as cuf
import src.recognizer.mode_fc_show_videostream as fcsvs
import src.recognizer.mode_find_f_and_sh_on_win as findsFaces


MODE_COLLECT_UNKNOWN_FACES = 1
MODE_FACECONTROL_SHOW_VIDEOSTREAM = 2

#find faces and draw frame and legend
MODE_FFS_DF_DL_OTW = 3 #find faces and draw frame and legend
#VSI  video stream image
#FFs - find faces
#SFsI2UD - save faces image to unknown directory
MODE_VSI_FFs_SFsI2UD = 4


def start(q, cmd_stop, mode):
    if mode == MODE_COLLECT_UNKNOWN_FACES:
        cuf.start(q, cmd_stop)
    elif mode == MODE_FACECONTROL_SHOW_VIDEOSTREAM:
        fcsvs.start(q, cmd_stop)
    elif mode == MODE_FFS_DF_DL_OTW:
        findsFaces.start(q, cmd_stop)
    else:
        print("RECOGNIZER:Неправильный режим работы!!!!")
        print("RECOGNIZER:__END__")

