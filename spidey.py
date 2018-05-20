#!/usr/bin/env python2.7
#Bui's Spidey

import getopt
import logging
import mimetypes
import os
import signal
import socket
import sys

# Constants

ADDRESS  = '0.0.0.0'
PORT     = 9234
BACKLOG  = 0
PROGRAM  = os.path.basename(sys.argv[0])
DOCROOT  = os.path.abspath(os.curdir)
LOGLEVEL = logging.INFO

ICON_MAPPING = {
    '.py'   : 'file-code-o',
    '.sh'   : 'file-code-o',
    '.md'   : 'file-text-o',
    '.gif'  : 'file-image-o',
    '.jpg'  : 'file-image-o',
    '.png'  : 'file-image-o',
    '.txt'  : 'file-text-o',
}

# Utility Functions

def usage(exit_code=0):
    print >>sys.stderr, '''Usage: {program} [-d DOCROOT -p PORT -f -v]

Options:

    -h         Show this help message
    -f         Enable forking mode
    -v         Set logging to DEBUG level

    -d DOCROOT Set root directory (default is current directory)
    -p PORT    TCP Port to listen to (default is {port})
'''.format(port=PORT, program=PROGRAM)
    sys.exit(exit_code)

def directory_compare(a, b):
    if os.path.isdir(a) and os.path.isdir(b):
        return cmp(a, b)

    if os.path.isdir(a):
        return -1

    if os.path.isdir(b):
        return 1

    return cmp(a, b)

# BaseHandler Class

class BaseHandler(object):

    def __init__(self, fd, address):
        ''' Construct handler from file descriptor and remote client address '''
        self.logger  = logging.getLogger()        # Grab logging instance
        self.socket  = fd                         # Store socket file descriptor
        self.address = '{}:{}'.format(*address)   # Store address
        self.stream  = self.socket.makefile('w+') # Open file object from file descriptor

        self.debug('Connect')

    def debug(self, message, *args):
        ''' Convenience debugging function '''
        message = message.format(*args)
        self.logger.debug('{} | {}'.format(self.address, message))

    def info(self, message, *args):
        ''' Convenience information function '''
        message = message.format(*args)
        self.logger.info('{} | {}'.format(self.address, message))

    def warn(self, message, *args):
        ''' Convenience warning function '''
        message = message.format(*args)
        self.logger.warn('{} | {}'.format(self.address, message))

    def error(self, message, *args):
        ''' Convenience error function '''
        message = message.format(*args)
        self.logger.error('{} | {}'.format(self.address, message))

    def exception(self, message, *args):
        ''' Convenience exception function '''
        message = message.format(*args)
        self.logger.exception('{} | {}'.format(self.address, message))

    def handle(self):
        ''' Handle connection '''
        self.debug('Handle')
        raise NotImplementedError

    def finish(self):
        ''' Finish connection by flushing stream, shutting down socket, and
        then closing it '''
        self.debug('Finish')
        try:
            self.stream.flush()
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            pass    # Ignore socket errors
        finally:
            self.socket.close()

# HTTPHandler Class

class HTTPHandler(BaseHandler):

    def __init__(self, fd, address, docroot=None):
        BaseHandler.__init__(self, fd, address)
        self.docroot = docroot or DOCROOT

    def handle(self):
        # TODO: Parse request
        self._parse_request()

        # TODO: Construct uripath
        self.uripath = os.path.normpath(self.docroot + os.environ['REQUEST_URI'])

        # TODO: Check if uripath exists and that it starts with docroot,
        # otherwise display 404
        if not os.path.exists(self.uripath) or not self.uripath.startswith(self.docroot):
            self._handle_error(404)
        elif os.path.isfile(self.uripath) and os.access(self.uripath, os.X_OK):
            self._handle_script()
        elif os.path.isfile(self.uripath) and os.access(self.uripath, os.R_OK):
            self._handle_file()
        elif os.path.isdir(self.uripath) and os.access(self.uripath, os.R_OK):
            self._handle_directory()
        else:
            self._handle_error(403)

    def _parse_request(self):
        # TODO: Set REMOTE_ADDR, REMOTE_HOST, REMOTE_PORT from address
        # information
        os.environ['REMOTE_ADDR'] = self.address.split(':', 1)[0]
        os.environ['REMOTE_HOST'] = self.address.split(':', 1)[0]
        os.environ['REMOTE_PORT'] = self.address.split(':', 1)[1]

        # TODO: Read stream and set REQUEST_METHOD, REQUEST_URI, QUERY_STRING
        data = self.stream.readline().strip().split()
        self.debug('Parsing {}', data)
        os.environ['REQUEST_METHOD'] = data[0]
        os.environ['REQUEST_URI']    = data[1].split('?', 1)[0]
        os.environ['QUERY_STRING']   = data[1].split('?', 1)[1] if '?' in data[1] else ''

        # TODO: Read stream until empty line and parse headers
        data = self.stream.readline().strip()
        while data:
            data = data.split(':', 1)
            key  = 'HTTP_' + data[0].upper().replace('-', '_')
            os.environ[key] = data[1].strip()
            data = self.stream.readline().strip()

    def _handle_file(self):
        self.debug('Handle File')
        mimetype, _ = mimetypes.guess_type(self.uripath)
        if mimetype is None:
            mimetype = 'application/octet-stream'

        self.stream.write('HTTP/1.0 200 OK\r\nContent-Type: {}\r\n\r\n'.format(mimetype))
        with open(self.uripath, 'rb') as file:
            data = file.read()
            while data:
                self.stream.write(data)
                data = file.read()

    def _handle_directory(self):
        self.debug('Handle Directory')
        self.stream.write('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
        self.stream.write('''<!DOCTYPE html>
<html lang="en">
<head>
<title>{REQUEST_URI}</title>
<link href="https://www3.nd.edu/~pbui/static/css/blugold.css" rel="stylesheet">
<link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css" rel="stylesheet">
</head>
<body>
<div class="container">
<div class="page-header">
<h2>Directory Listing: {REQUEST_URI}</h2>
</div>
<table class="table table-striped">
<thead>
<th>Type</th>
<th>Name</th>
<th>Size</th>
</thead>
<tbody>
'''.format(**os.environ))
        paths = [os.path.join(self.uripath, n) for n in os.listdir(self.uripath)]
        for path in sorted(paths, cmp=directory_compare):
            name = os.path.basename(path)
            url  = os.path.normpath(os.path.join(os.environ['REQUEST_URI'], name))

            if os.path.isdir(path):
                icon = 'folder-o'
                size = '-'
            else:
                icon = ICON_MAPPING.get(os.path.splitext(path)[-1], 'file-o')
                size = os.path.getsize(path)

            self.stream.write('''<tr>
<td><i class="fa fa-{icon}"></i></td>
<td><a href="{url}">{name}</a></td>
<td>{size}</td>
</tr>
'''.format(icon=icon, name=name, url=url, size=size))

        self.stream.write('''</tbody>
</table>
</div>
</body>
</html>''')

    def _handle_script(self):
        self.debug('Handle Script')
        try:
            signal.signal(signal.SIGCHLD, signal.SIG_DFL)
            for line in os.popen(self.uripath):
                self.stream.write(line)
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        except (IOError, OSError) as e:
            self.exception('Unable to popen: {}', e)

    def _handle_error(self, error):
        self.debug('Handle Error')
        self.stream.write('HTTP/1.0 {} OK\r\nContent-Type: text/html\r\n\r\n'.format(error))
        self.stream.write('''<!DOCTYPE html>
<html lang="en">
<head>
<title>{0} Error</title>
<link href="https://www3.nd.edu/~pbui/static/css/blugold.css" rel="stylesheet">
<link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css" rel="stylesheet">
</head>
<body>
<div class="container">
<div class="page-header">
<h2>{0} Error</h2>
</div>
<div class="thumbnail">
    <img src="http://9buz.com/content/uploads/images/September2014/picard-seriously.jpg" class="img-responsive">
</div>
</div>
</body>
</html>
'''.format(error))

# TCPServer Class

class TCPServer(object):

    def __init__(self, address=ADDRESS, port=PORT, handler=HTTPHandler, forking=False):
        ''' Construct TCPServer object with the specified address, port, and
        handler '''
        self.logger  = logging.getLogger()                              # Grab logging instance
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Allocate TCP socket
        self.address = address                                          # Store address to listen on
        self.port    = port                                             # Store port to lisen on
        self.forking = forking                                          # Store forking mode
        self.handler = handler                                          # Store handler for incoming connections

    def run(self):
        ''' Run TCP Server on specified address and port by calling the
        specified handler on each incoming connection '''
        try:
            # Bind socket to address and port and then listen
            self.socket.bind((self.address, self.port))
            self.socket.listen(BACKLOG)
        except socket.error as e:
            self.logger.error('Could not listen on {}:{}: {}'.format(self.address, self.port, e))
            sys.exit(1)

        self.logger.info('Listening on {}:{}...'.format(self.address, self.port))

        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        while True:
            # Accept incoming connection
            client, address = self.socket.accept()
            self.logger.debug('Accepted connection from {}:{}'.format(*address))

            # Instantiate handler, handle connection, finish connection
            if not self.forking:
                self._handle(client, address)
            else:
                self.logger.debug('Forking...')
                try:
                    pid = os.fork()
                except OSError as e:
                    self.logger.error('Unable to fork: {}'.format(e))
                    continue

                if pid == 0:
                    self._handle(client, address)
                    os._exit(0)
                else:
                    client.close()

    def _handle(self, client, address):
        self.logger.debug('Handling...')
        try:
            handler = self.handler(client, address)
            handler.handle()
        except Exception as e:
            handler.exception('Exception: {}', e)
        finally:
            handler.finish()

# Main Execution

if __name__ == '__main__':
    # Parse command-line arguments
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hfd:p:v")
    except getopt.GetoptError as e:
        usage(1)

    for option, value in options:
        if option == '-p':
            PORT = int(value)
        elif option == '-f':
            FORKING = True
        elif option == '-d':
            DOCROOT = value
        elif option == '-v':
            LOGLEVEL = logging.DEBUG
        else:
            usage(1)

    # Set logging level
    logging.basicConfig(
        level   = LOGLEVEL,
        format  = '[%(asctime)s] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    # Instantiate and run server
    server = TCPServer(port=PORT, forking=FORKING)

    try:
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)

