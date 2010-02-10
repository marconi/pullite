import threading
import urllib2
from Queue import Empty

#custom classes
from settings import *

class FileWorker(threading.Thread):
  def __init__(self):
    super(FileWorker, self).__init__()
  
  def run(self):
    try:
      task = Settings.task_list.get(False)
      
      request = urllib2.Request(task['remote_file'])
      bytes_range = 'bytes=%d-%d' % (task['position'], (task['position'] + (task['byte_chunk'] - 1)))
      request.add_header('Range', bytes_range)
      response = urllib2.urlopen(request)
      task['data'] = response.read()
      
      Settings.finished_tasks.put(task)
      Settings.log('info', 'Worker done')
    except Empty:
      pass