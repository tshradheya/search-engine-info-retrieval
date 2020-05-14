#!/usr/bin/python3
import re
from collections import defaultdict

import nltk
import sys
import getopt
import os
import pickle

from dictionary import Dictionary
from postingsfile import PostingsFile
import util


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    indexing_doc_files = sorted(map(int, os.listdir(in_dir)))

    dictionary = Dictionary(out_dict)
    postings = PostingsFile(out_postings)

    temp_dictionary = defaultdict(lambda: defaultdict(int))

    # For each document get the terms and add it into the temporary in-memory posting lists
    for document in indexing_doc_files:
        terms = util.read_document(in_dir, document)
        tf_for_doc = defaultdict(int)

        for term in terms:
            tf_for_doc[term] += 1
            temp_dictionary[term][document] += 1

        # Maintain normalised length and count in dictionary.txt
        dictionary.add_normalised_doc_length(document, tf_for_doc)
        dictionary.add_doc_count()

    # Format posting to store in posting list
    postings.format_posting(temp_dictionary)

    # Save dictionary and posting list with offsets tracking
    postings.save(dictionary)
    dictionary.save()


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
