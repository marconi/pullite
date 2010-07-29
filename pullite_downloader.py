import os, types
from twisted.web import client
from twisted.internet import defer, reactor
from twisted.python import failure

class PulliteDownloader(client.HTTPClientFactory):
    """
    Download to a file.
    
    This is a modified version of the HTTPDownloader class since
    HTTPDownloader assumes that file already exist on request for partial data.
    """
    
    protocol = client.HTTPPageDownloader
    value = None
    
    def __init__(self, url, fileOrName, workerId=0, position=0, method='GET',
                postdata=None, headers=None, supportPartial=True, agent="Twisted client"):
        self.requestedPartial = supportPartial
        self.position = position
        self.workerId = workerId
        if isinstance(fileOrName, types.StringTypes):
            self.fileName = fileOrName
            self.file = None
        else:
            self.file = fileOrName
        client.HTTPClientFactory.__init__(self, url, method=method, postdata=postdata, headers=headers, agent=agent)
        self.deferred = defer.Deferred()
        self.waiting = 1
    
    def gotHeaders(self, headers):
        if headers.has_key('content-length'):
            self.totalLength = int(headers['content-length'][0])
        else:
            self.totalLength = 0
        self.currentLength = 0.0
        
        if self.requestedPartial:
            contentRange = headers.get("content-range", None)
            if not contentRange:
                # server doesn't support partial requests
                self.requestedPartial = False
                return
    
    def openFile(self, partialContent):
        if partialContent and os.path.exists(self.fileName):
            file = open(self.fileName, 'rb+')
            file.seek(self.position)
        else:
            file = open(self.fileName, 'wb')
        return file
    
    def pageStart(self, partialContent):
        if partialContent and not self.requestedPartial:
            raise ValueError, "we shouldn't get partial content response if we didn't want it!"
        if self.waiting:
            self.waiting = 0
            try:
                if not self.file:
                    self.file = self.openFile(partialContent)
            except IOError:
                #raise
                self.deferred.errback(failure.Failure())
    
    def pagePart(self, data):
        if not self.file:
            return
        try:
            self.file.write(data)
            
            self.currentLength += len(data)
            if self.totalLength:
                percent = "%i%%" % ((self.currentLength/self.totalLength)*100)
            else:
                percent = '%dK' % (self.currentLength/1000)
            # print "%d:Progress: %s" % (self.workerId ,percent)
        
        except IOError:
            #raise
            self.file = None
            self.deferred.errback(failure.Failure())
    
    def pageEnd(self):
        if not self.file:
            return
        try:
            self.file.close()
        except IOError:
            self.deferred.errback(failure.Failure())
            return
        self.deferred.callback(self.value)
    
    def startDownload(self):
        reactor.connectTCP(self.host, self.port, self)