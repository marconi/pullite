import sys
import logging

from file import File

logging.basicConfig()
log = logging.getLogger(__file__)


if __name__ == "__main__":
    try:
        while True:
            request = raw_input('>> ')
            if len(request.strip()) == 0:
                log.error('error', 'Invalid usage: pullite <remote file> [thread count]')
            else:
                tmp = request.split()

                # check if user wan't to quit
                if tmp[0] == 'quit':
                    break

                remote_file = tmp[0]
                if len(tmp) == 1:
                    workers_count = 3
                else:
                    workers_count = int(tmp[1])

                try:
                    File(remote_file, workers_count).download()
                except ValueError, e:
                    log.error(e)
    except KeyboardInterrupt:
        sys.exit(1)
