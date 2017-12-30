Fastest of those models is consumer-producer which ahas separate
threads for serving file and counting words in it. For all models
I used collections Counter object. For multi processing the first
model which is PEER-TO-PEER is most suitable because it is most
reducible since it uses separate memory for each process. For file
reading and processing it is faster.

I implemented non-threaded model, first multi-threaded model (P2P),
first multi processed model (P2P) and producer-consumer model.


Running files:

-f "file1 file2" for filename is required (separated by whitespace)
-o "word1 word2" is for occurrences for words (separated by whitespace)
-m showing most common word

filename.py -f "file1.txt file2.txt etc" [-o "word1 word2 wordn"] [-m]