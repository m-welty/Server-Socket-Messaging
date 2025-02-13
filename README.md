# Server-Socket-Messaging
Code that establishes a server with publishers and subscribers to simulate MQTT.

Running the Test Sequence: \
Run the .py file. \
A prompt will appear in the Terminal asking if the user wants to run the test. \
Y/y - Test will run. \
N/n - Test will not run.

Imports: socket, threading, and time.

Server Class - Initialization \
Args: None. \
Initializes with a socket. \
Binds the socket to 0.0.0.0 on port 12345. \
Waits for incoming connections. \
Has a dictionary of subscribers linked to the two subjects. \
Has a dictionary of messages linked to the two subjects. \
Has a dictionary of offline subscribers. \
Has an array of the offline message queue, which will store tuples of (client, topic, message, timestamp). \
After initializing, it will print a statement about the server being ready.

Server Class - Clean Queue \
Args: None. \
Will clean the offline_queue dictionary by removing tuples with a timestamp that is older than 30 seconds.

Server Class - Client Handling \
Args: client_socket and client_address. \
Sends CONN_ACK to the client. \
Receives message from the client. \
Confirms by sending message back to the client. \
If the message received is 'DISC', send DISC_ACK to client. \
If the message received is 'RECON':
- Respond with CON_ACK.
- Perform the clean queue function.
- Obtain subscriptions of the reconnecting client from the subscribers dictionary.
- Resubscribes the client to the past subscriptions.
- Runs through the offline_queue. If the client address and subscription match, it will send all missing messages to the client.
- Cleans the offline_queue by removing all messages relating to the reconnecting client.
- Removes the client from the offline subscribers dictionary.

If the message received is 'SUB':
- Add client to dictionary of subscribers of a subject if not already there.
- Send SUB_ACK to the client.
- Sends any already published messages to the new subscriber.
If the message received is 'PUB':
- Put the message content into the dictionary for the subject.
- Send the message content to all current subscribers of the subject.
- If an offline client was subscribed to the topic, save the (client, topic, message, timestamp) as a tuple in the offline message queue.

After breaking from the loop via 'DISC', the client socket will close.

Server Class - Start \
Args: None. \
Starts the server in an infinite loop. \
Allows for threads to be created for all new clients.

Client Class - Initialization \
Args: action, id, host, port. \
Action: 'p' to define client as a publisher or 's' to define as a subscriber. \
ID: Any number as a string (i.e. '1', '2', '999') used to distinguish clients of the same action. \
Host: Default set to 127.0.0.1 \
Port: Same as server, 12345. \
Client name is initialized as the spelled out action of the client and the client ID (i.e. Subscriber 1).

Client Class - Send Message \
Args: Message. \
Message: String to be sent to the server. \
Sends the message to the server. \
Receives a response from the server. \
Returns the response.

Client Class - Publish \
Args: subject, content. \
Subject: The subject the published message will be sent to, either 'NEWS' or 'WEATHER'. \
Content: The string to be published. \
Uses send_message to send a message to the server, consisting of the client name, the 'PUB' action, the subject, and the content.

Client Class - Subscribe \
Args: subject. \
Subject: The subject the client will subscribe to, either 'NEWS' or 'WEATHER'. \
Uses send_message to send a message to the server, consisting of the client name, the 'SUB' action, and the subject.

Client Class - Disconnect \
Uses send_message to initiate disconnecting the client from the server.

Client Class - Reconnect \
Uses send_message to initiate reconnecting the client to the server.

Test Sequence - Step 1 \
Initializes the server and allows for new threads to be created for clients.

Test Sequence - Step 2 \
Publishers connect to the server. \
Publishers send messages which will be stored.

Test Sequence - Step 3 \
Clients subscribe to subjects. \
Clients will received the previously published and now stored messages.

Test Sequence - Step 4 \
Publishers will continue to send messages. \
Clients will receive the new messages.

Error Handling - Part 1 \
Subscriber attempts to subscribe to an unlisted subject. \
Error message is generated.

Error Handling - Part 2 \
Publisher attempts to publish to an unlisted subject. \
Error message is generated.

Test Sequence - Step 5 \
All subscribers disconnect from the server.

Test Sequence - Step 6 \
Publisher will send message, which ultimately should not be received by reconnecting clients as it will be older than 30 seconds. \
Publisher will send another message, which should be received by reconnecting clients. \
Subscribers reconnect and receive recent messages.

Test Sequence - Step 7 \
All clients disconnect.

Error Handling \
Error if a subscriber tries to subscribe to a subject other than 'NEWS' and 'WEATHER'. \
Error if a publisher tries to publish to a subject other than 'NEWS' and 'WEATHER'. \
Error if the action is not 'DISC', 'SUB', or 'PUB'. \
Error for exceptions when trying to establish connection with a client.
