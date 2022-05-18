import json
import mysql
import chat.credentials as cred


conn = mysql.connector.connect(
        host=cred.db_host,
        user=cred.db_user,
        password=cred.db_pw,
        database=cred.db_database
        )


def get_thread_info():
    '''gets threads from database to display on forum page'''

    # grad all relevant thread information
    query = "select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID order by ts desc;"
    cursor = conn.cursor()
    cursor.execute(query)
    query_result = cursor.fetchall()

    # js strings delimited by semicolon
    json_string = ''
    for i in query_result:
        json_string += '{"author":"'+i[0]+'",'
        json_string += '"threadID":"'+str(i[1])+'",'
        json_string += '"title":"'+i[2]+'",'
        json_string += '"content":"'+i[3]+'",'
        json_string += '"date":"'+i[4].strftime('%Y-%m-%d')+'"}'
        json_string += ';'

    return json_string


def send_new_thread(sessionID, threadname, threadcontent):
    ''''creates new forum thread'''

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

    return '1'


def get_reply_page(threadID):
    '''gets replies for a given forum thread for reply page'''

    # grab al relevant forum thread information
    query = "select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID and threads.threadID=%s;"
    val = (threadID,)
    cursor = conn.cursor()
    cursor.execute(query, val)
    query_result = cursor.fetchall()

    thread_json_string = ''
    for i in query_result:
        thread_json_string += '{"author":"'+i[0]+'",'
        thread_json_string += '"threadID":"'+str(i[1])+'",'
        thread_json_string += '"title":"'+i[2]+'",'
        thread_json_string += '"content":"'+i[3]+'",'
        thread_json_string += '"date":"'+i[4].strftime('%Y-%m-%d')+'"}'
        thread_json_string += '+'

    # grab all relevant reply data for the given forum thread
    query = "select users.uname, replies.content, replies.replyts from users,replies where users.userID=replies.userID and replies.threadID=%s order by replies.replyts desc;"
    val = (threadID,)
    cursor.execute(query, val)
    query_result = cursor.fetchall()

    replies_json_string = ''
    for i in query_result:
        replies_json_string += '{"author":"'+i[0]+'",'
        replies_json_string += '"content":"'+i[1]+'",'
        replies_json_string += '"date":"'+i[2].strftime('%Y-%m-%d')+'"}'
        replies_json_string += ';'

    return (thread_json_string + replies_json_string)

def send_new_reply(sessionID, threadID, replycontent):
    '''create/send new reply on given threadID to database'''
    # grab the users id
    query = "select userID from sessions where sessionID=%s;"
    val = (sessionID,)
    cursor = conn.cursor()
    cursor.execute(query, val)
    query_result = cursor.fetchall()

    # return false if session not vaild
    if not query_result:
        return ''
    userID = query_result[0][0]

    # inserts new reply into replies table
    query = "insert into replies (threadID, userID, content) values (%s, %s, %s);"
    val = (threadID, userID, replycontent)
    cursor.execute(query, val)
    conn.commit()

    return '1'

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
