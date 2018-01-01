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


def count_words(word_list, counter):
    for word in word_list:
        counter[word] += 1
