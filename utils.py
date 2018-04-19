import socket
import requests
from datetime import datetime, time
from random import randrange
import telegram
import re
import os
try:
    from user_settings import *
except ImportError:
    from default_settings import default_ports, DEBUG, recently_warning_servers_path, server_list_path, telegram_conf_path

port_service = {22: 'SSH', 25:'SMTP', 80:'HTTP', 443: 'HTTPS', 110: 'POP3', 143:'IMAP', 993: 'IMAPS', 995: 'POP3S', 9999: 'Test port' }
shit = '💩'
fuck_u = '🖕'
good = '👌'
thumbs_up = '👍'
thumbs_down = '👎'
horns = '🤘'
spock = '🖖'
wink = '😉'
smile = '😊'
thinking = '🤔'
disapointed = '😞'
crying = '😢'
screaming = '😱'
love = '😍'
victory = '✌'

emojis_good = (good, thumbs_up, horns, spock, wink, smile, love, victory)
emojis_bad = (shit, fuck_u, thumbs_down, disapointed, crying, screaming)

if TELEGRAM_TOKEN:
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

def good():
    return emojis_good[randrange(len(emojis_good))]

def bad():
    return emojis_bad[randrange(len(emojis_bad))]
 
def is_night():
    now = datetime.now()
    now_time = now.time()
    if now_time >= time(23,00) or now_time <= time(9,00): 
        return True
    else:
        return False

def record_warning(servername, reason):
    with open(recently_warning_servers_path, 'a') as f:
        now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        f.write(f'|{servername}|{reason}|{now}|\n')

def remove_record(servername, reason):
    record = f'|{servername}|{reason}|'
    with open(recently_warning_servers_path, 'r') as f:
        lines = f.read()

    if lines.find(record) != -1:
        lines = re.sub(re.escape(record)+ r'.+\n', '', lines )
        with open(recently_warning_servers_path, 'w') as f: 
            f.write(lines)

def is_recorded(servername, reason):
    record = f'|{servername}|{reason}|'
    try:
        with open(recently_warning_servers_path, 'r') as f:
            lines = f.read()
    except FileNotFoundError:
        record_warning(servername, reason)
        return False

    if lines.find(record) == -1:
        return False
    else:
        return True

def is_recently_recorded(servername, reason):
    record = f'|{servername}|{reason}|'
    try:
        with open(recently_warning_servers_path, 'r') as f:
            lines = f.read()
    except FileNotFoundError:
        record_warning(servername, reason)
        return False

    if lines.find(record) == -1:
        record_warning(servername, reason)
        return False
    else:
        strdate = re.search(re.escape(record) + r'(.+)\|\n', lines).groups()[0] 
        d = datetime.strptime(strdate, '%Y-%m-%d %H-%M-%S')
        if abs(d - datetime.now()).seconds/3600 > 12:
            now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            lines = re.sub(re.escape(record)+ r'.+\n', record + f'{now}' + '|\n', lines )
            with open(recently_warning_servers_path, 'w') as f: 
                f.write(lines)
            return False
        return True

def send_message(message, silently=False, force=False, parse_mode=''):
    print(message)
    if is_night():
        silently = True

    if (not DEBUG and bot) or force:
        bot.send_message(chat_id=CHAT_ID, text=message, disable_notification=silently, parse_mode=parse_mode    )

def warning(servername, reason, message=None):
    if not is_recently_recorded(servername, reason):
        if message:
            send_message(f'{servername} {message}')
        elif reason == 'DIED':
            send_message(f'{servername} is died. RIP. That is a {bad()}')
        elif reason == 'SSL_ERROR':
            send_message(f'{servername} has a SLL error. https is not working. Too bad {bad()}', True)
        elif type(reason) == str and reason.startswith('HTTP_') :
            send_message(f'{servername} return a {reason} error code. Time to work {bad()}')
        elif reason == 'DNS_ERROR':
            send_message(f'{servername} could not be resolved. Maybe is died or has a bad configured dns {thinking}')
        else:
            send_message(f'{servername} not responding at port {reason} {"("+port_service[reason]+")" if reason in port_service else ""} {bad()}')
    else:
        print(f'LOG: {servername} {reason} {message}')

def compliment(servername, reason=None, message=None):
    remove_record(servername, reason)
    if message:
        send_message(f'{servername} {message}')
    elif reason == 'DIED':
        send_message(f'{servername} is now alive!! {good()} {good()}')
    elif reason == 'SSL_ERROR':
        send_message(f'{servername} is now working over https {good()} {good()}')
    elif type(reason) == str and reason.startswith('HTTP_') :
        send_message(f'{servername} server has send a good http response. Great! {good()} {good()}')
    elif reason == 'DNS_ERROR':
        send_message(f'{servername} is now resolving his dns {good()}')
    else:
        send_message(f'{servername} is now responding at port {reason} ({port_service[reason]}) {good()}{good()}')

def quote():
    now = datetime.now()
    now_time = now.time()
    if now_time >= time(23,00) and now_time < time(23,5):
        r = requests.get(url="https://andruxnet-random-famous-quotes.p.mashape.com/",
                                headers={"X-Mashape-Key": "4WVC9IL5lpmshhPQDUeefIfhbbLqp1u6Djijsnq7Ta41f631tF",
                                         "Accept": "application/json"}
                                )
        j = r.json()
        send_message(message=f'{j["quote"]} \n{j["author"]}')

def check_port(remote_server, port):
    try:
        remote_server_ip = socket.gethostbyname(remote_server)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((remote_server_ip, port))
        sock.close()
        if result != 0:
            return port
        else:
            return 'OK'

    except socket.error:
        return 'DIED'

    except socket.gaierror:
        return 'DNS_ERROR'

def error_handler(servername, reason):
    if reason == 'DIED':
        return check_port(servername, 80)
    elif reason == 'SSL_ERROR':
        return check_http(servername)
    elif reason.startswith('HTTP_') :
        return check_http(servername, ssl=False)    
    elif reason == 'DNS_ERROR':
        return check_port(servername, 80)
    else:
        return False

def check_http(remote_server, ssl=True):
    try:
        s = requests.session()
        r = s.get(f'http{"s" if ssl else ""}://{remote_server}/', timeout=5)
        s.close()

        if r.status_code != 200:
            return f'HTTP_{r.status_code}'
        else:
            return 'OK'

    except requests.exceptions.SSLError:
        return 'SSL_ERROR'
    except requests.exceptions.ConnectionError:
        return 80

def check_server(servername, ports=None):
    print("-" * 60) 
    print ("Please wait, scanning remote host", servername)
    print ("-" * 60)

    if not ports:
        ports = default_ports

    for port in ports:
        result = check_port(servername, port)
        if result != 'OK':
            warning(servername=servername, reason=result)

    if 80 in ports or 443 in ports:
        result = check_http(servername, ssl=(443 in ports))
        if result != 'OK':
            warning(servername=servername, reason=result)

    print ("-" * 60)

def recheck_servers():
    try:
        with open(recently_warning_servers_path, 'r') as file:
            print('Rechecking recorded warnings...')
            print ("-" * 60)
            for l in file:
                recorded_data = l.split('|') # |{servername}|{reason}|{datetime.now()}|\n
                recorded_data = list(filter(None, recorded_data)) # remove empty strings
                try:
                    port = int(recorded_data[1])
                    result = check_port(recorded_data[0], port)
                except ValueError:
                    result = error_handler(recorded_data[0], recorded_data[1])
                if result == 'OK':
                    reason = port if port else recorded_data
                    compliment(servername=recorded_data[0], reason=reason)
                
                print(l,' --> ', result)
            print ("-" * 60)

    except FileNotFoundError:
        return
