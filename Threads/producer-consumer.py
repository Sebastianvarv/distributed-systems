import logging
import string
import threading
from argparse import ArgumentParser
from collections import Counter

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )


class Queue:
    def __init__(self):
        self.__q = []
        self.__cv = threading.Condition()

    def put(self, e):
        with self.__cv:
            logging.debug('Added element')
            self.__q.append(e)
            if len(self.__q) == 1:
                # First element added - notify all waiting threads
                logging.debug('Queue is no more empty, notifying all' \
                              'waiting threads')
                self.__cv.notifyAll()

    def get(self):
        e = None
        with self.__cv:
            if len(self.__q) <= 0:
                logging.debug('Queue is empty, waiting ...')
                self.__cv.wait()
            e = self.__q.pop()
        return e


def remove_punct(s):
    table = string.maketrans("", "")
    return s.translate(table, string.punctuation)


def consumer(q, count):
    """wait for the condition and use the resource"""
    logging.debug('Starting consumer thread')
    while True:
        wd = q.get()
        logging.debug('consumed: %s' % wd)
        count[wd] += 1


def producer(q, files):
    """set up the resource to be used by the consumer"""
    logging.debug('Starting producer thread')
    for file in files:
        with open(file) as f:
            for line in f:
                parts = line.split()
                for word in parts:
                    wd = remove_punct(word.strip())
                    q.put(wd)
                    logging.debug('Added: %s' % wd)
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
    cons = threading.Thread(name='Consumer', target=consumer, args=(q, count))
    prod = threading.Thread(name='Producer', target=producer, args=(q, files.split()))

    cons.start()
    prod.start()

    cons.join()
    prod.join()

    print(list(count.elements()))
