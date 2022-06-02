import PikaClasses
import credentials as cred

'''
The database driver which establishes an MQ rpc subscriber connection
listens for incoming database requests on 'threads' queue
'''

queue = 'threads'
sub_conn = PikaClasses.RunSubscriber(cred.user, cred.pw, cred.ip_address)
sub_conn.rpc_subscribe(queue)