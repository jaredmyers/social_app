import mysql.connector
import credentials as cred
import bcrypt
import uuid
import datetime
import random
import json


def accessor_methods(body, queue):

    conn = mysql.connector.connect(
            host=cred.db_host,
            user=cred.db_user,
            password=cred.db_pw,
            database=cred.db_database
            )
    print("accessor method connected to db")

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

    def generate_hashpw(pw):
        '''generates new user password hash to store'''
        salt = bcrypt.gensalt()
        pw = pw.encode()
        hashed = bcrypt.hashpw(pw, salt)

        return hashed.decode('utf-8')

    def process_login(body):
        '''check user provided login creds against db '''
        print("from process_login of db_accessor_methods, body:")
        print(body)
        username = body["username"]
        password = body["password"]

        print("process_login running..")

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

    def register_user(body):
        '''registers new user in db'''
        username = body['username']
        pw = body['pw']

        hashedpw = generate_hashpw(pw)

        # check if username already exists
        query = "select userID from users where uname = %s;"
        val = (username,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # create if username doesn't exist, else return
        if not query_result:
            query = "insert into users (uname, pw) values (%s, %s);"
            val = (username, hashedpw)
            cursor.execute(query, val)
            conn.commit()

            return generate_sessionId(username)
        else:
            return ''

    print("body of db_accessor_methods:")
    print(body)
    body = body.decode('utf-8')
    print("body after decode...")
    print(body)
    body = json.loads(body)
    print("body after json.loads..")
    print(body)
    print(type(body))

# main entry point
#

    if body['type'] == 'login':
        print("login is in body")
        return process_login(body)
    elif body['type'] == 'register':
        return register_user(body)
    else:
        print("db_accessor_meth detected no valid body value")
        return ''
