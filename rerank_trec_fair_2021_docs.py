import argparse
import copy
import json
import random
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--corpus', type=str, required=True)
parser.add_argument('--run', type=str, required=True, help='run in {query_id}\t{doc_id} form')
parser.add_argument('--output', type=str, required=True, help='file to store reranked runs')
parser.add_argument('--option', type=int, choices=[1, 2, 3], required=True)
parser.add_argument('--alpha', type=float, required=False)
args = parser.parse_args()

def load_corpus():
    corpus = {}
    with open(args.corpus, 'r') as f:
        for line in tqdm(f):
            line = json.loads(line)
            corpus[int(line['id'])] = line['raw']['geographic_locations']
    return corpus

def load_runs():
    runs = {}
    with open(args.run, 'r') as f:
        prev_query_id = -1
        for line in tqdm(f):
            query_id, doc_id = line.split()
            query_id = int(query_id)
            doc_id = int(doc_id)
            if query_id != prev_query_id:
                prev_query_id = query_id
                runs[query_id] = []
            runs[query_id].append(doc_id)
    return runs

categories = {
    "regions": ["Africa", "Antarctica", "Asia", "Europe", "Latin America and the Caribbean", "Northern America", "Oceania", "None"]
}

def init_fairness_categories():
    fairness_categories = {}
    for category, groups in categories.items():
        fairness_categories[category] = {}
        for group in groups:
            fairness_categories[category][group] = {
                "idx": 0,
                "docs": []
            }
    return fairness_categories

def reorder1(runs):
    reordered_runs = {}
    for query, docs in runs.items():
        reordered_runs[query] = copy.deepcopy(docs)
        random.shuffle(reordered_runs[query])
    return reordered_runs

def populate_fairness_categories(corpus, docs, fairness_categories):
    for doc_id in docs:
        if len(corpus[doc_id]) == 0:
            fairness_categories['regions']['None']['docs'].append(doc_id)
            continue
        for region in corpus[doc_id]:
            fairness_categories['regions'][region]['docs'].append(doc_id)

def reorder2(corpus, runs, fairness_categories):
    reordered_runs = {}
    for query, docs in runs.items():
        reordered_runs[query] = []
        categories_copy = copy.deepcopy(categories)
        fairness_categories_copy = copy.deepcopy(fairness_categories)
        populate_fairness_categories(corpus, docs, fairness_categories_copy)

        region_idx = 0
        while len(categories_copy['regions']) > 0:
            if region_idx >= len(categories_copy['regions']):
                region_idx = 0
            region = categories_copy['regions'][region_idx]
            docs_idx = fairness_categories_copy['regions'][region]['idx']
            region_docs = fairness_categories_copy['regions'][region]['docs']
            while docs_idx < len(region_docs) and region_docs[docs_idx] in reordered_runs[query]:
                docs_idx += 1
            if docs_idx >= len(region_docs):
                categories_copy['regions'].pop(region_idx)
            else:
                reordered_runs[query].append(region_docs[docs_idx])
                fairness_categories_copy['regions'][region]['idx'] = docs_idx + 1 
                region_idx += 1
    return reordered_runs

def reorder3(corpus, initial_runs, fairness_categories, alpha):
    reordered_runs = {}
    if alpha == None:
        alpha = 0.3 
    for query, docs in runs.items():
        run = []
        categories_copy = copy.deepcopy(categories)
        fairness_categories_copy = copy.deepcopy(fairness_categories)
        populate_fairness_categories(corpus, docs, fairness_categories_copy)
        docs_copy = copy.deepcopy(docs)
        
        run_doc_idx = 0
        region_idx = 0
        while run_doc_idx < len(docs_copy):
            if len(categories_copy['regions']) > 0 and random.uniform(0, 1) < alpha: #round robin pick
                if region_idx >= len(categories_copy['regions']):
                    region_idx = 0
                region = categories_copy['regions'][region_idx]
                docs_idx = fairness_categories_copy['regions'][region]['idx']
                region_docs = fairness_categories_copy['regions'][region]['docs']
                while docs_idx < len(region_docs) and region_docs[docs_idx] in run:
                    docs_idx += 1
                if docs_idx >= len(region_docs):
                    categories_copy['regions'].pop(region_idx)
                else:
                    run.append(region_docs[docs_idx])
                    fairness_categories_copy['regions'][region]['idx'] = docs_idx + 1 
                    region_idx += 1
            else: #pick in order
                while run_doc_idx < len(docs_copy) and docs_copy[run_doc_idx] in run:
                    run_doc_idx += 1
                if run_doc_idx >= len(docs_copy):
                    break
                run.append(docs_copy[run_doc_idx])
                run_doc_idx += 1
        reordered_runs[query] = run
    return reordered_runs

def reorder4(corpus, initial_runs, fairness_categories):
    return

def write_runs(runs):
    with open(args.output, 'w') as outf:
        for key, docs in runs.items():
            for doc_id in docs:
                outf.write(str(key) + '\t' + str(doc_id) + '\n') 

fairness_categories = init_fairness_categories()
runs = load_runs()
corpus = load_corpus()
if args.option == 1:
    reranked_runs = reorder1(runs)
elif args.option == 2:
    reranked_runs = reorder2(corpus, runs, fairness_categories)
elif args.option == 3:
    reranked_runs = reorder3(corpus, runs, fairness_categories, args.alpha)
else:
    print("option not supported")
    quit()
write_runs(reranked_runs)

#runs = {0: [0, 1, 2]}
#corpus = {0: [], 1: ['Africa'], 2: ['Africa']}
#reranked_runs = reorder3(corpus, runs, fairness_categories)
#print(reranked_runs)
