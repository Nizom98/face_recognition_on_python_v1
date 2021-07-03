CONFIG_SEC_NAME_STORAGE = "STORAGE"
KEY_DIR_NAME_STORAGE = "dir_name_storage"
KEY_DIR_NAME_FACES = "dir_name_faces"
KEY_DIR_NAME_ENCODINGS = "dir_name_encodings"
KEY_DIR_NAME_IMGS = "dir_name_imgs"

KEY_MODE_NEW_FACE = "new_face_file"
KEY_MODE_RECOGNIZER = "recognizer"
KEY_MODE_RECOGNIZER_BY_2_CAMS = "recognizer2cams"
KEY_MODE_CALIBRATE = "calibrate"
KEY_MODE_NEW_FACE_FROM_CAM = "new_face_cam"

CONFIG_SEC_NAME_DB_CONNECT = "DB_CONNECT"
KEY_CONFIG_ITEM_HOST = "host"
KEY_CONFIG_ITEM_USER = "user"
KEY_CONFIG_ITEM_PSWD = "password"
KEY_CONFIG_ITEM_DB_NAME = "db_name"
KEY_CONFIG_ITEM_DB_CHARSET = "db_charset"

CONFIG_FILE_NAME = "settings.ini"
CONFIG_FILE_PATH = "./" + CONFIG_FILE_NAME

EVENT_TYPE_INFO = "1"
EVENT_TYPE_WARNING = "2"
EVENT_TYPE_ERROR = "3"

#данные для подачи команд считывателю видеопотока из ip - кмеры
#Q - queue, FL - frame loader, LNF - load new frame
P_KEY_CMD = "cmd" #ключ, по которому находится команда
P_CMD_STOP = "stop" #команда на остановку работы
P_CMD_LNF = "get_new_frame" #команда для получения нового кадра
P_ERR_KEY_SOURCE = "source"
P_ERR_KEY_MSG = "source"

P_KEY_DB_CON = "con"
P_KEY_CAM_ID = "cam_id"
P_KEY_CAM_URL = "url"

P_KEY_FROM_LEFT = "left"
P_KEY_FROM_RIGHT = "right"

P_KEY_Q_FIRST = "right"
P_KEY_Q_SECOND = "sec"
P_KEY_Q_CMD = "q_cmd"

P_KEY_IMG = "img"
P_KEY_FACE_ID = "face_id"
P_KEY_FACE_LOCS = "face_locs"

P_KEY_SUB_PROCESS = "face_locs"



INSTRUCTION = """
---Краткая инструкция---
Используемые флаги:
-m  :выбор режима работа программы
    Режимы работы программы:
    1) """ + KEY_MODE_NEW_FACE + """ - добавление данных о новых 
        пользователя с использованием файла типа JSON
    2) """ + KEY_MODE_NEW_FACE_FROM_CAM + """ - добавление данных о новых 
        пользователя с использованием камеры видеонаблюдения
    3) """ + KEY_MODE_CALIBRATE + """ - режим калибровки.
    4) """ + KEY_MODE_RECOGNIZER + """ - режим управления доступом с использованием
        одной камеры видеонаблюдения.
    5) """ + KEY_MODE_RECOGNIZER_BY_2_CAMS + """ - режим управления доступом с использованием
        двух камер видеонаблюдения.
-f  :путь к файлу, где находятся данные о новых пользователях 
    (используется для режима """ + KEY_MODE_NEW_FACE + """)
    Например, '/home/newData.json'

Пример запуска программы в режиме """ + KEY_MODE_NEW_FACE + """:
    'sudo main2 -m """ + KEY_MODE_NEW_FACE + """ -f "/home/newData.json"'
Пример запуска программы в режиме """ + KEY_MODE_RECOGNIZER + """:
    'sudo main2 -m """ + KEY_MODE_RECOGNIZER + """ 
"""
