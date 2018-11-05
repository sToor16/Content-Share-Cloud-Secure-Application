import pymysql.cursors
from controller.config import hostConfig, dbConfig, passwordConfig, userConfig

from google.cloud import storage

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

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))
