
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
        'created_boards': []
    })
    datastore_client.put(entity)

def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity

####################### Create and Retrieve Vehicles ###########################
#Create Vehicle Objects
def createBoard(claims, name):
    # 63 bit random number that will serve as the key for this address object. not sure
    # why the data store doesn't like 64 bit numbers
    id = random.getrandbits(63)
    entity_key = datastore_client.key('Board', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'name': name,
        'task_list': [],
        'user_list': []
    })
    datastore_client.put(entity)
    return id

#Retrieve Vehicle Objects
def retrieveBoards(user_info):
    #make key objects out of all the keys and retrieve them
    board_id = user_info['created_boards']
    board_keys = []
    for i in range(len(board_id)):
        board_keys.append(datastore_client.key('Board', board_id[i]))
    board_list = datastore_client.get_multi(board_keys)
    return board_list

# Get vehicle info
def retrieveBoardInfo(id):
    entity_key = datastore_client.key('Board', id)
    entity = datastore_client.get(entity_key)
    return entity

######################### Bind Vehicles to UserInfo ############################
def addBoardToUser(user_info, id):
    board_keys = user_info['created_boards']
    board_keys.append(id)
    user_info.update({
        'created_boards': board_keys
    })
    datastore_client.put(user_info)















####################### Create and Retrieve Reviews ###########################
# Create vehicle reviews
def createReview(claims, rating, review, dt):
    id = random.getrandbits(63)
    entity_key = datastore_client.key('Review', id)
    entity = datastore.Entity(key = entity_key)
    entity.update({
        'rating' : rating,
        'review' : review,
        'timestamp': dt
    })
    datastore_client.put(entity)
    return id

#Retrieve Vehicle Objects
def retrieveReviews(vehicle_info):
    #make key objects out of all the keys and retrieve them
    review_id = vehicle_info['review_list']
    review_keys = []
    for i in range(len(review_id)):
        review_keys.append(datastore_client.key('Review', review_id[i]))
    review_list = datastore_client.get_multi(review_keys)
    return review_list

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


######################### Delete Vehicles via UserInfo ########################
def deleteVehicle(claims, id):
    user_info = retrieveUserInfo(claims)
    vehicle_list_keys = user_info['vehicle_list']

    vehicle_key = datastore_client.key('Vehicle', id)
    datastore_client.delete(vehicle_key)
    vehicle_list_keys.remove(id)
    user_info.update({
        'vehicle_list' : vehicle_list_keys
    })
    datastore_client.put(user_info)

################################################################################
################################## App Routes ##################################
################################################################################
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
