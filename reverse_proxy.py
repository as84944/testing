# reverse_proxy.py

from http.server import BaseHTTPRequestHandler, HTTPServer
import http.client

# Define the host and port of the target server (Apache Atlas running locally)
TARGET_HOST = 'localhost'
TARGET_PORT = 21000

class ReverseProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def proxy_request(self):
        # Set up a connection to the target server
        target_conn = http.client.HTTPConnection(TARGET_HOST, TARGET_PORT)
        target_path = self.path

        # Forward the request headers and body (if any)
        target_conn.request(self.command, target_path, self.headers, self.rfile)
        
        # Get the response from the target server
        target_response = target_conn.getresponse()

        # Send the target server's response back to the client
        self.send_response(target_response.status)
        for header, value in target_response.getheaders():
            self.send_header(header, value)
        self.end_headers()
        
        # Send the response body in chunks to the client
        chunk = target_response.read(8192)
        while chunk:
            self.wfile.write(chunk)
            chunk = target_response.read(8192)

        # Close the connection to the target server
        target_conn.close()

if __name__ == '__main__':
    # Set up the reverse proxy server
    proxy_server_address = ('', 8000)  # Replace with your desired port
    reverse_proxy = HTTPServer(proxy_server_address, ReverseProxyHandler)

    print(f'Starting reverse proxy server on port {proxy_server_address[1]}...')
    try:
        reverse_proxy.serve_forever()
    except KeyboardInterrupt:
        pass

    reverse_proxy.server_close()
    print('Reverse proxy server stopped.')
