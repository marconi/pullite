from twisted.internet import reactor
from twisted.protocols import basic

class PulliteIOProtocol(basic.LineReceiver):
    delimiter = '\n'
    prompt = ">>>"
    commands = ["download", "quit"]
    
    def __init__(self):
        import optparse
        self.parser = optparse.OptionParser("Invalid usage: download <remote file> [-f|--filename file name] [-s|--split thread count]")
        self.parser.add_option("-f", "--filename", action="store", type="string", dest="fileName")
        self.parser.add_option("-s", "--split", action="store", type="int", dest="splitCount")

    def displayPrompt(self):
        self.transport.write(self.prompt)
    
    def connectionMade(self):
        self.printLine("Welcome to Pullite!")
    
    def printLine(self, line):
        self.sendLine(line)
        self.displayPrompt()
    
    def lineReceived(self, line):
        
        options, args = self.parser.parse_args(line.split(" "))
        
        if args[0] == "quit":
            self.transport.loseConnection()
            return
        
        if len(args) < 2:
            self.printLine(self.parser.get_usage())
            return
        
        cmd = args[0]
        url = args[1]
        
        if cmd == "download":
            self.initDownload(url, options.fileName, options.splitCount)
        self.displayPrompt()
        
    def connectionLost(self, reason):
        if reactor.running: reactor.stop()
    
    def initDownload(self, url, fileName, splitCount):
        import urllib2, os
        from pullite_downloader import PulliteDownloader
        
        # if not file name specified,
        # use the one from the url
        if not fileName: fileName = os.path.basename(url)
        if not splitCount: splitCount = 3

        response = urllib2.urlopen(url)
        
        if not response.info().has_key('Content-Length'):
            self.printLine("Unable to retrieve the file's length.") 
            return

        file_size = int(response.info()['Content-Length'])
        chunks = file_size/splitCount

        for i in range(splitCount):
            offset = i*chunks if i == 0 else (i*chunks)+1
            worker = PulliteDownloader(url, fileName, workerId=i, position=offset, headers={'range': 'bytes=%d-%d' % (offset, offset + chunks)})
            worker.deferred.addCallback(self.downloadComplete)
            worker.startDownload()
    
    def downloadComplete(self, data):
        self.printLine("done!")