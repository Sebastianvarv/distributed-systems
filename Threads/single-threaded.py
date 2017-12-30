from argparse import ArgumentParser
from collections import Counter

from common import read_file, count_words

if __name__ == '__main__':
    parser = ArgumentParser(description="Homework 3 Single threaded program")

    parser.add_argument('-o', '--occurrences', help='Count occurrences of the specified words', required=False)
    parser.add_argument('-m', '--mostfrequent', help='Calculate most frequent word', required=False,
                        action='store_true')
    parser.add_argument('-f', '--files', help='Files', required=True)

    args = parser.parse_args()
    occurrences = args.occurrences
    most_frequent = args.mostfrequent
    files = args.files

    # Count word occurences
    counts = Counter()
    for filename in files.split():
        count_words(read_file(filename), counts)

    if occurrences:
        for word in occurrences.split():
            print word, counts[word]

    elif most_frequent:
        print counts.most_common(1)[0][0]
