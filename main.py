
import datetime
from multiprocessing.sharedctypes import Value
import google.oauth2.id_token
import random
from google.cloud import datastore
from flask import Flask, render_template, request, redirect, session, url_for
from google.auth.transport import requests

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

######################### Create and Retrieve UserInfo #########################
def createUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'email': claims['email'],
        'name': claims['name'],
        'board_list': []
    })
    datastore_client.put(entity)

def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity

####################### Create and Retrieve Boards ###########################
#Create Board Objects
def createBoard(claims, name):
    # 63 bit random number that will serve as the key for this board object.
    id = random.getrandbits(63)
    entity_key = datastore_client.key('Board', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'name': name,
        'task_list': [],
        'user_list': [],
        'creator': claims['email']
    })
    datastore_client.put(entity)
    addUserToBoard(entity, claims['email'])
    return id

#Retrieve Board Objects
def retrieveBoards(user_info):
    #make key objects out of all the keys and retrieve them
    board_id = user_info['board_list']
    board_keys = []
    for i in range(len(board_id)):
        board_keys.append(datastore_client.key('Board', board_id[i]))
    board_list = datastore_client.get_multi(board_keys)
    return board_list

#Retrieve User Objects
def retrieveUsers(board):
    #make key objects out of all the keys and retrieve them
    user_id = board['user_list']
    user_keys = []
    for i in range(len(user_id)):
        user_keys.append(datastore_client.key('UserInfo', user_id[i]))
    user_list = datastore_client.get_multi(user_keys)
    return user_list

# Get a board by key
def getBoardByKey(id):
    entity_key = datastore_client.key('Board', id)
    entity = datastore_client.get(entity_key)
    return entity

######################### Bind Boards to UserInfo ############################
def addBoardToUser(user_info, id):
    board_keys = user_info['board_list']
    board_keys.append(id)
    user_info.update({
        'board_list': board_keys
    })
    datastore_client.put(user_info)

####################### Create and Retrieve Tasks ###########################
# Create tasks
def createTask(claims, title, due_date, status, assigned_to):
    id = random.getrandbits(63)
    entity_key = datastore_client.key('Task', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'title' : title,
        'due_date' : due_date,
        'status': status,
        'assigned_to': assigned_to,
        'completed_at': None
    })
    datastore_client.put(entity)
    return id

#Retrieve Task Objects
def retrieveTasks(board):
    #make key objects out of all the keys and retrieve them
    task_id = board['task_list']
    task_keys = []
    for i in range(len(task_id)):
        task_keys.append(datastore_client.key('Task', task_id[i]))
    task_list = datastore_client.get_multi(task_keys)
    return task_list

# Get a board by key
def getTaskByKey(id):
    entity_key = datastore_client.key('Task', id)
    entity = datastore_client.get(entity_key)
    return entity

def addTaskToBoard(board, id):
    task_keys = board['task_list']
    task_keys.append(id)
    board.update({
        'task_list': task_keys
    })
    datastore_client.put(board)
def addUserToBoard(board, email):
    user_keys = board['user_list']
    user_keys.append(email)
    board.update({
        'user_list': user_keys
    })
    datastore_client.put(board)

######################### Delete Task ########################
def deleteTask(board_id, task_id):
    board = getBoardByKey(board_id)
    task_list_keys = board['task_list']

    task_key = datastore_client.key('task', task_id)
    datastore_client.delete(task_key)
    task_list_keys.remove(task_id)
    board.update({
        'task_list' : task_list_keys
    })
    datastore_client.put(board)
















# Calculate average ratings
def update_average_rating(vehicle_info):
    reviews = retrieveReviews(vehicle_info)
    sum = 0
    for review in reviews:
        sum += int(review['rating'])
    if len(reviews)!=0:
        average = sum/len(reviews)
        average = round(average, 2)
    else:
        average = 0
    vehicle_info.update({
        'average_rating': average
    })
    datastore_client.put(vehicle_info)
    return average
######################### Bind Reviews to VehicleInfo ############################
def addReviewToVehicle(vehicle_info, id):
    review_keys = vehicle_info['review_list']
    review_keys.append(id)
    vehicle_info.update({
        'review_list': review_keys
    })
    datastore_client.put(vehicle_info)

def addReviewToUser(user_info, id):
    review_keys = user_info['review_list']
    review_keys.append(id)
    user_info.update({
        'review_list': review_keys
    })
    datastore_client.put(user_info)





















################################################################################
################################## App Routes ##################################
################################################################################


@app.route('/delete_task/<int:id>', methods=['GET', 'POST'])
def delete_task(id):
    id_token = request.cookies.get("token")
    error_message = None
    current_id = int(request.form['board_id'])
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
            deleteTask(current_id, id)
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for("open_board", id=current_id))

@app.route('/rename_board', methods=['POST'])
def rename_board():
    id_token = request.cookies.get("token")
    error_message = None
    current_id = int(request.form['board_id'])
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
            board = getBoardByKey(current_id)
            board.update({
                'name': request.form['name']
            })
            datastore_client.put(board)
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for("open_board", id=current_id))

@app.route('/mark_task', methods=['POST'])
def mark_task():
    id_token = request.cookies.get("token")
    error_message = None
    current_id = int(request.form['board_id'])
    id = int(request.form['id'])
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
            task = getTaskByKey(id)
            if request.form['status'] == 'complete':
                task.update({
                    'status': request.form['status'],
                    'completed_at': datetime.datetime.now()
                })
            else:
                task.update({
                    'status': request.form['status'],
                    'completed_at': None
                })
            datastore_client.put(task)
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for("open_board", id=current_id))
            
            

@app.route('/board/<int:id>', methods=['GET','POST'])
def open_board(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    board = None
    current_id = id
    users = None
    tasks = None
    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)
                user_info = retrieveUserInfo(claims)
                board = getBoardByKey(id)
                tasks = retrieveTasks(board)
                users = retrieveUsers(board)
            except ValueError as exc:
                error_message = str(exc)
        return render_template('board.html', user_data=claims, error_message=error_message, user_info=user_info, 
                               board=board, current_id=current_id, tasks=tasks, users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    current_id = int(request.form['board_id'])
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            board = getBoardByKey(current_id)
            
            entity_key = datastore_client.key('UserInfo', request.form['email'])
            entity = datastore_client.get(entity_key)
            if entity:
                addUserToBoard(board, request.form['email'])
                addBoardToUser(entity, current_id)
            
            
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for("open_board", id=current_id))

@app.route('/create_task', methods=['POST'])
def create_task():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    current_id = int(request.form['board_id'])
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            board = getBoardByKey(current_id)
            id = createTask(claims, request.form['title'], request.form['due_date'], request.form['status'], request.form['assigned_to'])
            addTaskToBoard(board, id)
        except ValueError as exc:
            error_message = str(exc)
    return redirect(url_for("open_board", id=current_id))

@app.route('/create_board', methods=['POST'])
def create_board():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            id = createBoard(claims, request.form['name'])
            addBoardToUser(user_info, id)
            
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    boards = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            if user_info == None:
                createUserInfo(claims)
                user_info = retrieveUserInfo(claims)
            boards = retrieveBoards(user_info)
        except ValueError as exc:
            error_message = str(exc)

    return render_template('main.html', user_data=claims, error_message=error_message, user_info=user_info, boards=boards)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
