Seminar #2 Sample Application
2016-09-13 Copyright (c) 2016 DSLab

Simple application (Message board) illustrating implementation of
Application Layer protocols on TCP. According to seminar documentation we
have implemented the example application in 1 part:

Part #1 -----------------------------------------------------------------------

Implements state-less protocol on top of TCP ( MBoard protocol 0.1.0.x )
The source is organized as follows:

part1/
├── mboard_client.py	# Main method, PYTHONPATH setup, arguments processing
├── mboard_server.py	# Main method, PYTHONPATH setup, arguments processing
└── tcp
    └── mboard
        └── sessions
            ├── board.py	# Mboard API implementation
            ├── client
            │   ├── main.py	# Client-client side application start
            │   └── protocol.py	# Client-side MBoard protocol
            ├── common.py	# Common variables (constants and methods)
            └── server
                ├── main.py	# Server-side application start
                └── protocol.py	# Server-side MBoard protocol

* MBoard API:
	- publish M
	- get last N messages

!!!NB!  EXECUTING the Python code !!!!!!
		# mboard_client.py and mboard_server.py contain 
		#	the main methods for MBoard client and server
		# PYTHONPATH variable is NOT needed this time ;)
		# 
		# The starter scripts mboard_client.py and mboard_server.py
		# 	take of setting up PYTHONPATH)

		# On all platforms, using command line and
		# assuming your current directory
		# assuming <python> is Python2.7 interpretor, for example:
		# 	* C:\Python27\python in Windows
		# 	* python2.7 in Linux/Mac
		# is "TCP Application\part1":
		# running client or server, calling help message
		<python> mboard_client.py -h
		<python> mboard_server.py -h



# Compiled binaries --------------------------------------------------------
No binaries shared this time. 
Please make sure you can run the code ursing Python 2.7 interpretor
