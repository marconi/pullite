from twisted.internet import stdio, reactor
from pullite_ioprotocol import PulliteIOProtocol

if __name__ == '__main__':    
    stdio.StandardIO(PulliteIOProtocol())
    reactor.run()