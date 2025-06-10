import socket
import ssl

#Class for defining a socket
class Socket:
    def __init__(self, url):
        self.url = url
        #The default socket has:
        self.socket = socket.socket(
            family=socket.AF_INET, #Is a socket to the web
            type=socket.SOCK_STREAM, #Is a stream of unset size
            proto=socket.IPPROTO_TCP #Uses the TCP protocol
        )
        self.headers = {} #Dictionary of request headers
        self.fill_headers()

    #Method for setting up headers
    def fill_headers(self):
        self.headers['Host'] = self.url.host
        self.headers['Connection'] = 'close'

    #Connects the program to a distant device
    def connect(self):
        self.socket.connect((self.url.host, self.url.get_port()))
        if self.url.scheme == 'https':
            ctx = ssl.create_default_context() #Manages the SSL protocol for HTTPS requests
            self.socket = ctx.wrap_socket(self.socket, server_hostname=self.url.host)

    #Handles the request
    def request(self):
        request = 'GET {} HTTP/1.1\r\n'.format(self.url.path)
        for key, val in self.headers.items():
            request += '{}: {}\r\n'.format(key, val)
        request += '\r\n'
        self.socket.send(request.encode('utf8'))

    #Manages the response of the server
    def response(self):
        response = self.socket.makefile('r', encoding='utf8', newline='\r\n') #The recieved content gets cached
        #This reads from the response header
        statusline = response.readline()
        version, status, explanation = statusline.split(' ', 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line == '\r\n': break #Read while there is an empty line
            header, value = line.split(':', 1)
            response_headers[header.casefold()] = value.strip()

        assert 'transfer-encoding' not in response_headers
        assert 'content-encoding' not in response_headers

        content = response.read() #Loads the HTML code
        self.socket.close() #Closes the socket
        
        return content #Return the HTML code
    
    #Logic used to link the networking with the GUI
    def load_content(self):
        text = ''
        #Future support to render files
        if self.url.scheme != 'file':
            self.connect() #Connect to source
            self.request() #Send the request
            text = self.response() #Get the HTML code
        else:
            text = '2'
        return text #Return HTML

#Class to operate on the URL
class URL:
    def __init__(self, url):
        #Find the protocol used for searching
        self.scheme, url = url.split('://', 2)
        assert self.scheme in ['http', 'https', 'file']
        
        #Add / at the end of the URL for consisntency
        if '/' not in url:
            url += '/'
        self.host, url =  url.split('/', 1)

        #Find the port of the address
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
    
    #Get the port of the address
    def get_port(self):
        #If the port isn't se manual, get it based on the URL scheme
        if self.port == '':
            if self.scheme == 'http':
                self.port = '80'
            elif self.scheme == 'https':
                self.port = '443'
        return int(self.port)