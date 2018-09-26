from http.server import BaseHTTPRequestHandler, HTTPServer

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith('/hello'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ''
            message += '<html><body>Hello!</body></html>'
            self.wfile.write(message.encode())
            print(message)
            return
        if self.path.endswith('/hola'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = '''
                <!DOCTYPE html>
                <html>
                    <body>
                        &#161Hola
                        <a href="/hello">Back to Hello</a>
                    </body>
                </html>
            '''
            self.wfile.write(message.encode())
            print(message)
            return
        else:
            self.send_error(404, 'File not found: %s' % self.path)

def main():
    try:
        port = 8000
        server_address = ('', port)
        server = HTTPServer(server_address, WebServerHandler)
        print('Web server running on port %s' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C entered, stopping web server')
        server.socket.close()

if __name__ == '__main__':
    main()