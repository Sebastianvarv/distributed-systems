import os


def create_test_file(filename):
    filepath = os.getcwd() + "/" + filename
    with open(filepath, 'w') as f:
        f.write((str(filename) + " ") * 10 ** 5)


create_test_file("testfail_2.txt")
