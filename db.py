import pymysql
import variables as var
import functions as funcs
import datetime
 

def getConnnection(path = var.CONFIG_FILE_PATH):
    #print("gg",funcs.getConfigFileItem(path, var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_PSWD))
    try:
        con = pymysql.connect(
            host=funcs.getConfigFileItem(path, var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_HOST), 
            user=funcs.getConfigFileItem(path, var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_USER), 
            password=funcs.getConfigFileItem(path, var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_PSWD),
            database=funcs.getConfigFileItem(path, var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_DB_NAME), 
            charset=funcs.getConfigFileItem(path, var.CONFIG_SEC_NAME_DB_CONNECT, var.KEY_CONFIG_ITEM_DB_CHARSET), 
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.err.OperationalError as e:
        print("ERROR:cannot connect to database", e)
        return None
    return con

def getTableCols(con, table):
    cur = con.cursor()
    cur.execute("show columns from " + str(table) + ";")
    rows = cur.fetchall()
    cols = [i["Field"] for i in rows]
    return cols

def query(con, queryStr):
    rows = []
    affectedCount = 0
    lastID = -1
    try:
        with con.cursor() as cur:
            cur.execute(queryStr)
            rows = cur.fetchall()
            affectedCount = cur.rowcount
            lastID = cur.lastrowid
    except pymysql.err.ProgrammingError as e:
        print("query:Синтаксическая ошибка:", e)
    except pymysql.err.Error as e:
        print("query:Не предвиденная ошибка:", e)
    con.commit()
    if lastID == None:
        lastID = -1
    return rows, affectedCount, lastID

def insertInto(con, table = "tableName", args = {"colName" : "value"}):
    q = "INSERT INTO " + table + " "
    colNames = " ("
    colVals = " VALUES ("
    for k, v in args.items():
        colNames += str(k) + ","
        colVals += "'" + str(v) + "',"
    colNames = colNames.strip(",") + ")"
    colVals = colVals.strip(",") + ")"
    q += colNames + colVals
    count = 0
    rows, count, lastID = query(con, q)
    return count, lastID

def updateWhere(con, table = "clients", args = {"name" : "de"}, keys = {"name" : "de"}):
    q = "UPDATE " + table + " "
    setPart = " SET "
    wherePart = " WHERE "
    for k, v in args.items():
        setPart += str(k) + "='" + str(v) + "',"
    setPart = setPart.strip(",") + " "
    for k, v in keys.items():
        wherePart += str(k) + "='" + str(v) + "',"
    wherePart = wherePart.strip(",") + " "
    q += setPart + wherePart
    count = 0
    #print("qu:", q)
    rows, count, lastID = query(con, q)
    return count
    
def getConfigParams(con, keys):
    ret = {}
    for key in keys:
        rows, count, lastID = query(con, "SELECT * FROM configParams cp WHERE cp.key = \'" + key + "\';")
        if len(rows) == 0:
            return ret, False
        ret[key] = rows[0]["value"]
    return ret, True

def newEvent(con, text, userID = -1, camID = -1, typeID = var.EVENT_TYPE_INFO):
    params = {}
    params["typeId"] = typeID
    params["text"] = text
    if userID != -1: params["userId"] = userID
    if camID != -1: params["camId"] = camID
    count, newEventID = insertInto(con, "events", params)
    if count == 0:
        print("functions.py:newEvent():cannot create event")
    return newEventID

def getStorageParams(con):
    res, _ = getConfigParams(con, [var.KEY_DIR_NAME_STORAGE, var.KEY_DIR_NAME_FACES, var.KEY_DIR_NAME_ENCODINGS, var.KEY_DIR_NAME_IMGS])
    return res.get(var.KEY_DIR_NAME_STORAGE, ""), res.get(var.KEY_DIR_NAME_FACES, ""), res.get(var.KEY_DIR_NAME_ENCODINGS, ""), res.get(var.KEY_DIR_NAME_IMGS, "")



#con = getConnnection()
#print("res:", insertInto(con, "users", {"nick": "name3"}))
# cur = con.cursor()
# cur.execute("select * from clients;")
# rows = cur.fetchall()
# for row in rows:
#     print(row)


# d = {"name": "name1", "log": "log1", "pass": "pass1"}
# con = getConnnection()
# count = insertInto(con, "clients", d)
# print("aff:", count)

###########---------------------##############################--------0





###########---------------------##############################--------1


