import argparse
import json
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, required=True, help='input file containing the rel docs of trec fair 2022 documents')
parser.add_argument("--output", type=str, required=True, help='output file containg the rel docs in qrels format')
args = parser.parse_args()

with open(args.input, 'r') as f, open(args.output, 'w') as outf:
    for line in tqdm(f):
        query = json.loads(line)
        rel_docs = set()
        for q in query['rel_docs']:
            rel_docs.add(q)
        for doc_id in rel_docs:
            output = str(query['id']) + " 0 " + str(doc_id) + " 1"
            outf.write(output + '\n')
