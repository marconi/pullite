import os
import urllib2
import mimetypes
from urlparse import *
import math
import time
from datetime import datetime, timedelta
import gevent
from gevent import monkey

from conf import Config

monkey.patch_socket()
config = Config.get_config()


class File(object):

    def __init__(self, remote_file, workers_count=2):
        self.remote_file = remote_file

        # get to know the file
        response = urllib2.urlopen(self.remote_file)
        file_info = response.info()
        content_type = file_info['Content-Type']

        # use the file's base name as the local name
        # for the downloaded file.
        basename = os.path.basename(remote_file)
        if basename:
            local_file = basename
        else:
            # if we can't get a base name form remote file,
            # lets try figure it out.
            extension = mimetypes.guess_extension(content_type)
            local_file = "%s%s" % (urlparse(remote_file).hostname, extension)

        # assign file meta data
        self.local_file = "%s/%s" % (config.download_path, local_file)
        self.workers_count = workers_count
        self.workers = []
        self.file_size = int(file_info['Content-Length'])
        self.chunk_size = int(math.ceil(self.file_size / self.workers_count))

        print "File size: %s" % self.file_size
        print "File chunks: %s" % self.chunk_size

        self.deploy_workers()

    def deploy_workers(self):
        filesize = self.file_size
        for i in range(self.workers_count):
            # calculate file bytes block to read
            start = i * self.chunk_size
            end = start + (self.chunk_size - 1)

            filesize -= self.chunk_size
            print "Remaining: %s" % filesize

            # if we're already at the end block,
            # of the remaining bytes doesn't fit on a single block,
            # lets just read all the remaining
            if filesize <= self.chunk_size or \
                ((end + filesize) <= self.chunk_size * 2):
                end = self.file_size

            # spawn some greenlet workers
            self.workers.append(gevent.spawn(self._download, start, end))

    def _download(self, start, end):
        request = urllib2.Request(self.remote_file)
        request.add_header('Range', 'bytes=%d-%d' % (start, end))
        response = urllib2.urlopen(request)

        print "Chunk: %d to %d" % (int(start), int(end))

        return start, end, response.read()

    def download(self):
        start_time = time.time()

        # let the workers do their job
        gevent.joinall(self.workers)

        # grab the handler to the file
        handle = open(self.local_file, 'wb')

        # when all workers are done,
        # merge all the gathered datas
        for worker in self.workers:
            start, end, data = worker.value

            print "Appending %d bytes at %d to %d for %s" % (
                len(data), int(start), int(end), self.remote_file)

            # moved to the position of the read data
            # and write the newly downloaded chunks
            handle.seek(start)
            handle.write(data)
        handle.close()

        duration = int(time.time() - start_time)

        print "DONE: %s" % self.remote_file
        print "Duration: %s" % time.strftime("%H:%M:%S", time.gmtime(duration))
