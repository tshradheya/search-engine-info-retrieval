#!/usr/bin/python3
import sys
import getopt
from dictionary import Dictionary
from postingsfile import PostingsFile
import util

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """

    dictionary = Dictionary(dict_file)
    postings = PostingsFile(postings_file)

    dictionary.load()  # Load dictionary into memory

    with open(queries_file, 'r') as query_file:
        with open(results_file, 'w') as output_file:
            complete_result = []
            for query in query_file:
                if query.strip():
                    result = util.eval_query(query, dictionary, postings)
                    result = util.format_result(result)
                    complete_result.append(result)
                else:
                    complete_result.append("")

            write_data = "\n".join(complete_result)
            output_file.write(write_data)

        output_file.close()
    query_file.close()


dictionary_file = postings_file = file_of_queries = file_of_output = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
