This is a simple chat application using RabbitMq. This application is using manual polling in order to fetch new messages.
Opening a client application gives various possibilities for example creating a private message room, for this write
-p [room name] [users separated by comma]. Only the selected or invited users see this chat room using -r in the lobby.
For entering a chat room keyword -j [room name] can be used, keyword "exit()" is for returning the lobby. Chat room will
be deleted if all uusers leave the room. in order to load new messages in the chat room without writing one just press
enter without writing any text. Use ctrl + c to leave the client application. Username sing command line parameter -u is
required when starting a client application, username is unique.