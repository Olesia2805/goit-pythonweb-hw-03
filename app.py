import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import datetime
import requests
import json

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        try:
            if pr_url.path == '/':
                self.send_html_file('index.html')
            elif pr_url.path == '/message':
                self.send_html_file('message.html')
            else:
                if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                    self.send_static()
                else:
                    self.send_html_file('error.html', 404)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())

    def send_html_file(self, filename, status=200):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} not found.")
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(post_data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

        storage_path = pathlib.Path('storage/data.json')
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        if storage_path.exists():
            with open(storage_path, 'r') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data[timestamp] = data_dict

        print(data)

        with open(storage_path, 'w') as file:
            json.dump(data, file, indent=4)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('0.0.0.0', 3000)
    http = server_class(server_address, handler_class)
    print("Server running on http://localhost:3000")
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        http.server_close()

if __name__ == '__main__':
    print("Starting server...")
    run()
