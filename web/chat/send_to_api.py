from chat.PikaClasses import RpcPublisher
import chat.credentails as cred
import json

'''
api driver which established MQ rpc publish connection
'''


def send_to_api(message, queue):
    rpc_publish = RpcPublisher(cred.mq_user, cred.mq_pw, cred.mq_ip)
    print(" [x] Publishing message to api...")
    print(message)

    # dumping dict (json) to string
    message = json.dumps(message)

    response = rpc_publish.call(message, queue)
    print(" [.] Got %r" % response)

    return response.decode('utf-8')
