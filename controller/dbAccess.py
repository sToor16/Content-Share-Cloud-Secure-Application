import pymysql.cursors
from controller.config import hostConfig, dbConfig, passwordConfig, userConfig, secretKeyConfig

def insertQuery(sql, params):
    connection = pymysql.connect(host=hostConfig,
                                 user=userConfig,
                                 password=passwordConfig,
                                 db=dbConfig,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (params['userName'], params['user_id'], params['hashedPw']))
        connection.commit()
    finally:
        connection.close()

def fetchQuery(sql, params):
    try:
        connection = pymysql.connect(host=hostConfig,
                                     user=userConfig,
                                     password=passwordConfig,
                                     db=dbConfig,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            cursor.execute(sql, (params['user_id']))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()
