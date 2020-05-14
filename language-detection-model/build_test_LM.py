#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import log10
import re
import sys
import getopt
# import nltk

# Configurations #
NGRAM_MODEL_SIZE = 4  # Ngram size for character-based ngrams
SUPPORT_OTHER_LANGUAGE = False  # Flag whether to support showing "other" in language when predicting
OTHER_THRESHOLD = 0.8  # missing counts/total number of ngrams threshold
PADDING = True  # Whether to pad start/end of line when building and testing
REMOVE_NUMBERS = True  # Whether to remove numbers from line when building and testing
REMOVE_PUNCTUATIONS = False  # Whether to remove all punctuations from the sentence
##################

START_PAD = '<'
END_PAD = '>'

def pre_process_line(line):
    """
    This function prepossesses a line based on configurations for heuristics in order to obtain better results
    :param line: data line of a particular language either used for training or testing
    :return: temp: formatted input string based on configurations
    """
    temp = line.strip().strip(".").lower()  # Remove empty space, convert to lowercase and remove period from end

    if REMOVE_PUNCTUATIONS:
        temp = re.sub(r'[^\w\s]', '', temp)
    if REMOVE_NUMBERS:
        temp = re.sub('[0-9]', '', temp)
    if PADDING:
        temp = START_PAD + temp + END_PAD

    return temp

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    :param in_file: name of input file which contains training data
    :return language_model: a dictionary of dictionaries containing count of n-gram
                for all languages with AddOne smoothing
    :return total_count: vocabulary count for each language found in training data
    """
    print('building language models...')

    language_model = {}  # E.g. { 'tamil': {('a', 'b', 'c', 'd'): 5} }
    total_count = {}  # E.g. {'tamil': 42819 }

    input_file = open(in_file, 'r')

    # First we build the dictionary DS for all languages found in training and keep the data structure dynamic
    for observation in input_file:
        language = observation.split(" ")[0]
        if language not in language_model:
            language_model[language] = {}
            total_count[language] = 0
    input_file.close()

    # Go through all training data and add the character based 4-gram in Language Model with AddOne Smoothing
    # Also keeps track of vocabulary count for each language model
    input_file = open(in_file, 'r')
    for observation in input_file:
        language = observation.split(" ")[0]
        data_lang = pre_process_line(observation.split(" ", 1)[1])

        ngrams = []
        for i in range(len(data_lang) - NGRAM_MODEL_SIZE + 1):
            ngrams.append(tuple(data_lang[i: i + NGRAM_MODEL_SIZE]))

        for ngram in ngrams:
            for lang in language_model:
                if ngram not in language_model[lang]:
                    language_model[lang][ngram] = 1  # AddOne Smoothing
                    total_count[lang] += 1

            language_model[language][ngram] += 1
            total_count[language] += 1

    input_file.close()

    return language_model, total_count


def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    :param in_file: testing file which contains lines for which prediction needs to be made
    :param out_file: file into which predicted result needs to be written into
    :param LM: contains lang_model with ngrams and lang_count which has vocabulary count
    """
    print("testing language models...")

    test_file = open(in_file, 'r')
    result_file = open(out_file, 'w')

    lang_model, lang_count = LM

    # Goes through test cases and predicts language based on probabilities found in language model
    for line in test_file:
        line_formatted = pre_process_line(line)

        test_ngrams = []
        for i in range(len(line_formatted) - NGRAM_MODEL_SIZE + 1):
            test_ngrams.append(tuple(line_formatted[i: i + NGRAM_MODEL_SIZE]))

        result_prob = {}
        not_present_in_LM = {}
        for lang in lang_model:
            not_present_in_LM[lang] = 0
            current_result = 0
            for gram in test_ngrams:
                if gram in lang_model[lang]:  # Only multiply probability if present in model
                    # Used log10 addition instead of probability multiplication to avoid floating number issue in python
                    current_result += log10(lang_model[lang][gram] / float(lang_count[lang]))
                else:  # Done to support "other language" if config enabled
                    not_present_in_LM[lang] += 1
            result_prob[current_result] = lang

        lang_detected = result_prob.get(max(result_prob))

        if SUPPORT_OTHER_LANGUAGE:
            if (min(not_present_in_LM.values()) / float(len(test_ngrams))) > OTHER_THRESHOLD:
                lang_detected = "other"

        result_file.write(lang_detected + " " + line)

    result_file.close()
    test_file.close()


def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b is None or input_file_t is None or output_file is None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
