import os

connection = {
    'address': os.environ.get('AMI_HOST', '127.0.0.1'),
    'port': int(os.environ.get('AMI_PORT', '5038')),
}

login = {
    'username': os.environ.get('AMI_USER', 'admin'),
    'secret': os.environ.get('AMI_SECRET', 'password'),
}
