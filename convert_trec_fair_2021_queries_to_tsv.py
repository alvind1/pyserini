import argparse
import json
from pathlib import Path
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
args = parser.parse_args()

print("loading topics...")

with open(args.input, 'r') as f, open(args.output, 'w') as outf:
    for line in tqdm(f):
        query = json.loads(line)
        output = str(query['id']) + "\t" + query['title'] + " " + " ".join(query['keywords'])
        outf.write(output + "\n")
