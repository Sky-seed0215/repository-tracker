import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get('TOKEN')
# user = os.environ.get('USER')
# pwd = os.environ.get('PWD')
# host = os.environ.get('HOST')
# port = os.environ.get('PORT')
# db = os.environ.get('DB')
