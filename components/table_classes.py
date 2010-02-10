class Download(object):
  def __init__(self, **kwargs):
    self.name      = kwargs.get('name')
    self.url       = kwargs.get('url')
    self.progress  = kwargs.get('progress')
    self.size      = kwargs.get('size')
    self.completed = kwargs.get('completed')
    self.created   = kwargs.get('created')