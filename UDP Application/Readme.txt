Seminar #1 Sample Application
2016-08-19 Copyright (c) 2016 DSLab

Simple application (Message board) illustrating implementation of
Application Layer protocols on UDP. According to seminar documentation we
have implemented the example application in 2 parts:

Part #1 -----------------------------------------------------------------------

Implements state-less protocol on top of UDP ( MBoard protocol 0.0.0.x )
The source is organized as follows:

part1
└── udp
    └── mboard
        └── stateless
            ├── board.py			# MBoard API implementation
            ├── client.py			# MBorad client (main)
            ├── protocol.py			# MBoard protocol processor (server-side)
            ├── server.py			# MBoard Server (main)
            └── TODO.txt

* MBoard API:
	- publish
	- get
	- last

!!!NB!  EXECUTING the Python code !!!!!!
		# client.py and server.py need PYTHONPATH variable has to be declared
		# make sure you have PYTHONPATH variable set to "part1" directory:
		#
		# Example in Linux and Mac
		# (assuming your current directory is "UDP Application"):
		export PYTHONPATH=$(pwd)/part1

		# Running client or server, calling help message
		python2.7 part1/udp/mboard/stateless/client.py -h
		python2.7 part1/udp/mboard/stateless/server.py -h

		# Example on Windows
		# (assuming your current directory is "UDP Application"):
		set PYTHONPATH=%cd%\part1

		# Running client or server, calling help message
		# assuming Python 2.7 is installed in C:\Python27\
		C:\Python27\python part1\udp\mboard\stateless\client.py -h
		C:\Python27\python part1\udp\mboard\stateless\server.py -h

Part #2 -----------------------------------------------------------------------

1. Implements state-full protocol on top of UDP ( Sessions protocol 0.0.0.x )
2. Re-factors the MBoard protocol to rely on Sessions protocol instead of UDP
The source is organized as follows:

part2
└── udp
    └── mboard
        └── sessions
            ├── board.py			# MBoard API (not changed)
            ├── client
            │   ├── main.py			# Client-side main method
            │   ├── protocol.py		# Client-side MBoard protocol
            │   ├── sessions.py		# Client-side Sessions protocol
            ├── common.py			# Common variables and constants
            ├── server
            │   ├── main.py			# Server-side main method
            │   ├── protocol.py		# Server-side MBoard protocol
            │   ├── sessions.py		# Server-side Sessions protocol
            └── tests
                └── main.py			# Main method running tests


!!!NB!  EXECUTING the Python code !!!!!!
		# PYTHONPATH variable has to be declared
		# make sure you have PYTHONPATH variable set to "part1" directory:
		# Example in Linux/Mac
		# (assuming your current directory is "UDP Application"):
		export PYTHONPATH=$(pwd)/part2

		# Running client or server calling help message
		python2.7 part2/udp/mboard/sessions/client/main.py -h
		python2.7 part2/udp/mboard/sessions/server/main.py -h

		# Example on Windows
		# (assuming your current directory is "UDP Application"):
		set PYTHONPATH=%cd%\part2

		# Running client or server calling help message
		C:\Python27\python part2\udp\mboard\sessions\client\main.py -h
		C:\Python27\python part2\udp\mboard\sessions\server\main.py -h

# Compiled binaries --------------------------------------------------------
Alternatively you may the ready binaries to just test the application
Binaries are located in the bin folder and organized as follows:

TODO: add binaries layout
