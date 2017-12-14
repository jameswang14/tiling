from parse import main
from os import listdir
from os.path import isfile, join
path = "./input/"
for file in listdir(path):
    if isfile(join(path, file)) and file != ".DS_Store":
        _, time_one, __ = main(file, "true", "true", "true")
        solutions, time, num_pieces = main(file, "true", "true", "false")
        length = 0
        if solutions:
            length = len(solutions)
        print(file + " | " + str(length) + " | " + str(time_one) + " | " + str(time))