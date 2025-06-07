import socket
import ssl

class Socket:
    def __init__(self, url):
        self.url = url
        self.socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        self.headers = {}
        self.fill_headers()

    def fill_headers(self):
        self.headers['Host'] = self.url.host
        self.headers['Connection'] = 'close'

    def connect(self):
        self.socket.connect((self.url.host, self.url.get_port()))
        if self.url.scheme == 'https':
            ctx = ssl.create_default_context()
            self.socket = ctx.wrap_socket(self.socket, server_hostname=self.url.host)

    def request(self):
        request = 'GET {} HTTP/1.1\r\n'.format(self.url.path)
        for key, val in self.headers.items():
            request += '{}: {}\r\n'.format(key, val)
        request += '\r\n'
        self.socket.send(request.encode('utf8'))

    def response(self):
        response = self.socket.makefile('r', encoding='utf8', newline='\r\n')
        statusline = response.readline()
        version, status, explanation = statusline.split(' ', 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line == '\r\n': break
            header, value = line.split(':', 1)
            response_headers[header.casefold()] = value.strip()

        assert 'transfer-encoding' not in response_headers
        assert 'content-encoding' not in response_headers

        content = response.read()
        self.socket.close()
        
        return content
    
    def lex(self, body):
        text = ''
        in_tag = False
        for c in body:
            if c == '<':
                in_tag = True
            elif c == '>':
                in_tag = False
            elif not in_tag:
                text += c
        return text
    
    def load_content(self):
        text = ''
        if self.url.scheme != 'file':
            self.connect()
            self.request()
            text = self.lex(self.response())
        else:
            text = '2'
        return text

class URL:
    def __init__(self, url):
        self.scheme, url = url.split('://', 1)
        assert self.scheme in ['http', 'https', 'file']
        
        if '/' not in url:
            url += '/'
        self.host, url =  url.split('/', 1)

        self.port = ''
        if ':' in self.host:
            self.host, self.port = self.host.split(':', 2)

        url = '/' + url
        self.path = url

    def __str__(self):
        str = self.scheme + '://' + self.host
        if self.port:
            str += ':' + self.port
        str += self.path
        return str
    
    def get_port(self):
        if self.port == '':
            if self.scheme == 'http':
                self.port = '80'
            elif self.scheme == 'https':
                self.port = '443'
        return int(self.port)