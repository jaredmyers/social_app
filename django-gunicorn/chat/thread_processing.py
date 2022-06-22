import json
from chat.send_to_db import send_to_db

# For communicating with MQ on a given queue
# for specific functions


# thread page processing
def get_thread_info():
    '''
    sends signal to MQ to retrieve threads
    from database to display on forum page
    '''
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
    '''sends signal to MQ to create new forum thread'''

    message = {}
    message['type'] = 'send_new_thread'
    message['sessionID'] = sessionID
    message['threadname'] = threadname
    message['threadcontent'] = threadcontent

    print('send_new_thread sending to db...')
    response = send_to_db(message, 'thread_chat_proc')


def get_reply_page(threadID):
    '''
    sends signal to MQ to get replies
    from database to display for a given thread page
    '''
    message = {}
    message['type'] = 'get_reply_page'
    message['threadID'] = threadID

    print('get_reply_page sending to db...')
    response = send_to_db(message, 'thread_chat_proc')

    return response


def send_new_reply(sessionID, threadID, replycontent):
    '''
    sends signal to MQ to create new reply
    on given threadID
    '''
    message = {}
    message['type'] = 'send_new_reply'
    message['sessionID'] = sessionID
    message['threadID'] = threadID
    message['replycontent'] = replycontent

    print('send_new_reply sending to db...')
    response = send_to_db(message, 'thread_chat_proc')


def add_friend(sessionID, friendname):
    '''sends add signal to mq for adding a new friend'''
    message = {}
    message['type'] = 'add_friend'
    message['sessionID'] = sessionID
    message['friendname'] = friendname

    print('add_friend sending to db...')
    response = send_to_db(message, 'thread_chat_proc')

    return response


def remove_friend(sessionID, friendname):
    '''sends remove friend signal to mq to remove friend from friendlist'''

    message = {}
    message['type'] = 'remove_friend'
    message['sessionID'] = sessionID
    message['friendname'] = friendname

    response = send_to_db(message, 'thread_chat_proc')

    return response


def get_friends(sessionID):
    '''
    sends signal to MQ for getting users friends
    from database to display in friendslist
    '''
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
    '''sends signal to MQ for creating new chat table between friends'''
    message = {}
    message['type'] = 'create_chat'
    message['sessionID'] = sessionID
    message['chat_recipient'] = chat_recipient

    response = send_to_db(message, 'thread_chat_proc')

    return response


def get_username(sessionID):
    '''sends signal to MQ for getting a users username based on sessionID'''
    message = {}
    message['type'] = 'get_username'
    message['sessionID'] = sessionID

    response = send_to_db(message, 'thread_chat_proc')

    return response


def new_chat_message(username, new_message, room_id):
    '''sends signal to MQ for creating the new chat message in given chat table'''
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
    '''sends signal to MQ for getting chat messages in a given chatroom'''
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


class ThreadMain():
    '''
    Struct for organizing information for Django parsing
    within HTML thread(forum) pages
    '''

    def __init__(self, author, threadID, title, content, date):
        self.threadID = threadID
        self.content = content
        self.author = author
        self.date = date
        self.title = title


class ThreadReplies():
    '''
    Struct for organizing information for Django parsing
    within HTML reply pages
    '''

    def __init__(self, author, content, date):
        self.author = author
        self.content = content
        self.date = date
