import os
import urllib2
import mimetypes
from urlparse import *

#custom classes
from file_worker import *

class File(object):
  def __init__(self, remote_file, thread_count):
    super(File, self).__init__()
    
    self.remote_file    = remote_file
    basename            = os.path.basename(remote_file)
    if basename != '':
      local_file        = basename 
    else:
      response          = urllib2.urlopen(self.remote_file)
      content_type      = response.info()['Content-Type']
      extension         = mimetypes.guess_extension(content_type)
      local_file        = "%s%s" % (urlparse(remote_file).hostname, extension)
    
    self.local_file     = "%s/%s" % (Settings.download_path, local_file)
    self.thread_count   = thread_count
    self.workers        = []
    self._discover()
    self._assignTasks()
  
  def _discover(self):
    response        = urllib2.urlopen(self.remote_file)
    self.file_size  = int(response.info()['Content-Length'])
    self.byte_chunk = self.file_size / self.thread_count
    Settings.log('info', 'bytes: %d' % self.byte_chunk)
    
  def _assignTasks(self):
    for i in range(self.thread_count):
      position = i * self.byte_chunk
      Settings.log('info', '%d: %d' % (i, position))
      task     = {'remote_file': self.remote_file,
                  'local_file' : self.local_file,
                  'byte_chunk' : self.byte_chunk,
                  'position'   : position}
      Settings.task_list.put(task)
    Settings.log('info', 'All tasks assigned')
    
  def download(self):
    for i in range(self.thread_count):
      worker = FileWorker()
      self.workers.append(worker)
      worker.start()
    Settings.log('info', 'All workers created')
  
  def __repr__(self):
    return "<File('%s', '%s', %d)>" % (self.remote_file, self.local_file, self.thread_count)