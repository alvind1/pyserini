import argparse
import json
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True)
parser.add_argument('--output', type=str, required=True)

args = parser.parse_args()

with open(args.input, 'r') as f, open(args.output, 'w') as outf:
    docIDs = set()
    for line in tqdm(f):
        line = json.loads(line)
        docIDs.add(int(line['id']))
    docIDList = list(docIDs)
    docIDList.sort()
    print(len(docIDList))
    json.dump(docIDList, outf)
