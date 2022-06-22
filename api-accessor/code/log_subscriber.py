# from PikaClasses import RunSubscriber
import PikaClasses
import credentials as cred

# subscribes to a given MQ exchange for logs
# writes those logs to event.log

exchange = 'log_exchange'
log_path = './event.log'

connection = PikaClasses.RunSubscriber(cred.user, cred.pw, cred.ip_address)
connection.listen_fanout(exchange, log_path)
