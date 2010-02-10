import logging
from Queue import *
from PyQt4.QtGui import *

class Settings(object):
  
  download_path  = "%s/%s" % (QDesktopServices.storageLocation(QDesktopServices.HomeLocation), 'PulliteDownloads')
  task_list      = Queue(0)
  finished_tasks = Queue(0)
  logging.basicConfig(level=logging.DEBUG)
  
  @staticmethod
  def log(type, msg):
    getattr(logging, type)(msg)