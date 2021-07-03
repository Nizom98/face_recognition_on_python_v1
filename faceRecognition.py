import functions as funcs
import storage as st
import variables as var
import switchControl as sc
import db
import time
import datetime

def allowIn2(faceData, params):
    """Функция для принятия решения о предоставлении доступа.
    args:
        faceData: - данные о пользователе перед камерой.
        params: - содержит объект для подключения к базе данных.
    """
    faceID = faceData["face_id"]
    camID = faceData["cam_id"]
    con = params["con"]
    relayName = ""
    rows, _, _ = db.query(
        con, 
        "SELECT s.`name` FROM switch2camera s2c " + 
        "INNER JOIN switches s ON s2c.switchId = s.id " +
        "WHERE s2c.camId = " + str(camID) + ";"
    )
    if len(rows) == 0:
        db.newEvent(con, "Не удалось получить имя релейного модуля для открытия двери", faceID, camID, var.EVENT_TYPE_ERROR)
        print("ERROR:", "Не удалось получить имя релейного модуля для открытия двери")
        return
    else:
        relayName = rows[0]["name"]
    updKey = {}
    updKey["id"] = faceID
    updParams= {}
    updParams["lastSession"] = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    db.updateWhere(con, "users", updParams, updKey)
    sc.sendTurnOnSignal(relayName)
    rows, _, _ = db.query(
        con, 
        "SELECT * FROM users u WHERE u.id = " + str(faceID) + ";"
    )
    if len(rows) > 0:
        print("ACCESS GRANTED, USER_ID:", faceID, ", USER_NAME:", rows[0]["nick"])
    time.sleep(2)