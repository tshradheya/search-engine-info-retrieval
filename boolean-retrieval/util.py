import nltk
import os
import terms_eval
import pickle

STEMMER = nltk.stem.porter.PorterStemmer()


def get_posting_list(posting_file, offset):
    """
    Gets posting list for a given offset in file
    :param posting_file: postings.txt disk file
    :param offset: the offset to seek to in file
    :return: Posting list [(1, 0), (10,0)]
    """
    with open(posting_file, 'rb') as file:
        file.seek(offset)
        return pickle.load(file)


def read_document(directory, doc):
    """
    retrieves the tokenzied/stemmed words in each document
    :param directory: of all corpus documents
    :param doc: documentId to read
    :return: all normalised terms
    """
    terms = []
    with open(os.path.join(directory, str(doc))) as in_file:
        content = in_file.read()
        sentences = nltk.tokenize.sent_tokenize(content)
        for sentence in sentences:
            words = nltk.tokenize.word_tokenize(sentence)
            for word in words:
                terms.append(STEMMER.stem(word).lower())

        return terms

def reverse_polish_expression(query):
    """
    Converts the input query to a postfix expression using Shunting yard algorithm
    :param query: Query to evaluate. E.g. a AND b
    :return: Postfix expression of query. E.g. a b AND
    """

    query_tokens = nltk.tokenize.word_tokenize(query)
    postfix_expression = []
    temp_stack = []
    OPERATORS = ['NOT', 'AND', 'OR']
    BRACKETS = ['(', ')']

    for query_token in query_tokens:
        if query_token not in OPERATORS and (query_token not in BRACKETS):
            postfix_expression.append(STEMMER.stem(query_token).lower())
        elif query_token == 'NOT':
            temp_stack.append(query_token)
        elif query_token == 'AND':
            while len(temp_stack) > 0 and temp_stack[-1] == 'NOT':
                postfix_expression.append(temp_stack.pop())
            temp_stack.append(query_token)        
        elif query_token == 'OR':
            while len(temp_stack) > 0 and (temp_stack[-1] == 'NOT' or temp_stack[-1] == 'AND'):
                postfix_expression.append(temp_stack.pop())
            temp_stack.append(query_token)    
        elif query_token == '(':
            temp_stack.append(query_token)
        else:
            while len(temp_stack) > 0 and (temp_stack[-1] != '('):
                postfix_expression.append(temp_stack.pop())
            temp_stack.pop()           

    while len(temp_stack) > 0:
        postfix_expression.append(temp_stack.pop())

    return postfix_expression


def execute_query(query, dictionary, posting_file):
    """
    Computes the result of the user query
    :param query: Postfix expression
    :param dictionary: in memory dictionary object
    :param posting_file:
    :return: final result in posting list format
    """

    OPERATORS = ['NOT', 'AND', 'OR']
    operands = []
    len_query = len(query)

    i = 0
    while i < len_query:
        token = query[i]
        if token not in OPERATORS:
            operands.append(token)

        elif len(operands) > 0:
            intermediate_result = []
            if token == 'NOT':
                term = operands.pop()
                #  optimize for AND NOT queries
                if i < len_query - 1 and len(operands) > 0 and query[i+1] == "AND":
                    i += 1
                    later_term = operands.pop()
                    intermediate_result = terms_eval.eval_AND_NOT(posting_file, dictionary, later_term, term)
                else:
                    intermediate_result = terms_eval.eval_NOT(posting_file, dictionary, term)
            elif token == 'AND':
                first = operands.pop()
                second = operands.pop()
                intermediate_result = terms_eval.eval_AND(posting_file, dictionary, first, second)
            elif token == 'OR':
                first = operands.pop()
                second = operands.pop()
                intermediate_result = terms_eval.eval_OR(posting_file, dictionary, first, second)
            operands.append(intermediate_result)

        i += 1

    final_result = operands.pop()
    if isinstance(final_result, str):
        first_offset = dictionary.get_offset_of_term(final_result)
        if first_offset != -1:
            final_result = get_posting_list(posting_file, first_offset)
        else:
            final_result = []

    return final_result


def format_result(result):
    """
    Formats result as required for output file
    :param result: In format [(1, 0), (10, 0)]
    :return: '1 10' formatted string
    """
    formatted_res = list()
    for val in result:
        formatted_res.append(val[0])

    formatted_res = " ".join(map(str, formatted_res))
    return formatted_res

