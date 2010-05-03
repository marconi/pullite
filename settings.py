import os
import logging
from Queue import *

class Settings(object):
  
  download_path  = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'downloads')
  task_list      = Queue(0)
  finished_tasks = Queue(0)
  logging.basicConfig(level=logging.DEBUG)
  
  def __init__(self):
    super(Settings, self).__init__()
  
  @staticmethod
  def log(type, msg):
    getattr(logging, type)(msg)