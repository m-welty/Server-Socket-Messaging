import socket
import threading
import time


class Server:

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", 12345))
        self.server_socket.listen(5)
        self.subscribers = {'WEATHER': [], 'NEWS': []}
        self.messages = {'WEATHER': [], 'NEWS': []}
        self.offline_subscribers = {}
        self.offline_queue = []
        print("[INFO] Server listening on port 12345.\n")

    def clean_queue(self):
        clean_time = time.time()
        self.offline_queue = [(client, topic, message, timestamp) for client, topic, message, timestamp in self.offline_queue if clean_time - timestamp < 30]

    def handle_client(self, client_socket, client_address):
        print(f"[INFO] Connected to {client_address}\n")

        try:
            client_socket.send(b"CONN_ACK\n")
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                print(f"[MESSAGE from {client_address}]: {message}\n")
                client_socket.sendall(
                    f"Server received: {message}\n".encode('utf-8'))
                message_split = message.split(", ")
                client_name = message_split[0].upper()
                action = message_split[1].upper()

                if action == 'DISC':
                    if client_name not in self.offline_subscribers:
                        self.offline_subscribers[client_name] = []
                    for topic, clients in list(self.subscribers.items()):
                        if client_socket in clients:
                            self.offline_subscribers[client_name].append(topic)
                            clients.remove(client_socket)
                    client_socket.send(b"<DISC_ACK>\n")
                    break

                elif action == 'RECON':
                    if client_name in self.offline_subscribers:
                        client_socket.send(b"<CONN_ACK>")
                        self.clean_queue()
                        subscriptions = self.offline_subscribers[client_name]
                        for topic in subscriptions:
                            if topic in self.subscribers:
                                self.subscribers[topic].append(client_socket)
                        for item in self.offline_queue:
                            if len(item) !=4:
                                continue
                            offline_client, topic, content, timestamp = item
                            if (offline_client == client_name and topic in subscriptions):
                                try:
                                    client_socket.send(f"Subject: {topic}, Message: {content}\n".encode('utf-8'))
                                    time.sleep(1)
                                except Exception as e:
                                    print(f"Error sending message: {e}")
                        self.offline_queue = [item for item in self.offline_queue if item[0] != client_name]
                        self.offline_subscribers.pop(client_name)

                                

                subject = message_split[2].upper()

                if action == 'SUB':
                    if subject not in self.subscribers:
                        client_socket.send(
                            f"<ERROR: Subscription Failed - Subject Not Found>"
                            .encode('utf-8'))
                        print(
                                "<ERROR: Subscription Failed - Subject Not Found>\n"
                            )
                    else:
                        self.subscribers[subject].append(client_socket)
                        client_socket.send(b"SUB_ACK\n")
                        for text in self.messages[subject]:
                            client_socket.send(
                                f"Subject: {subject}, Message: {text}".encode(
                                    'utf-8'))

                elif action == 'PUB':
                    content = message_split[3]
                    if subject not in self.messages:
                        client_socket.send(
                            f"<ERROR: Publishing Failed - Subject Not Found>".
                            encode('utf-8'))
                        print(
                            "<ERROR: Publishing Failed - Subject Not Found>\n")
                    else:
                        self.messages[subject].append(content)
                        for subscriber in self.subscribers[subject]:
                            subscriber.send(
                                f"Subject: {subject}, Message: {content}\n".
                                encode('utf-8'))
                        for offline_client, topics in self.offline_subscribers.items():
                            if subject in topics:
                                self.offline_queue.append((offline_client, subject, content, time.time()))

                else:
                    client_socket.send(b"<ERROR: Unknown action>")
                    print("<ERROR: Unknown Action>\n")

        except Exception as e:
            print(f"<ERROR: {e}\n>")

        finally:
            client_socket.close()
            print(f"[INFO] Connection closed {client_address}\n")

    def server_start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client,
                                             args=(client_socket,
                                                   client_address))
            client_thread.start()


class Client:

    def __init__(self, action, id, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        if action.lower() == 'p':
            self.client_name = "Publisher " + id
        else:
            self.client_name = "Subscriber " + id

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        print(f"[{self.client_name}] Server Response: {response}\n")
        return response

    def publish(self, subject, content):
        self.send_message(f"{self.client_name}, PUB, {subject}, {content}")

    def subscribe(self, subject):
        self.send_message(f"{self.client_name}, SUB, {subject}")

    def disconnect(self):
        self.send_message(f"{self.client_name}, DISC")

    def reconnect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.send_message(f"{self.client_name}, RECON")


def test_sequence():
    print('\n\n\n[TEST] Step 1: Server Initialization\n')
    time.sleep(1)
    test_server = Server()
    time.sleep(1)
    server_thread = threading.Thread(target=test_server.server_start)
    time.sleep(1)
    server_thread.start()
    time.sleep(5)

    print('\n\n\n[TEST] Step 2: Publisher Connection\n')
    time.sleep(1)
    publisher1 = Client('p', '1')
    time.sleep(1)
    publisher2 = Client('p', '2')
    time.sleep(1)
    publisher1.publish('WEATHER', 'It is sunny today')
    time.sleep(1)
    publisher2.publish('NEWS', 'Breaking News!')
    time.sleep(1)
    publisher1.publish('WEATHER', 'It is going to rain tomorrow')
    time.sleep(5)

    print(
            '\n\n\n[TEST] Step 3: Subscriber Connects and Subscribes to Subjects\n')
    time.sleep(1)
    subscriber1 = Client('s', '1')
    time.sleep(1)
    subscriber1.subscribe('NEWS')
    time.sleep(1)
    subscriber2 = Client('s', '2')
    time.sleep(1)
    subscriber2.subscribe('WEATHER')
    time.sleep(1)
    subscriber3 = Client('s', '3')
    time.sleep(1)
    subscriber3.subscribe('NEWS')
    time.sleep(1)
    subscriber3.subscribe('WEATHER')
    time.sleep(5)

    print(
            '\n\n\n[TEST] Step 4: Publishers Continue Sending Real-Time Messages\n')
    time.sleep(1)
    publisher1.publish('WEATHER', 'Heavy rain is expected tomorrow')
    time.sleep(1)
    publisher2.publish('NEWS', 'Election results are out!')
    time.sleep(5)

    print(
            '\n\n\n[TEST] Error Handling 1: Subscribing to a Non-Existent Subject\n')
    time.sleep(1)
    subscriber1.subscribe("SPORTS")
    time.sleep(5)

    print(
            '\n\n\n[TEST] Error Handling 2: Publisher Publishes to a Non-Existent Subject\n'
        )
    time.sleep(1)
    publisher1.publish("SPORTS", "Football match update")
    time.sleep(10)

    print('\n\n\n[TEST] Step 5: Subscribers Disconect\n')
    time.sleep(1)
    subscriber1.disconnect()
    time.sleep(2)
    subscriber2.disconnect()
    time.sleep(2)
    subscriber3.disconnect()
    time.sleep(5)

    print(
            '\n\n\n[TEST] Step 6: Subscriber Reconnects and Receives Missed Messages'
        )
    time.sleep(1)
    publisher1.publish(
        'WEATHER',
        "This message should time out and will not be sent to the reconnecting subscriber"
    )
    time.sleep(35)
    publisher1.publish('WEATHER', "Temperature will be normal tomorrow")
    time.sleep(1)
    publisher2.publish('NEWS', "This is more news")
    time.sleep(1)
    subscriber1.reconnect()
    time.sleep(1)
    subscriber2.reconnect()
    time.sleep(5)

    print('\n\n\n[TEST] Step 7: Clients Disconnect\n')
    time.sleep(1)
    subscriber1.disconnect()
    time.sleep(2)
    subscriber3.disconnect()
    time.sleep(2)
    publisher1.disconnect()
    time.sleep(2)
    publisher2.disconnect()


run_test = input("Run Test Sequence? [Y/N]\nIt will take about 3 minutes.\n")
if run_test.lower() == 'y':
    test_sequence()
else:
    print("Test sequence aborted.")
