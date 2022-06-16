# from PikaClasses import RunSubscriber
import PikaClasses
import credentials as cred

exchange = 'log_exchange'
log_path = './event.log'

connection = PikaClasses.RunSubscriber(cred.user, cred.pw, cred.ip_address)
connection.listen_fanout(exchange, log_path)
