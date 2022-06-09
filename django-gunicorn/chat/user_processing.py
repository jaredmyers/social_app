import mysql.connector
import uuid
import chat.credentials as cred
import bcrypt
from chat.send_to_db import send_to_db

"""
conn = mysql.connector.connect(
        host=cred.db_host,
        user=cred.db_user,
        password=cred.db_pw,
        database=cred.db_database
        )
"""
"""
def generate_hashpw(pw):
    '''generates password hash to store'''
    salt = bcrypt.gensalt()
    pw = pw.encode()
    hashed = bcrypt.hashpw(pw, salt)

    return hashed.decode('utf-8')


def generate_sessionId(username):
    '''generates a user sessionId for a new login'''
    # grab current usernames userID
    query = "SELECT userID from users where uname = %s;"
    val = (username,)
    cursor = conn.cursor()
    cursor.execute(query, val)
    query_result = cursor.fetchall()
    userID = query_result[0][0]

    sessionID = uuid.uuid4().hex

    # if user has a session, delete it
    query = "DELETE FROM sessions WHERE userID=%s;"
    val = (userID,)
    cursor.execute(query, val)
    conn.commit()

    # insert newly generated sessionId into sessions
    query = "INSERT into sessions (userID, sessionID) values (%s, %s);"
    val = (userID, sessionID)
    cursor.execute(query, val)
    conn.commit()

    return sessionID
"""
"""
def process_login(username, password):
    '''check user login credentials against db '''
    query = "SELECT uname, pw FROM users WHERE uname = %s;"
    val = (username,)
    cursor = conn.cursor()
    cursor.execute(query, val)
    query_result = cursor.fetchall()

    if not query_result:
        return ''

    uname = query_result[0][0]
    hashed = query_result[0][1]

    print("from process_login:")
    print(uname, hashed)

    # this is where the hash will be checked using bcrypt
    cred_match = bcrypt.checkpw(password.encode(), hashed.encode())
    print("credmatch = ")
    print(cred_match)

    if cred_match:
        return generate_sessionId(username)

    return ''

#    if username == uname and password == pw:
#        return generate_sessionId(username)
#    else:
#        return ''
"""


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


"""
def register_user(username, pw):
    '''registers new user in db'''
    hashedpw = generate_hashpw(pw)

    # check if username already exists
    query = "SELECT userID FROM users WHERE uname = %s;"
    val = (username,)
    cursor = conn.cursor()
    cursor.execute(query, val)
    query_result = cursor.fetchall()

    # create if username doesn't exist
    if not query_result:
        query = "INSERT into users (uname, pw) values (%s, %s);"
        val = (username, hashedpw)
        cursor.execute(query, val)
        conn.commit()

        return generate_sessionId(username)
    else:
        return ''
"""
