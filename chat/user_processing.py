import mysql.connector
import uuid
import chat.credentials as cred

conn = mysql.connector.connect(
        host=cred.db_host,
        user=cred.db_user,
        password=cred.db_pw,
        database=cred.db_database
        )


def generate_sessionId(username):
    '''generates a user sessionId for a new login'''
    #grab current usernames userID
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


def process_login(username, password):

    query = "SELECT uname, pw FROM users WHERE uname = %s;"
    val = (username,)
    cursor = conn.cursor()
    cursor.execute(query, val)
    query_result = cursor.fetchall()

    if not query_result:
        return ''

    uname = query_result[0][0]
    pw = query_result[0][1]

    # this is where the hash will be checked using bcrypt
    if username == uname and password == pw:
        return generate_sessionId(username)
