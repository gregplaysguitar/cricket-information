import os

DEBUG = True
ASSETS_DEBUG = DEBUG

HOST = os.environ.get('HOST')
PORT = int(os.environ.get('PORT')) if os.environ.get('PORT') else None
