Simple chat service with server and client. Server sends broadcast messages with pyro uri to
connect with clients. Clients will connect to the server using this uri and will be registered to the server
afterwards.

Client application takes username as argument. All instructions how to use the chat client are
printed on top of the console. This application uses pyro implementation of the chat application which
was provided in the practise session. Only difference is leaving the server and sending private messages.
private messages can be sent using keyword -p [username-to] [message], and all users can be listed using -l.