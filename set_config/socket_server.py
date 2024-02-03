from websocket_server import WebsocketServer

# 新しいクライアントが接続したときの処理
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    server.send_message_to_all("Hey all, a new client has joined us")

# クライアントが切断したときの処理
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])

# クライアントからメッセージを受信したときの処理
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200]+'..'
    print("Client(%d) said: %s" % (client['id'], message))

PORT=5003
server = WebsocketServer(host='localhost', port=PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()

while True:
    str = input("Enter your input: ")
    server.send_message_to_all(str)