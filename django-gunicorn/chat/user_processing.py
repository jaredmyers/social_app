from chat.send_to_db import send_to_db


def process_login(username, password):
    message = {}
    message["type"] = "login"
    message["username"] = username
    message["password"] = password

    response = send_to_db(message, 'user_processing')
    return response


def register_user(username, pw):
    message = {}
    message["type"] = "register"
    message["username"] = username
    message["pw"] = pw

    response = send_to_db(message, 'user_processing')
    return response


def check_session(sessionID):
    message = {}
    message["type"] = "check_session"
    message["sessionID"] = sessionID

    response = send_to_db(message, 'user_processing')
    return response


def delete_session(sessionID):
    message = {}
    message["type"] = "delete_session"
    message["sessionID"] = sessionID

    response = send_to_db(message, 'user_processing')
    return response
