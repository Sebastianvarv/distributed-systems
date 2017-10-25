from argparse import ArgumentParser
from collections import Counter
import string


def remove_punct(s):
    table = string.maketrans("", "")
    return s.translate(table, string.punctuation)


def read_file(file):
    words = []
    with open(file) as f:
        for line in f:
            parts = line.split()
            for word in parts:
                words.append(remove_punct(word.strip()))
    return words


def count_words(word_list):
    count = Counter()
    for word in word_list:
        count[word] += 1
    return count


if __name__ == '__main__':
    parser = ArgumentParser(description="Homework 3 Single threaded program")

    parser.add_argument('-o', '--occurrences', help='Count occurrences of the specified words', required=False)
    parser.add_argument('-m', '--mostfrequent', help='Calculate most frequent word', required=False,
                        action='store_true')
    parser.add_argument('-f', '--files', help='Files', required=True)

    args = parser.parse_args()
    occurrences = args.occurrences
    mostfrequent = args.mostfrequent
    files = args.files

    # Count word occurences
    counts = Counter()
    for filename in files.split():
        counts += count_words(read_file(filename))
    if occurrences:
        for word in occurrences.split():
            print word, counts[word]
    elif mostfrequent:
        print counts.most_common(1)[0][0]
