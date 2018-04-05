import socket
import requests
from datetime import datetime
from telegram_send import send
import re
import os

default_ports = (22, 25, 80, 110, 143, 443, 993, 995,)
port_service = {22: 'SSH', 25:'SMTP', 80:'HTTP', 443: 'HTTPS', 110: 'POP3', 143:'IMAP', 993: 'IMAPS', 995: 'POP3S', 9999: 'Test port' }
shit = '💩'
fuck_u = '🖕'
good = '👌'
thumbs_up = '👍'
thumbs_down = '👎'
horns = '🤘'
spock = '🖖'

abs_path = os.path.dirname(os.path.abspath(__file__))


def record_warning(servername, reason):
    with open(os.path.join(abs_path, 'recently-warning-servers.dat'), 'a') as f:
        now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        f.write(f'{servername}|{reason}|{now}\n')

def remove_record(servername, reason):
    record = f'{servername}|{reason}|'
    with open(os.path.join(abs_path, 'recently-warning-servers.dat'), 'r') as f:
        lines = f.read()
    
    if lines.find(record) != -1:
        lines = re.sub(re.escape(record)+ r'.+\n', '', lines )
        with open(os.path.join(abs_path, 'recently-warning-servers.dat'), 'w') as f: 
            f.write(lines)

def is_recently_recorded(servername, reason):
    record = f'{servername}|{reason}|'
    try:
        with open(os.path.join(abs_path, 'recently-warning-servers.dat'), 'r') as f:
            lines = f.read()
    except FileNotFoundError:
        record_warning(servername, reason)
        return False

    if lines.find(record) == -1:
        record_warning(servername, reason)
        return False
    else:
        strdate = re.search(re.escape(record) + r'(.+)\n', lines).groups()[0] 
        d = datetime.strptime(strdate, '%Y-%m-%d %H-%M-%S')
        if abs(d - datetime.now()).seconds/3600 > 3:
            now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            lines = re.sub(re.escape(record)+ r'.+\n', record + f'{now}' + '\n', lines )
            with open(os.path.join(abs_path, 'recently-warning-servers.dat'), 'w') as f: 
                f.write(lines)
            return False
        return True

def send_message(message):
    #send(messages=None, conf=None, parse_mode=None, files=None, images=None, captions=None, timeout=30)
    print(message)
    send(conf=os.path.join(abs_path,'telegram-send.conf'), messages=(message,))
    
def warning(servername, reason, message=None):
    if not is_recently_recorded(servername, reason):
        if message:
            send_message(f'{servername} {message}')
        elif reason == 'DIED':
            send_message(f'{servername} is died. RIP. That is a {shit}')
        elif reason == 'SSL_ERROR':
            send_message(f'{servername} has a SLL error. https is not working. Too bad {thumbs_down}')
        elif type(reason) == str and reason.startswith('HTTP_') :
            send_message(f'{servername} return a {reason} error code. Time to work {thumbs_down}')
        elif reason == 'DNS_ERROR':
            send_message(f'{servername} could not be resolved. Maybe is died or has a bad configured dns. So, there is a {shit} somewhere')
        else:
            send_message(f'{servername} not responding at port {reason} {"("+port_service[reason]+")" if reason in port_service else ""} {thumbs_down}')

def compliment(servername, reason=None, message=None):
    remove_record(servername, reason)
    if message:
        send_message(f'{servername} {message}')
    elif reason == 'DIED':
        send_message(f'{servername} is now alive!! {spock} {good}')
    elif reason == 'SSL_ERROR':
        send_message(f'{servername} is now working over https {good} {thumbs_up}')
    elif reason.startswith('HTTP_') :
        send_message(f'{servername} server has send a good http response. Great! {spock} {thumbs_up}')
    elif reason == 'DNS_ERROR':
        send_message(f'{servername} is now resolving his dns {thumbs_up}')
    else:
        send_message(f'{servername} is now responding at port {reason} ({port_service[reason]}) {horns}{horns} {thumbs_up}')

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
        print ("Couldn't connect to server")
        return 'DIED'
    
    except socket.gaierror:
        return 'DNS_ERROR'

def error_handler(servername, reason):
    if reason == 'DIED':
        return check_port(servername, 80)
    elif reason == 'SSL_ERROR':
        return check_http(servername)
    elif reason.startswith('HTTP_') :
        return check_http(servername)    
    elif reason == 'DNS_ERROR':
        return check_port(servername, 80)
    else:
        return False

def check_http(remote_server):
    try:
        s = requests.session()
        r = s.get(f'https://{remote_server}/', timeout=5)
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
    print(servername)
    if not ports:
        ports = default_ports

    for port in ports:
        result = check_port(servername, port)
        if result != 'OK':
            warning(servername=servername, reason=result)

    if 80 in ports or 443 in ports:
        result = check_http(servername)
        if result != 'OK':
            warning(servername=servername, reason=result)

def recheck_servers():
    try:
        with open(os.path.join(abs_path, 'recently-warning-servers.dat'), 'r') as file:
            for l in file:
                recorded_data = l.split('|') # {servername}|{reason}|{datetime.now()}\n
                try:
                    port = int(recorded_data[1])
                    result = check_port(recorded_data[0], port)
                except ValueError:
                    result = error_handler(recorded_data[0], recorded_data[1])
                if result == 'OK': 
                    compliment(servername=recorded_data[0], reason=recorded_data[1])

    except FileNotFoundError:
        return
    