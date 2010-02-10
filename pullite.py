import sys

#custom classes
from settings import *
from file_fixer import *
from file import *

if __name__ == "__main__":

  fixer = FileFixer()
  fixer.start()
  
  try:
    while True:
      request = raw_input('>> ')
      if len(request.strip()) == 0:
        Settings.log('error', 'Invalid usage: pullite <remote file> [thread count]')
      else:
        request       = request.split()
        if request[0] == 'quit': break
        remote_file   = request[0]
        threads_count = int(request[1]) if len(request) > 1 else 3
        try:
          File(remote_file, threads_count).download()
        except ValueError:
          Settings.log('error', 'Invalid file URL')
  except KeyboardInterrupt:
    Settings.finished_tasks.put('quit')
