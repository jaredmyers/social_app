import mysql.connector
import chat.credentials as cred
import bcrypt
import uuid
import datetime
import random
import json


def accessor_methods(body, queue):
    """
    conn = mysql.connector.connect(
            host=cred.db_host,
            user=cred.db_user,
            password=cred.db_pw,
            database=cred.db_database
            )
    """
    def generate_sessionId(username):
        '''generates user sessionId for new login'''
        # grab current usersnames userID
        query = "select userID from users where uname= %s;"
        val = (username,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        userID = query_result[0][0]

        sessionID = uuid.uuid4().hex

        # if user has session, delete it
        query = "delete from sessions where userID=%s;"
        val = (userID,)
        cursor.execute(query, val)
        conn.commit()

        # insert newly generated sessionId into sessions
        query = "insert into sessions (userID, sessionID) values (%s, %s);"
        val = (userID, sessionID)
        cursor.execute(query, val)
        conn.commit()

        return sessionID

    def process_login(body):
        '''check user provided login creds against db '''
        username = body["username"]
        password = body["password"]

        query = "select uname, pw from users where uname = %s;"
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

        # checking hash
        cred_match = bcrypt.checkpw(password.encode(), hashed.encode())
        print("credmatch = ")
        print(cred_match)

        if cred_match:
            return generate_sessionId(username)

        return ''

    body = body.decode('utf-8')
    body = json.loads(body)

    if "login" in body:
        return process_login(body)
