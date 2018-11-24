from flask import Blueprint, render_template, request, session, redirect
import datetime
import os
from controller.externalAccess import establishConnection, upload_blob

bucket_name = 'secure-flask-app-bucket'
bucket_base = 'https://storage.googleapis.com/secure-flask-app-bucket/'

common = Blueprint('common', __name__, template_folder='templates')

@common.route('/selectedGroup', methods=['GET','POST'])
def selectedGroup():

    if request.method == 'POST':
        idgroup = request.form['idgroup']
        print(idgroup)

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

    file = request.files['file']

    params['fileName'] = params['date'] + '_' + params['time'] + '_' + file.filename
    createTempFile(file, params['fileName'])

    dbQueries(params)
    return "success"

def createTempFile(file, fileName):
    path = '/tmp/'+ fileName
    file.save(path)

def dbQueries(params):
    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "SELECT totalSize FROM groups " \
                  "WHERE idGroup = %s"
            cursor.execute(sql,(params['idgroup']))
            result = cursor.fetchall()

            groupTotalSize = float (result[0]['totalSize'])
            params['fileSize'] = getFileSize(params['fileName'])
            newGroupTotalSize = groupTotalSize + params['fileSize']

            if newGroupTotalSize > 100:
                print("file cannot be uploaded, group already using allocated memory")
                return "failed"
            else:
                filePath = '/tmp/' + params['fileName']
                upload_blob(bucket_name, filePath, params['fileName'])
                params['full_file_url'] = bucket_base + params['fileName']

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

def getFileSize(path):
    path = '/tmp/'+path
    fileSize = os.stat(path).st_size
    fileSize = str(fileSize / (1024 * 1024))
    fileSize = fileSize[0:4]
    fileSize = float(fileSize)
    return fileSize

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

@common.route('/deleteGroupItem', methods=['POST'])
def deleteGroupItem():
    deleteItemId = request.form['deleteItemId']
    idgroup = request.form['idgroup']

    itemSize = fetchDeleteItemSize(deleteItemId)
    deleteItem(deleteItemId)
    updateGroupSize(itemSize, idgroup)

    return "success"

def fetchDeleteItemSize(deleteItemId):
    result = 0
    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "SELECT size FROM group_items " \
                  "WHERE idgroup_items = %s"
            cursor.execute(sql,(deleteItemId))
            result = cursor.fetchall()
            result = result[0]['size']
    finally:
        connection.close()

    return result


def deleteItem(deleteItemId):
    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM group_items " \
                  "WHERE idgroup_items = %s"
            cursor.execute(sql,(deleteItemId))
        connection.commit()
    finally:
        connection.close()

def updateGroupSize(itemSize, idgroup):
    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "SELECT totalSize FROM groups " \
                  "WHERE idgroup = %s"
            cursor.execute(sql,(idgroup))
            result = cursor.fetchall()
            totalSizeCurrent = float (result[0]['totalSize'])

            totalSizeNew = totalSizeCurrent - float (itemSize)
            if totalSizeNew  < 0:
                totalSizeNew = 0

            totalSizeNew = str (totalSizeNew)
            totalSizeNew =  totalSizeNew[0:4]

            sql = "UPDATE groups " \
                  "SET totalSize = %s " \
                  "WHERE idgroup = %s"
            cursor.execute(sql,(totalSizeNew, idgroup))

        connection.commit()
    finally:
        connection.close()