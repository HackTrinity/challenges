#!/usr/bin/env python3
import re
import threading
import os
import time
import mimetypes
import socketserver

SERVER_NAME = 'My Cool HTTP Server/0.1'
REQ_LINE_REGEX = re.compile(r'(?P<method>(GET|POST|PUT|DELETE|PATCH|TRACE|CONNECT|OPTIONS)) (?P<uri>\S+) HTTP\/1\.1')

HDR_SERVER = f'Server: {SERVER_NAME}\r\n'
HDR_CACHE = 'Cache-Control: no-cache\r\n'
RES_BAD_REQUEST = \
    'HTTP/1.1 400 You Don\'t Make Sense\r\n' + \
    HDR_SERVER + \
    HDR_CACHE + \
    '\r\n'
RES_NOT_FOUND = \
    'HTTP/1.1 404 Couldn\'t Find it\r\n' + \
    HDR_SERVER + \
    HDR_CACHE + \
    '\r\n'
RES_NOT_IMPLEMENTED = \
    'HTTP/1.1 501 I Can\'t Do That\r\n' + \
    HDR_SERVER + \
    HDR_CACHE + \
    '\r\n'
RES_INTERNAL_ERROR = \
    'HTTP/1.1 500 Oops\r\n' + \
    HDR_SERVER + \
    HDR_CACHE + \
    '\r\n'
RES_OK = \
    'HTTP/1.1 200 Yeah Alright Then\r\n' + \
    HDR_SERVER + \
    HDR_CACHE + \
    'Content-Type: {mime}\r\n' + \
    '\r\n'
RES_REDIRECT = \
    'HTTP/1.1 301 Move Along\r\n' + \
    HDR_SERVER + \
    HDR_CACHE + \
    'Location: {uri}' + \
    '\r\n'

DIR_LIST = '''
<html>
    <head>
        <title>My Cool HTTP Server - {path}</title>
    </head>
    <body>
        <h1>My Cool HTTP Server</h1>
        <p>Directory listing for "{path}"</p>
        <ul>
            {entries}
        </ul>
    </body>
</html>
'''

class CoolHTTPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        req = self.request.recv(4096).decode('utf-8').split('\r\n')
        req_line = REQ_LINE_REGEX.match(req[0])

        if not req_line:
            self.request.sendall(RES_BAD_REQUEST.encode('utf-8'))
            return

        if req_line.group('method') != 'GET':
            self.request.sendall(RES_NOT_IMPLEMENTED.encode('utf-8'))
            return


        try:
            path = req_line.group('uri')
            if path.startswith('/'):
                path = path[1:]

            if not path:
                path = './'

            print(f'{int(time.time())} {req_line.group("method")} {path}')

            mime, _ = mimetypes.guess_type(path)
            if not mime:
                mime = 'text/plain'

            if not os.path.exists(path):
                self.request.sendall(RES_NOT_FOUND.encode('utf-8'))
                return
            if os.path.isdir(path):
                if not path.endswith('/'):
                    self.request.sendall(RES_REDIRECT.format(uri=path + '/').encode('utf-8'))
                    return

                index = os.path.join(path, 'index.html')
                if os.path.isfile(index):
                    path = index
                    mime = 'text/html'
                else:
                    entries = ['..']
                    for entry in os.listdir(path):
                        if os.path.isdir(os.path.join(path, entry)):
                            entry += '/'
                        entries.append(entry)
                    entries = list(map(lambda e: f'<li><a href="{e}">{e}</a></li>', entries))
                    self.request.sendall(RES_OK.format(mime='text/html').encode('utf-8'))
                    self.request.sendall(DIR_LIST.format(path=path, entries='\n'.join(entries)).encode('utf-8'))
                    return

            with open(path, 'rb') as f:
                self.request.sendall(RES_OK.format(mime=mime).encode('utf-8'))
                while data := f.read(4096):
                    self.request.send(data)
        except:
            self.request.sendall(RES_INTERNAL_ERROR.encode('utf-8'))
            raise

socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(('0.0.0.0', 80), CoolHTTPHandler) as server:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
