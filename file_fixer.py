import threading
import os

#custom classes
from settings import *

class FileFixer(threading.Thread):
  def __init__(self):
    super(FileFixer, self).__init__()
    Settings.log('debug', 'Fixer created, ready for downloads')
    
  def run(self):
    while True:
      task = Settings.finished_tasks.get()
      if task == 'quit': break
      existing_data = None
      
      #check if file already exist and
      #read existing data
      if os.path.isfile(task['local_file']):
        file = open(task['local_file'], 'rb')
        existing_data = file.read()
        file.close()
      
      #open the file again for writing
      file = open(task['local_file'], 'wb')
      
      #if we have existing data, append it first
      if existing_data != None:
        file.write(existing_data)
      
      file.seek(task['position'])
      file.write(task['data'])
      file.close()
      Settings.log('info', 'Fixer done')
    Settings.log('info', 'Shutting down resources')