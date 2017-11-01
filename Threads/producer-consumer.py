import logging
import string
import threading
from argparse import ArgumentParser
from collections import Counter


class Queue:
    def __init__(self):
        self.__q = []
        self.__cv = threading.Condition()

    def put(self, e):
        with self.__cv:
            self.__q.append(e)
            if len(self.__q) == 1:
                # First element added - notify all waiting threads
                self.__cv.notifyAll()

    def get(self):
        e = None
        with self.__cv:
            if len(self.__q) <= 0:
                self.__cv.wait()
            e = self.__q.pop()
        return e


def remove_punct(s):
    table = string.maketrans("", "")
    return s.translate(table, string.punctuation)


def consumer(q, count, files):
    """wait for the condition and use the resource"""

    for i in range(len(files)):
        words = q.get()
        for wd in words:
            count[wd] += 1


def producer(q, files):
    """set up the resource to be used by the consumer"""
    for file in files:
        with open(file) as f:
            words = []
            for line in f:
                parts = line.split()
                for word in parts:
                    words.append(remove_punct(word.strip()))
            q.put(words)
                    # time.sleep(1)


if __name__ == '__main__':
    parser = ArgumentParser(description="Homework 3 Multi threaded program")
    parser.add_argument('-o', '--occurrences', help='Count occurrences of the specified words', required=False)
    parser.add_argument('-m', '--mostfrequent', help='Calculate most frequent word', required=False,
                        action='store_true')
    parser.add_argument('-f', '--files', help='Files', required=True)

    args = parser.parse_args()
    occurrences = args.occurrences
    most_frequent = args.mostfrequent
    files = args.files
    count = Counter()

    q = Queue()
    files_list = files.split()
    cons = threading.Thread(name='Consumer', target=consumer, args=(q, count, files_list))
    prod = threading.Thread(name='Producer', target=producer, args=(q, files_list))

    cons.start()
    prod.start()

    cons.join()
    prod.join()