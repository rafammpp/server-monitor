import os

abs_path = os.path.dirname(os.path.abspath(__file__))
default_ports = (22, 25, 80, 110, 143, 443, 993, 995,)
DEBUG = True
telegram_conf_path = os.path.join(abs_path, 'telegram-send.conf')
server_list_path = os.path.join(abs_path, 'server-list.dat')
recently_warning_servers_path = os.path.join(abs_path, 'recently-warning-servers.dat')
