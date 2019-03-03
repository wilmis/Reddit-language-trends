import pickle
import json
import argparse
import numpy as np

from language_analyser import Corpus

parser = argparse.ArgumentParser(description='Convert previously used pickle corpuses to json')
parser.add_argument('files', metavar='s', type=str, nargs='*', help='which files to convert')

args = parser.parse_args()

def decoder(obj):
    if isinstance(obj, np.float32):
        return float(obj)
    
    return obj.__dict__

for filepath in args.files:
    print("Reading:", filepath)
    corpus_file = open(filepath, mode='rb')
    corpus = pickle.load(corpus_file)
    corpus_file.close()
    
    # assuming .pickle file ending
    filepath = filepath[:-7]+".json"
    print("Saving to:", filepath)
    corpus_file = open(filepath, mode='w')
    json.dump(corpus.__dict__, corpus_file, default=decoder)
    corpus_file.close()
    