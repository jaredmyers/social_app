from chat.send_to_db import send_to_db

# For communicating with MQ on given queue
# for specific functions


def process_login(username, password):
    ''' sends user login credentials to MQ for verification'''
    message = {}
    message["type"] = "login"
    message["username"] = username
    message["password"] = password

    response = send_to_db(message, 'user_processing')
    return response


def register_user(username, pw):
    '''sends new user info to MQ for registration'''
    message = {}
    message["type"] = "register"
    message["username"] = username
    message["pw"] = pw

    response = send_to_db(message, 'user_processing')
    return response


def check_session(sessionID):
    '''sends current session to MQ for verification'''
    message = {}
    message["type"] = "check_session"
    message["sessionID"] = sessionID

    response = send_to_db(message, 'user_processing')
    return response


def delete_session(sessionID):
    '''sends delete signal to MQ to wipe current session info'''
    message = {}
    message["type"] = "delete_session"
    message["sessionID"] = sessionID

    response = send_to_db(message, 'user_processing')
    return response
