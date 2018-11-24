from flask import Blueprint, render_template, request, redirect, session, flash

import datetime
import os
from controller.externalAccess import establishConnection, upload_blob

bucket_name = 'secure-flask-app-bucket'
bucket_base = 'https://storage.googleapis.com/secure-flask-app-bucket/'

common = Blueprint('common', __name__, template_folder='templates')

@common.route('/selectedGroup', methods=['GET','POST'])
def selectedGroup():

    idgroup = request.form['idgroup']

    try:
        connection = establishConnection()
        with connection.cursor() as cursor:

            sql = "SELECT groups.*, group_items.* FROM groups " \
                  "LEFT JOIN group_items " \
                  "ON groups.idgroup = group_items.idgroup " \
                  "WHERE groups.idgroup = %s"
            cursor.execute(sql,(idgroup))
            result = cursor.fetchall();
    finally:
        connection.close()

    return render_template('common/selected_group.html', groupData = result);

@common.route('/uploadNewFile', methods=['POST'])
def uploadPage():
    idgroup = request.form['idgroup']
    return render_template('common/upload_file.html', idgroup = idgroup)

@common.route('/uploadFile', methods=['POST'])
def uploadFile():
    params = {}

    params['idgroup'] = request.form['idgroup']
    params['description'] = request.form['description']
    params['name'] = request.form['name']

    now = datetime.datetime.now()
    time = now.time()
    date = now.date()
    params['date'] = date.strftime('%m%d%Y')
    params['time'] = time.strftime('%H%B')


    file = request.files.get('file')
    fileTemp = file

    params['fileSize'] = getFileSize(file)
    print("outside file size is: ", params['fileSize'])


    destination_blob_name = params['date'] + '_' + params['time'] + '_' + file.filename
    upload_blob(bucket_name, fileTemp, destination_blob_name)


    # params['full_file_url'] = bucket_base + destination_blob_name

    # dbQueries(params)
    return "success"

def getFileSize(file):
    file.save('/tmp/file')
    fileSize = os.stat('/tmp/file').st_size
    fileSize = str(fileSize / (1024 * 1024))
    fileSize = fileSize[0:4]
    fileSize = float(fileSize)

    return fileSize

def dbQueries(params):
    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "SELECT totalSize FROM groups " \
                  "WHERE idGroup = %s"
            cursor.execute(sql,(params['idgroup']))
            result = cursor.fetchall()
            groupTotalSize = (float) (result[0]['totalSize'])

            newGroupTotalSize = groupTotalSize + params['fileSize']
            print("newGroupTotalSize is: ", newGroupTotalSize)

            if newGroupTotalSize > 100:
                print("file cannot be uploaded, group already using allocated memory")
                return "failed"
            else:
                print("size is smaller, new file size is: ",params['fileSize'])
                sql = "UPDATE groups SET totalSize = %s " \
                      "WHERE idgroup = %s"
                cursor.execute(sql, (newGroupTotalSize, params['idgroup']))

                sql = "INSERT INTO group_items " \
                      "(idgroup, file_url, uploader_id, name, description, " \
                      "date, time, date_access, time_access, size) " \
                      "VALUES " \
                      "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (params['idgroup'], params['full_file_url'], session['userID'],
                                     params['name'], params['description'], params['date'],
                                     params['time'], params['date'], params['time'], params['fileSize']))
        connection.commit()
    finally:
        connection.close()

@common.route('/downloadFile', methods=['POST'])
def downloadFile():
    idgroup_items = request.form['idgroup_items']

    now = datetime.datetime.now()
    time = now.time()
    date = now.date()

    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "UPDATE group_items SET " \
                  "date_access= %s, time_access = %s " \
                  "WHERE idgroup_items = %s"
            cursor.execute(sql,(date, time, idgroup_items))
        connection.commit()

    finally:
        connection.close()

    return "success"
