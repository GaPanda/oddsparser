# -*- coding: utf-8 -*-

token = ''

ip_address = '0.0.0.0'
listen_ip_address = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше
port = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)

cert_path = './webhook_cert.pem'  # Путь к сертификату
key_path = './webhook_pkey.pem'  # Путь к приватному ключу
