import face_recognition as fr
import os
import fnmatch
import datetime as dt
import numpy as np
import pickle
import cv2
import src.functions as funcs

DIR_STORAGE = os.getcwd() +  "/storage"
DIR_FACE_IMGS = "imgs"
DIR_FACES = "known_faces"
DIR_FACE_ENCODINGS = "encodings"
DIR_UNKNOWN_FACES = "unknown_faces"

def newFace(name, face_encode, img):
    faces_len = len(os.listdir(DIR_FACES))
    newDir = DIR_STORAGE + "/" + DIR_FACES + "/face" + str(faces_len + 1)
    os.mkdir(newDir)
    dir_encodings = newDir + "/" + DIR_FACE_ENCODINGS 
    os.mkdir(dir_encodings)
    pickle.dump(face_encode, open(dir_encodings + "/" + name + ".pkl", "wb"))
    dir_imgs = newDir + "/" + DIR_FACE_IMGS
    os.mkdir(dir_imgs)
    cv2.imwrite(f"{dir_imgs}/{name}.jpg", img)
    return dir_encodings

def saveNewUnkwnFaceImg(img):
    unfacedir = DIR_STORAGE + "/" + DIR_UNKNOWN_FACES + "/"
    return cv2.imwrite(funcs.getNextName(unfacedir), img)

def add2faceImgs(face_dir_name, arr_face_im):
    path2dir = f"{DIR_STORAGE}/{DIR_FACES}/{face_dir_name}"
    if not os.path.isdir(path2dir):
        os.mkdir(path2dir)
    path2dir = f"{path2dir}/{DIR_FACE_IMGS}"
    if not os.path.isdir(path2dir):
        os.mkdir(path2dir)
    for face_im in np.nditer(arr_face_im):
        cv2.imwrite(funcs.getNextName(path2dir), face_im)

"""
def add2faceImgs(face_dir_name, arr_face_im, arr_face_en):
    path2faceDir = f"{DIR_STORAGE}/{DIR_FACES}/{face_dir_name}"
    if not os.path.isdir(path2faceDir):
        os.mkdir(path2faceDir)
    path2faceImDir = f"{path2faceDir}/{DIR_FACE_IMGS}"
    if not os.path.isdir(path2faceImDir):
        os.mkdir(path2faceImDir)
    path2faceEnDir = f"{path2faceDir}/{DIR_FACE_ENCODINGS}"
    if not os.path.isdir(path2facpath2faceEnDireImDir):
        os.mkdir(path2faceEnDir)
    for en, face_img in zip(arr_face_en, arr_face_im):
        
    cv2.imwrite(funcs.getNextName(unfacedir), img)
"""
    

def loadImgs():
    faces_encodings = []
    keys_encodings = [] 
    for dir_face in os.listdir(DIR_STORAGE + "/" + DIR_FACES):
        encodings = []
        dir_encodings = f"{DIR_STORAGE}/{DIR_FACES}/{dir_face}/{DIR_FACE_ENCODINGS}"
        for encode in os.listdir(dir_encodings):
            encodings.append(pickle.load(open(f"{dir_encodings}/{encode}", "rb"))) 
        if len(encodings) > 0:
            faces_encodings.append(encodings)
            keys_encodings.append(dir_encodings)
    return faces_encodings, keys_encodings
