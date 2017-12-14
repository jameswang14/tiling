from parse import main
from os import listdir
from os.path import isfile, join
path = "./input/"
out_path = "./solutions/"
for file in listdir(path):
    if isfile(join(path, file)) and file != ".DS_Store":
        outfile = open(join(out_path,file[:file.index('.')]+"_output.txt"), 'w')
        solutions, time_one, __ = main(file, "true", "true", "false")
        if solutions and len(solutions) > 0:
            for s in solutions:
                for line in s:
                    outfile.write(str(line))
                outfile.write("\n")
                


        