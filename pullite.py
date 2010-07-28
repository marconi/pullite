import os, types
from twisted.web import client, http
from twisted.internet import stdio, defer, reactor
from twisted.python import failure
from twisted.protocols import basic

class HTTPProgressDownloader(client.HTTPClientFactory):
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
    
def downloadComplete(data):
    print "done!"

def initDownload(ioProtocol, url, fileName, splitCount):
    import urllib2
    
    # if not file name specified,
    # use the one from the url
    if not fileName: fileName = os.path.basename(url)
    if not splitCount: splitCount = 3
    
    response = urllib2.urlopen(url)
    
    if not response.info().has_key('Content-Length'):
        ioProtocol.printLine("Unable to retrieve the file's length.") 
        return
    
    file_size = int(response.info()['Content-Length'])
    chunks = file_size/splitCount
    
    for i in range(splitCount):
        offset = i*chunks if i == 0 else (i*chunks)+1
        worker = HTTPProgressDownloader(url, fileName, workerId=i, position=offset, headers={'range': 'bytes=%d-%d' % (offset, offset + chunks)})
        worker.deferred.addCallback(downloadComplete)
        worker.startDownload()

class PulliteIOProtocol(basic.LineReceiver):
    delimiter = '\n'
    prompt = ">>>"
    commands = ["download", "quit"]

    def displayPrompt(self):
        self.transport.write(self.prompt)
    
    def connectionMade(self):
        self.printLine("Welcome to Pullite!")
    
    def printLine(self, line):
        self.sendLine(line)
        self.displayPrompt()
    
    def lineReceived(self, line):
        user_input = line.strip().split(" ")
        
        if user_input[0] == "quit":
            self.transport.loseConnection()
            return
        
        if len(user_input) < 2:
            self.printLine("Invalid usage: download <remote file> [file name] [thread count]")
            return
        
        cmd = user_input[0]
        url = user_input[1]
        
        fileName = user_input[2] if len(user_input) >= 3 and user_input[2] else None
        splitCount = user_input[3] if len(user_input) == 4 and user_input[3] else None
        
        if cmd == "download":
            if not url:
                self.printLine("Invalid usage: download <remote file> [file name] [thread count]")
            else:
                initDownload(self, url, fileName, int(splitCount))
        
    def connectionLost(self, reason):
        if reactor.running: reactor.stop()
    
if __name__ == '__main__':
    stdio.StandardIO(PulliteIOProtocol())
    reactor.run()