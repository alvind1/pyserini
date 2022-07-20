import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input-files', dest='input_files', type=str, nargs='+', required=True)
parser.add_argument('--output-dir', dest='output_dir', type=str, required=True) 
parser.add_argument('--task', type=int, choices=[1, 2], required=True)
args = parser.parse_args()

print(
    f"Preprocessing runs to {args.output_dir} for and Task {args.task}")


def preprocess_for_task1(filename):
    outfile = args.output_dir + '/' + 'eval_format.' + os.path.basename(filename)
    with open(filename, 'r') as f, open(outfile, 'w') as outf:
        lines = f.readlines()
        for line in lines:
            line = line.split()
            outf.write(line[0] + "\t" + line[2] + "\n")


def handle_task1():
    for filename in args.input_files:
        preprocess_for_task1(filename)


def preprocess_for_task2(filename):
    outfile = args.output_dir + '/' + 'eval_format.' + os.path.basename(filename)
    with open(filename, 'r') as f, open(outfile, 'w') as outf:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            rankings = []
            for _ in range(50):
                line = lines[i].split()
                i += 1
                rankings.append([line[0], line[2]])
            for repeat in range(100):
                for ranking in rankings:
                    outf.write(
                        ranking[0] + "\t" + str(repeat+1) + "\t" + ranking[1] + "\n")


def handle_task2():
    for filename in args.input_files:
        preprocess_for_task2(filename)

if args.task == 1:
    handle_task1()
elif args.task == 2:
    handle_task2()
