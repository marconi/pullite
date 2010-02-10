import os, time, urllib2, mimetypes
from urlparse import *

#custom classes
from file_worker import FileWorker
from settings import Settings
from table_factory import TableFactory

#database table classes
from table_classes import Download

class File(object):
  def __init__(self, **kwargs):
    super(File, self).__init__()
    
    self.name           = kwargs.get('name')
    self.remote_file    = kwargs.get('remote_file')
    self.thread_count   = kwargs.get('thread_count')
    self.workers        = []
    self.created        = time.strftime('%b %d, %Y - %I:%M %p')
    self._discoverFile()
    
    #save it if its a new download
    if kwargs.get('new'): self._saveFile() 
    
    self._assignTasks()
    
  def _discoverFile(self):
    response            = urllib2.urlopen(self.remote_file)
    self.file_size      = int(response.info()['Content-Length'])
    self.byte_chunk     = self.file_size / self.thread_count
    basename            = os.path.basename(self.remote_file)
    
    if basename != '':
      local_file        = basename 
    else:
      content_type      = response.info()['Content-Type']
      extension         = mimetypes.guess_extension(content_type)
      local_file        = "%s%s" % (urlparse(remote_file).hostname, extension)
    
    self.local_file     = "%s/%s" % (Settings.download_path, local_file)
    
  def _saveFile(self):
    file = Download(name=self.name, url=self.remote_file,
                    progress=0, size=File.getHumanSize(self.file_size),
                    completed=0, created=self.created)
    
    TableFactory.session.add(file)
    TableFactory.session.commit()

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

  @staticmethod
  def getHumanSize(num):
    for x in ['bytes','KB','MB','GB','TB']:
      if num < 1024.0:
        return "%3.1f%s" % (num, x)
      num /= 1024.0
      
if __name__ == '__main__':  
  file = File('http://demilane.com/dl/wall/redchristmas/redChristmas-2560x1600.jpg', 5)
  print File.getHumanSize(file.file_size)