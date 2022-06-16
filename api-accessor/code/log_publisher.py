# from PikaClasses import RunPublisher
import PikaClasses
import credentials as cred


def send_log(log_lines):

    exchange = 'log_exchange'
    connection = PikaClasses.RunPublisher(cred.user, cred.pw, cred.ip_address)
    connection.fan_publish(exchange, log_lines)
