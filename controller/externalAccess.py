import pymysql.cursors
from controller.config import hostConfig, dbConfig, passwordConfig, userConfig

from google.cloud import storage

def establishConnection():
    connection = pymysql.connect(host=hostConfig,
                                 user=userConfig,
                                 password=passwordConfig,
                                 db=dbConfig,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(source_file_name)

def download_blob(bucket_name, source_blob_name, destination_file_name):

    print('here')
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))