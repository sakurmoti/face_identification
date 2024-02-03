from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# サーバーの設定
host = 'localhost'
port = 8080

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200, 'OK')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(b'Hello, World!')
    
    def do_POST(self):
        print("POST called")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        # print(post_data)
        json_data = json.loads(post_data)
        print(type(post_data))
        print(json_data["name"])

        path = '../face_recognition/dataset'
        path = path + '/' + json_data["name"] + '.json'
        
        f = open(path, 'w')
        json.dump(json_data, f, indent=4)
        f.close()

        self._set_headers()
        response = "data received!"
        self.wfile.write(response.encode('utf-8'))

        

# サーバーの起動
if __name__ == '__main__':
    server_address = (host, port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Starting server on http://{host}:{port}')
    httpd.serve_forever()
