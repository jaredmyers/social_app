import PikaClasses
import credentials as cred

# hmmmmmm

'''
The database driver which establishes an MQ rpc subscriber connection
listens for incoming database requests on 'check_session' queue
'''

queue = 'check_session'
sub_conn = PikaClasses.RunSubscriber(cred.user, cred.pw, cred.ip_address)
sub_conn.rpc_subscribe(queue)
