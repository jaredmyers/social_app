import mysql.connector
import credentials as cred
import bcrypt
import uuid
import datetime
import random
import json


def accessor_methods(body, queue):
    '''
    API for accessing mysql
    '''

    conn = mysql.connector.connect(
            host=cred.db_host,
            user=cred.db_user,
            password=cred.db_pw,
            database=cred.db_database
            )
    print("accessor method connected to db")

    def delete_session(body):
        '''deletes a session'''
        sessionID = body['sessionID']

        query = "delete from sessions where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()

        return '0'

    def check_session(body):
        '''checks to see if session exists and is still valid'''
        sessionID = body['sessionID']
        token_expiry = 0.50

        # grab the given session time
        query = "select sessionID, sTime from sessions where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # return false if session doesn't exist
        # check sessions time, delete if expired
        if not query_result:
            return ''

        token_issue_date = query_result[0][1]
        current_time = datetime.datetime.now()
        diff = current_time - token_issue_date
        diff_hours = diff.total_seconds()/3600

        if diff_hours > token_expiry:
            wrapper = {}
            wrapper['sessionID'] = sessionID
            delete_session(wrapper)
            return ''

        return query_result[0][0]

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

    def get_thread_info():
        '''gets threads from database to display on forum page'''

        # grab all relevant thread information
        query = "select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID order by ts desc"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        cursor.close()

        # parse info for sending through mq
        thread = {}
        threads_string = ''
        for i in query_result:
            thread['author'] = i[0]
            thread['threadID'] = str(i[1])
            thread['title'] = i[2]
            thread['content'] = i[3]
            thread['date'] = i[4].strftime('%Y-%m-%d')

            threads_string += json.dumps(thread)
            threads_string += ';'

        return threads_string

    def send_new_thread(body):
        '''creates new thread'''
        sessionID = body['sessionID']
        threadname = body['threadname']
        threadcontent = body['threadcontent']

        # grab the users userID
        query = "select userID from sessions where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if session not valid
        if not query_result:
            return ''

        userID = query_result[0][0]

        # inserts new forum post into threads table
        query = "insert into threads (userID, title, content) values (%s, %s, %s);"
        val = (userID, threadname, threadcontent)
        cursor.execute(query, val)
        conn.commit()
        cursor.close()

        return '0'

    def get_reply_page(body):
        '''gets replies for a given forum thread for reply page'''
        threadID = body['threadID']

        # grab all relevant forum thread information
        query = "select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID and threads.threadID=%s;"
        val = (threadID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        cursor.close()

        thread = {}
        threads_string = ''
        for i in query_result:
            thread['author'] = i[0]
            thread['threadID'] = str(i[1])
            thread['title'] = i[2]
            thread['content'] = i[3]
            thread['date'] = i[4].strftime('%Y-%m-%d')

            threads_string += json.dumps(thread)
            threads_string += '+'

        # grab all relevant reply data for the given forum thread
        query = "select users.uname, replies.content, replies.replyts from users,replies where users.userID=replies.userID and replies.threadID=%s order by replies.replyts desc;"
        val = (threadID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        cursor.close()

        replies = {}
        replies_string = ''
        for i in query_result:
            replies['author'] = i[0]
            replies['content'] = i[1]
            replies['date'] = i[2].strftime('%Y-%m-%d')

            replies_string += json.dumps(replies)
            replies_string += ';'

        # returns json strings, in the delimited format of:
        # threadcontent+replycontent;replycontent;
        # will figure more elegant solution later, prob embed json
        return (threads_string + replies_string)

    def send_new_reply(body):
        '''create/send new reply on given threadID'''
        sessionID = body['sessionID']
        threadID = body['threadID']
        replycontent = body['replycontent']

        # grab the users id
        query = "select userID from sessions where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        cursor.close()

        # return false if session not valid
        if not query_result:
            return ''

        userID = query_result[0][0]

        # insert new reply into replies table
        query = "insert into replies (threadID, userID, content) values (%s, %s, %s);"
        val = (threadID, userID, replycontent)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()
        cursor.close()

        return '0'

    def add_friend(body):
        '''adds friend to users friendlist'''
        sessionID = body['sessionID']
        username = body['friendname']

        # grab current users userID
        query = "select userID from sessions where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        userID1 = cursor.fetchall()[0][0]

        # grab potential friends userID
        query = "select userID from users where uname=%s;"
        val = (username,)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if potential friend doesn't exist
        if not query_result:
            return ''

        userID2 = query_result[0][0]

        # return false if user tries to friend self
        if userID1 == userID2:
            return ''

        # check if they are already friends
        query = "select * from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1, userID2, userID2, userID1)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if already friends
        if query_result:
            return ''

        # add friend relationship to friends table
        query = "insert into friends (userID1, userID2) values (%s, %s);"
        val = (userID1, userID2)
        cursor.execute(query, val)
        conn.commit()
        cursor.close()

        return '0'

    # chat page processing
    def get_friends(body):
        '''fetch user friends for their friend list'''
        sessionID = body['sessionID']

        query = "select userID from sessions where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        userID = cursor.fetchall()[0][0]

        # grabbing all the users friend relationships
        query = "select * from friends where userID1=%s or userID2=%s;"
        val = (userID, userID)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # return false if user has no friends
        if not query_result:
            return ''

        # parsing out just the users friends as userIDs
        userID_list = []
        for i in query_result:
            for p in i:
                if p != userID:
                    userID_list.append(p)  # these are userID ints from db

        # selecting all the users
        query = "select * from users;"
        cursor.execute(query)
        query_result = cursor.fetchall()
        cursor.close()

        # grabbing all the usernames of all the users friends
        friend_names = ''
        for i in query_result:
            if i[0] in userID_list:
                friend_names += i[1] + ":"

        return friend_names

    def create_chat(body):
        '''create chatroom table for the specific chat'''
        sessionID = body['sessionID']
        chat_recipient = body['chat_recipient']

        # grab chat creators username and userID
        query = "select users.uname, users.userID from users inner join sessions on sessions.userID=users.userID where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        uname1 = query_result[0][0]
        userID1 = query_result[0][1]

        # grab chat recipient userID
        query = "select userID from users where uname = %s;"
        val = (chat_recipient,)
        cursor.execute(query, val)
        userID2 = cursor.fetchall()[0][0]

        # check if chatroom already exists
        query = "select roomID from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1, userID2, userID2, userID1)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # create chatroom if one doesn't exist,
        # update chatroom name into friends table
        # f-string vars all internal, not user input

        if not query_result[0][0]:
            roomID = f"{uname1}_{chat_recipient}"
            query = f"create table if not exists {roomID} (messageID INT AUTO_INCREMENT PRIMARY KEY, uname VARCHAR(255), message TEXT);"
            val = (roomID,)
            cursor.execute(query)
            conn.commit()

            query = "update friends set roomID=%s where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
            val = (roomID, userID1, userID2, userID2, userID1)
            cursor.execute(query, val)
            conn.commit()
            cursor.close()

            return roomID

        # returns chatroom name if it already existed
        cursor.close()
        return query_result[0][0]

    def get_username(body):
        '''grabs user username from sessionID data'''

        sessionID = body['sessionID']

        query = "select users.uname from users inner join sessions on sessions.userID=users.userID where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        username = cursor.fetchall()[0][0]
        cursor.close()

        return username

    def new_chat_message(body):
        '''creates a new chat message for the chatroom id'''
        username = body['username']
        chat_message = body['chat_message']
        room_id = body['room_id']

        # inserts new chat message into chatroom
        query = f"insert into {room_id} (uname, message) values (%s, %s);"
        val = (username, chat_message)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()
        cursor.close()

        return '0'

    def get_chat_messages(body):
        '''gets all chat messages for chatroom id to populate chatbox'''

        room_id = body['room_id']

        # grabs all the current messages to see if there are more than 20
        query = f"select messageID from {room_id};"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()

        # check/limit message history to latest 20
        if len(query_result) > 20:
            query = f"delete from {room_id} order by messageID ASC LIMIT 1;"
            cursor.execute(query)
            conn.commit()

        # get all remaining messages
        query = f"select uname, message from {room_id};"
        cursor.execute(query)
        query_result = cursor.fetchall()
        cursor.close()

        # send back formatted string to be decompressed into lists
        chat_records = ''
        for i in query_result:
            chat_records += i[0] + ":" + i[1] + ";"

        return chat_records

    def remove_friend(body):
        '''removes friend from users friendlist'''
        sessionID = body['sessionID']
        username = body['friendname']

        # grab current users userID
        query = "select userID from sessions where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        userID1 = cursor.fetchall()[0][0]

        # grab potential friends userID
        query = "select userID from users where uname=%s;"
        val = (username,)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if potential friend doesn't exist
        if not query_result:
            return ''

        userID2 = query_result[0][0]

        # return false if user tries to delete self
        if userID1 == userID2:
            return ''

        # check if they are already friends & get potential roomID
        query = "select * from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1, userID2, userID2, userID1)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if not friends
        if not query_result:
            return ''

        # delete chat table if exists
        if query_result[0][2]:
            roomID = query_result[0][2]

            # delete corresponding chat table
            query = f"drop table {roomID}"
            cursor.execute(query)
            conn.commit()

        # remove friend relationship from friends table
        query = "delete from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1, userID2, userID2, userID1)
        cursor.execute(query, val)
        conn.commit()

        return '0'

    def get_recommended(body):
        sessionID = body['sessionID']

        # grab userID of current user based on session data
        query = "select userID from sessions where sessionID=%s;"
        val = (sessionID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        userID = query_result[0][0]

        # grab all other users from db for potential match
        # this is done simply because this api is simulated
        # and needs valid usernames to simulate friend matches

        query = "select uname from users where userID not in (%s);"
        val = (userID,)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        matched_friends = []
        for tup in query_result:
            matched_friends.append(tup[0])

        return json.dumps(matched_friends)

# main entry point
    print("body of db_accessor_methods:")
    print(body)
    body = body.decode('utf-8')
    print("body after decode...")
    print(body)
    body = json.loads(body)
    print("body after json.loads..")
    print(body)
    print(type(body))

    if body['type'] == 'login':
        print("login is in body")
        return process_login(body)
    elif body['type'] == 'register':
        return register_user(body)
    elif body['type'] == 'get_threads':
        return get_thread_info()
    elif body['type'] == 'send_new_thread':
        return send_new_thread(body)
    elif body['type'] == 'get_reply_page':
        return get_reply_page(body)
    elif body['type'] == 'send_new_reply':
        return send_new_reply(body)
    elif body['type'] == 'add_friend':
        return add_friend(body)
    elif body['type'] == 'get_friends':
        return get_friends(body)
    elif body['type'] == 'create_chat':
        return create_chat(body)
    elif body['type'] == 'get_username':
        return get_username(body)
    elif body['type'] == 'new_chat_message':
        return new_chat_message(body)
    elif body['type'] == 'get_chat_messages':
        return get_chat_messages(body)
    elif body['type'] == 'remove_friend':
        return remove_friend(body)
    elif body['type'] == 'check_session':
        return check_session(body)
    elif body['type'] == 'delete_session':
        return delete_session(body)
    elif body['type'] == 'get_recommended':
        return get_recommended(body)
    else:
        print("db_accessor_meth detected no valid body value")
        return ''
