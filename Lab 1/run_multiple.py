import sys
import os
import subprocess

def main():
    #Check users inputs
    if len(sys.argv) != 3:
        print("Please enter 2 arugments in the form <directorypath> <part>.")
        print("Part options are part2 or part1.")
        return
    directory = sys.argv[1]
    part = sys.argv[2].lower()
    algos = ["bfs", "ids", "h1", "h2", "h3"]
    files = os.listdir(directory)
    files.sort()

    if part == "part2":
        results = open("part2.txt", "w")
        for algo in algos:
            results.write("Algorithm: " + algo + "\n")
            results.write("---------------\n")
            for file in files:
                file_path = directory + "/" + file
                results.write(file + ":\n")
                output = subprocess.run(["python3", "lab1.py", file_path, algo], capture_output=True, text=True)
                results.write(output.stdout + "\n")
        results.close()
    elif part == "part3":
        depths = ["L8", "L15", "L24"]
        results = open("part3.txt", "w")
        for algo in algos:
            results.write("Algorithm: " + algo + "\n")
            results.write("---------------\n")
            for depth in depths:
                results.write(depth + ":\n")
                files = os.listdir(directory + "/" + depth + "/")
                total_time = 0
                total_nodes = 0
                for file in files:
                    print(algo, "at depth:", depth, "and file:", file)
                    file_path = directory + "/" + depth + "/" + file
                    output = subprocess.run(["python3", "lab1.py", file_path, algo, "part3"], capture_output=True, text=True)
                    data = output.stdout.split("\n")
                    total_time += float(data[0])
                    total_nodes += int(data[1])
                avg_time = total_time / len(files)
                avg_nodes = total_nodes / len(files)
                results.write("Average time: " + str(avg_time) + "\n")
                results.write("Average nodes: " + str(avg_nodes) + "\n\n")
        results.close()
    else:
        print("Invalid part")
main()