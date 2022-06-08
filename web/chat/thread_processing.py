import json
import mysql
import chat.credentials as cred
from chat.send_to_db import send_to_db


# thread page processing
def get_thread_info():
    '''gets threads from database to display on forum page'''
    message = {}
    message['type'] = 'get_threads'
    print('get_thread_info sending to db...')
    response = send_to_db(message, 'thread_chat_proc')

    list_json_strings = response.split(';')
    del list_json_strings[-1]
    print('get_thread_info returning: ')
    print(list_json_strings)
    return list_json_strings


def send_new_thread(sessionID, threadname, threadcontent):
    '''sends info to driver to create new forum thread'''

    message = {}
    message['type'] = 'send_new_thread'
    message['sessionID'] = sessionID
    message['threadname'] = threadname
    message['threadcontent'] = threadcontent

    print('send_new_thread sending to db...')
    response = send_to_db(message, 'thread_chat_proc')


def get_reply_page(threadID):
    pass
    message = {}
    message['type'] = 'get_reply_page'
    message['threadID'] = threadID

    print('get_reply_page sending to db...')
    response = send_to_db(message, 'thread_chat_proc')

    return response


def send_new_reply(sessionID, threadID, replycontent):
    '''create/send new reply on given threadID to mq for db'''
    message = {}
    message['type'] = 'send_new_reply'
    message['sessionID'] = sessionID
    message['threadID'] = threadID
    message['replycontent'] = replycontent

    print('send_new_reply sending to db...')
    response = send_to_db(message, 'thread_chat_proc')


def add_friend(sessionID, friendname):
    message = {}
    message['type'] = 'add_friend'
    message['sessionID'] = sessionID
    message['friendname'] = friendname

    print('add_friend sending to db...')
    response = send_to_db(message, 'thread_chat_proc')

    return response


def remove_friend(sessionID, friendname):
    print('remove_friend??')
    message = {}
    message['type'] = 'remove_friend'
    message['sessionID'] = sessionID
    message['friendname'] = friendname

    print('remove friend sending to db...')

    response = send_to_db(message, 'thread_chat_proc')

    return response


def get_friends(sessionID):
    message = {}
    message['type'] = 'get_friends'
    message['sessionID'] = sessionID
    response = send_to_db(message, 'thread_chat_proc')

    if not response:
        return []

    friends_list = response.split(":")
    del friends_list[-1]

    return friends_list


def create_chat(sessionID, chat_recipient):
    message = {}
    message['type'] = 'create_chat'
    message['sessionID'] = sessionID
    message['chat_recipient'] = chat_recipient

    response = send_to_db(message, 'thread_chat_proc')

    return response


def get_username(sessionID):
    message = {}
    message['type'] = 'get_username'
    message['sessionID'] = sessionID

    response = send_to_db(message, 'thread_chat_proc')

    return response


def new_chat_message(username, new_message, room_id):
    message = {}
    message['type'] = 'new_chat_message'
    message['username'] = username
    message['chat_message'] = new_message
    message['room_id'] = room_id

    print("new_chat_message values are...")
    print(message['type'])
    print(type(message['type']))
    print(message['username'])
    print(type(message['username']))
    print(message['chat_message'])
    print(type(message['chat_message']))
    print(message['room_id'])
    print(type(message['room_id']))

    response = send_to_db(message, 'thread_chat_proc')

    return response


def get_chat_messages(room_id):
    message = {}
    message['type'] = 'get_chat_messages'
    message['room_id'] = room_id

    response = send_to_db(message, 'thread_chat_proc')

    chat_messages = response.split(";")
    del chat_messages[-1]

    p = 0
    message_dict = {}
    for i in chat_messages:
        message = i.split(":")
        message_dict[p] = [message[0], message[1]]
        p += 1

    return message_dict


def remove_friend(sessionID, friendname):
    pass

"""
# Chat page processing
def get_friends(sessionID):
    '''fetch users friends for their friend list'''
    
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
                userID_list.append(p) # these are userID ints from db

    # selecting all the users
    query = "select * from users;"
    cursor.execute(query)
    query_result = cursor.fetchall()
    cursor.close()

    # grabbing all the usernames of all the users friends
    friend_names = []
    for i in query_result:
        if i[0] in userID_list:
            friend_names.append(i[1])

    return friend_names


def create_chat(sessionID, chat_recipient):
    '''create chatroom table for the specific chat'''
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
    # f-string vars all internal values, not user input

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


def get_username(sessionID):
    '''grabs users username from sessionID data'''

    query = "select users.uname from users inner join sessions on sessions.userID=users.userID where sessionID=%s;"
    val = (sessionID,)
    cursor = conn.cursor()
    cursor.execute(query, val)
    username = cursor.fetchall()[0][0]
    cursor.close()

    return username


def new_chat_message(username, chat_message, room_id):
    '''creates a new chat message for the chatroom id'''

    # inserts new chat message into chatroom
    query = f"insert into {room_id} (uname, message) values (%s, %s);"
    val = (username, chat_message)
    cursor = conn.cursor()
    cursor.execute(query, val)
    conn.commit()
    cursor.close()

    return '1'


def get_chat_messages(room_id):
    '''gets all chat messages for chatroom id to populate chatbox'''

    # grabs all the current messages to see if there are more than 20
    query = f"select messageID from {room_id};"
    cursor = conn.cursor()
    cursor.execute(query)
    query_result = cursor.fetchall()

    # checl/limit message history to latest 20
    if len(query_result) > 20:
        query = f"delete from {room_id} order by messageID ASC LIMIT 1;"
        cursor.execute(query)
        conn.commit()

    #  get all remaining messages
    query = f"select uname, message from {room_id}"
    cursor.execute(query)
    query_result = cursor.fetchall()
    cursor.close()

    # send back formatted as a string to be decompressed into lists
    # using ; delim for lists, : delim for elements 
    # update: im leaving this as is for now. ugh.
    chat_records = ''
    for i in query_result:
        chat_records += i[0] + ":" + i[1] + ";"

    # i'll untangle all this later
    chat_messages = chat_records.split(";")
    del chat_messages[-1]

    p = 0
    message_dict = {}
    for i in chat_messages:
        message = i.split(":")
        message_dict[p] = [message[0], message[1]]
        p += 1

    return message_dict
"""


class ThreadMain():

    def __init__(self, author, threadID, title, content, date):
        self.threadID = threadID
        self.content = content
        self.author = author
        self.date = date
        self.title = title


class ThreadReplies():

    def __init__(self, author, content, date):
        self.author = author
        self.content = content
        self.date = date
