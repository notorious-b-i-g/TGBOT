API_TOKEN = '***REVOKED-TELEGRAM-TOKEN***'

DB_CONFIG = {
    'host': '127.0.0.1',  # Локальный хост, так как мы будем использовать туннель
    'port': 3306,
    'user': 'h540890_viniki',
    'password': '***REVOKED-DB-PASSWORD***',
    'db': 'h540890_viniki'
}

SSH_CONFIG = {
    'ssh_host': 'ssh.hosting.masterhost.ru',
    'ssh_port': 22,
    'ssh_user': 'h540890',
    'ssh_password': '***REVOKED-SSH-PASSWORD***',
    'remote_bind_address': ('h540890_viniki.mysql.masterhost.ru', 3306)
}

admins = ['chinanumb2', 'burzhuykaa','fullmetalldickk']
