import os
import urllib2
import mimetypes
from urlparse import *
import gevent

from conf import Config

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
        self.chunk_size = self.file_size / self.workers_count
        self.deploy_workers()

    def deploy_workers(self):
        for i in range(self.workers_count):
            # calculate file pointer
            pointer = i * self.chunk_size

            # spawn some greenlet workers
            self.workers.append(gevent.spawn(self._download, pointer))

    def download(self):
        # let the workers do their job
        gevent.joinall(self.workers)

        # when all workers are done,
        # merge all the gathered datas
        for worker in self.workers:
            start, end, data = worker.value
            self.append_chunk(start, end, data)

        print "DONE: %s" % self.remote_file

    def _download(self, start):
        request = urllib2.Request(self.remote_file)
        end = start + (self.chunk_size - 1)

        request.add_header('Range', 'bytes=%d-%d' % (start, end))
        response = urllib2.urlopen(request)

        print "Chunk: %d to %d" % (int(start), int(end))

        return start, end, response.read()

    def append_chunk(self, pointer, end, data):
        print "Appending %d bytes at %d to %d for %s" % (
            len(data), int(pointer), int(end), self.remote_file)
        handle = None

        # check if file already exist,
        # grabe its handle
        if os.path.exists(self.local_file):
            handle = open(self.local_file, 'wb')

        # if we don't have a handle to the file
        # yet, then this must have been a new file
        # so lets create a new handle.
        if not handle:
            handle = open(self.local_file, 'wb')

        # moved to the position of the read data
        # and write the newly downloaded chunks
        if handle:
            handle.seek(pointer)
            handle.write(data)
            handle.close()
