from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .forms import LoginForm, RegisterForm, PostThread, PostReply
from .forms import AddFriend, SendChat
from .user_processing import process_login, register_user
from .user_processing import check_session, delete_session
from .thread_processing import get_thread_info, send_new_thread
from .thread_processing import ThreadMain, ThreadReplies
from .thread_processing import get_reply_page, send_new_reply
from .thread_processing import get_friends, add_friend
from .thread_processing import create_chat, get_username, new_chat_message, get_chat_messages
import json
from .api_processing import get_recommended_friends, get_recommended_details


def validate_session(request):
    '''validate session'''
    # check for valid sessionID

    print('validating_session...')
    if 'sessionID' not in request.COOKIES:

        print('no cookie detected')
        please_log_in = True
        response = render(request, "login.html", {
            "form": LoginForm(), "please_log_in": please_log_in
            })

        #response = redirect('login')
        return ['', response]

    if 'sessionID' in request.COOKIES:
        print('cookie detected')
        session_response = check_session(request.COOKIES['sessionID'])
        print(f'response: {session_response}')
        if not session_response:
            print('cookie false or expired')
            session_expired = True
            response = render(request, 'login.html', {
                'form': LoginForm(), 'session_expired': session_expired
                })
            response.delete_cookie('sessionID')
            print('session terminated')
            return ['', response]
        else:
            return [session_response, '']


def login(request):
    '''main login page'''
    # validate post info and send to db for validation
    bad_login = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            print("loginform valid.")
            username = form.cleaned_data['username']
            pw = form.cleaned_data['pw']

            authentication = process_login(username, pw)
            if not authentication:
                print("login fail")
                bad_login = True
                return render(request, "login.html", {
                    "form": form, "bad_login": bad_login
                    })
            else:
                print("authentication successful")
                sessionID = authentication
                response = render(request, "home.html")
                response.set_cookie('sessionID', sessionID)
                return response
        else:
            print("form not valid")
            bad_login = True
            return render(request, "login.html", {
                "form": form, "bad_login": bad_login
                })

    # return render(request, 'index.html')
    return render(request, 'login.html', {
        "form": LoginForm(), "bad_login": bad_login,
        })


def index(request):
    return render(request, 'index.html')


def register(request):
    '''Register a new user'''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("Register Form Valid")
            username = form.cleaned_data['username']
            pw = form.cleaned_data['pw']
            pw2 = form.cleaned_data['pw2']

            if not pw == pw2:
                print("passwords do not match")
                bad_login = True
                return render(request, 'register.html', {
                    "form": form, "bad_login": bad_login
                    })
            else:
                registered = register_user(username, pw)
                if registered:
                    print("user was registered")
                    sessionID = registered
                    response = render(request, 'home.html')
                    response.set_cookie('sessionID', sessionID)
                    return response
                else:
                    print("user not registered, username taken")
                    bad_login = True
                    return render(request, 'register.html', {
                        "form": form, "bad_login": bad_login
                        })

    return render(request, 'register.html', {
        "form": RegisterForm()
        })


def home(request):
    '''main homepage for logged in user'''

    # validate current session
    print('sending to validate session function ...')
    session_status = validate_session(request)
    print("session status is:")
    print(session_status)
    if not session_status[0]:
        return session_status[1]

    return render(request, "home.html")


def forum(request):

    # validate current session
    session_status = validate_session(request)
    print("session status is:")
    print(session_status)
    if not session_status[0]:
        return session_status[1]

    sessionID = session_status[0]

    # validate if post request,
    # take in and send new thread to threads table
    if request.method == "POST":
        form = PostThread(request.POST)
        if form.is_valid():
            threadname = form.cleaned_data['threadname']
            threadcontent = form.cleaned_data['threadcontent']
            send_new_thread(sessionID, threadname, threadcontent)

    #list_of_threads = get_thread_info().split(';')
    #del list_of_threads[-1]
    list_of_threads = get_thread_info()
    print(list_of_threads)

    thread_posts = []
    for thread in list_of_threads:
        j = json.loads(thread)
        object = ThreadMain(j["author"], j["threadID"], j["title"], j["content"], j["date"])
        thread_posts.append(object)

    print("rendering...")
    return render(request, "forum.html", {
        "form": PostThread(), "thread_posts": thread_posts
        })


def thread(request, id):

    # take in and send new reply to database
    if request.method == "POST":
        form = PostReply(request.POST)
        if form.is_valid():
            replycontent = form.cleaned_data['replycontent']
            send_new_reply(request.COOKIES['sessionID'], str(id), replycontent)

    # get thread and its replies
    print("id is: " + str(id))
    thread_and_replies = get_reply_page(id).split('+')
    print("thread_and_replies= ..")
    print(thread_and_replies)
    thread = thread_and_replies[0]
    replies = thread_and_replies[1]

    # load thread from json to object
    j = json.loads(thread)
    thread = ThreadMain(j["author"], j["threadID"], j["title"], j["content"], j["date"])

    # segent each reply
    replies = replies.split(';')
    del replies[-1]

    # load replies from json to reply object, create list of reply objects
    reply_list = []
    for reply in replies:
        j = json.loads(reply)
        object = ThreadReplies(j["author"], j["content"], j["date"])
        reply_list.append(object)

    reply_count = len(reply_list)

    return render(request, "thread.html", {
        "thread": thread, "reply_list": reply_list, "reply_count": reply_count, "form": PostReply()
        })


def friendslist(request):

    # validate current session
    session_status = validate_session(request)
    print("session status is:")
    print(session_status)
    if not session_status[0]:
        return session_status[1]

    sessionID = session_status[0]
    friend_response = False

    # adds friend is users clicks 'add friend'
    if request.method == 'POST':
        form = AddFriend(request.POST)
        print(request.POST)
        if form.is_valid():
            print("addfriend form is valid")
            if 'friendname' in request.POST:
                friendname = request.POST['friendname']
                print(friendname)
                friend_response = add_friend(sessionID, friendname)

    recommended_friends = get_recommended_friends(sessionID)
    recommended_num = len(recommended_friends)

    print("rendering...")

    return render(request, "friendslist.html", {
        "recommended_friends": recommended_friends, "recommended_num": recommended_num, "friend_response": friend_response
        })


def recommended_details(request, username):

    # validate current session
    session_status = validate_session(request)
    print("session status is:")
    print(session_status)
    if not session_status[0]:
        return session_status[1]

    sessionID = session_status[0]

    recommended_friends = get_recommended_friends(sessionID)
    recommended_num = len(recommended_friends)
    friend_response = False
    details = get_recommended_details(sessionID, username)

    return render(request, "recommended_details.html", {
        "recommended_friends": recommended_friends, "recommended_num": recommended_num, "username": username, "details": details, "friend_response": friend_response
        })


def chat(request):

    # validate current session
    session_status = validate_session(request)
    print("session status is:")
    print(session_status)
    if not session_status[0]:
        return session_status[1]

    sessionID = session_status[0]

    friends_list = get_friends(sessionID)
    friend_number = len(friends_list)

    friend_response = True

    return render(request, "chat.html", {
        "form": AddFriend(), "friends_list": friends_list, "friend_number": friend_number, "friend_response": friend_response
        })


def chatroom(request, chat_recipient):

    # validate current session
    session_status = validate_session(request)
    print("session status is:")
    print(session_status)
    if not session_status[0]:
        return session_status[1]

    sessionID = session_status[0]

    # create chat table between two users if non-existent
    room_id = create_chat(sessionID, chat_recipient)
    username = get_username(sessionID)
    friends_list = get_friends(sessionID)
    friend_number = len(friends_list)

    return render(request, "chatroom.html", {
        "form": AddFriend(), "friends_list": friends_list, "friend_number": friend_number, "chat_recipient": chat_recipient, "form2": SendChat(), "room_id": room_id, "username": username
        })


def sendchat(request):
    room_id = request.POST['room_id']
    message = request.POST['message']
    username = request.POST['username']

    print('from djangos sendchat')

    print(room_id, message, username)

    new_message = new_chat_message(username, message, room_id)

    if new_message:
        print('from sendchat: message sent succesfully')
        return HttpResponse("message send succesfully")
    else:
        print('from sendchat: message did not send')
        return HttpResponse("message didn't send.")


def getMessages(request, room_id):
    '''receives the current chat and returns to chat page'''
    message_dict = get_chat_messages(room_id)

    return JsonResponse({"messages": message_dict})


def logout(request):
    '''log user out, delete session'''
    response = redirect('login')
    if 'sessionID' in request.COOKIES:
        print('cookie detected')
        delete_response = delete_session(request.COOKIES['sessionID'])
        print(f'delete response: {delete_response}')
        print('rendering...')
        response.delete_cookie('sessionID')
    return response
