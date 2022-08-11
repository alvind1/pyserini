import argparse
import json
import numpy as np
from tqdm import tqdm

# from https://tech.hbc.com/2018-03-23-negative-sampling-in-numpy.html
def negsamp_vectorized_bsearch(pos_inds, n_items, n_samp):
    """ Pre-verified with binary search
    `pos_inds` is assumed to be ordered
    """
    raw_samp = np.random.choice(np.arange(n_items - len(pos_inds)), size=n_samp, replace=False)
    raw_samp.sort()
    pos_inds_adj = pos_inds - np.arange(len(pos_inds))
    ss = np.searchsorted(pos_inds_adj, raw_samp, side='right')
    neg_inds = raw_samp + ss
    return set(neg_inds)

def sample_from_run(positives, run):
    idx = np.searchsorted(positives, len(run))

def load_run(path):
    run = {}
    with open(path, 'r') as frun:
        for line in tqdm(frun):
            query_id, _, doc_id, _, _, _ = line.split()
            query_id = int(query_id)
            doc_id = int(doc_id.rstrip('\n'))
            if query_id not in run:
                run[query_id] = []
            run[query_id].append(doc_id)
    return run

def load_doc_ids(path):
    docIDs = []
    with open(path, 'r') as f:
        docIDs = json.loads(f.readline())
        assert type(docIDs) == list
        assert len(docIDs) == trec_2021_fair_num_docs
    return docIDs

def get_pos_inds(doc_ids, rel_docs):
    rel_docs.sort()
    pos_inds = np.searchsorted(doc_ids, rel_docs)
    return pos_inds

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True, help='input file containing the rel docs of trec fair 2022 documents')
parser.add_argument('--output', type=str, required=True, help='output file containg the rel docs in qrels format')
parser.add_argument('--run', type=str, default="", required=False, help='path to BM25 run file from which to sample negative examples')
parser.add_argument('--docIDs', type=str, default="", required=False, help='path to docIDs file, used to generate negative examples')
parser.add_argument('--random-negative-samples', action='store_true', default=False, help='add randomly sampled negative examples from the corpus')
parser.add_argument('--run-negative-samples', action='store_true', default=False, help='add sampled negative examples from run')
args = parser.parse_args()

trec_2021_fair_num_docs = 6280328
max_positives = 564158

run = []
doc_ids = []
if args.random_negative_samples:
    assert args.docIDs != ""
    doc_ids = load_doc_ids(args.docIDs)

if args.run_negative_samples:
    assert args.run != ""
    run = load_run(args.run)
    assert args.docIDs != ""
    doc_ids = load_doc_ids(args.docIDs)

with open(args.input, 'r') as f, open(args.output, 'w') as outf:
    for line in tqdm(f):
        query = json.loads(line)
        rel_docs = set()
        for doc_id in query['rel_docs']:
            if doc_id not in rel_docs:
                output = str(query['id']) + " 0 " + str(doc_id) + " 1"
                outf.write(output + '\n')
                rel_docs.add(doc_id)

        if args.random_negative_samples:
            pos_inds = get_pos_inds(doc_ids, list(rel_docs))
            neg_inds = negsamp_vectorized_bsearch(pos_inds, trec_2021_fair_num_docs, len(rel_docs))
            assert len(neg_inds) == len(rel_docs)
            neg_elements = [doc_ids[i] for i in neg_inds]
            for doc_id in neg_elements:
                output = str(query['id']) + " 0 " + str(doc_id) + " 0"
                outf.write(output + '\n')
                assert doc_id not in rel_docs