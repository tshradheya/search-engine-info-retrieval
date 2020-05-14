import util
from math import sqrt

ALL_DOCS = "$all_docs$"

def eval_NOT(posting_file, dictionary, first):
    """
    Evaluates NOT of first
    :param posting_file: postings.txt disk file
    :param dictionary: in memory dictionary
    :param first: term or result of which NOT needs to be done
    :return: Result in format of posting list of NOT a
    """
    result = list()
    #  Get from posting if term otherwise use given result
    if isinstance(first, str):
        first_offset = dictionary.get_offset_of_term(first)
        if first_offset != -1:
            first_list = util.get_posting_list(posting_file, first_offset)
        else:
            first_list = []
    else:
        first_list = first

    all_docs_offset = dictionary.get_offset_of_term(ALL_DOCS)
    if all_docs_offset != -1:
        all_docs_list = util.get_posting_list(posting_file, all_docs_offset)
    else:
        all_docs_list = []

    idx_f = 0
    idx_s = 0

    len_first_list = len(first_list)
    len_all_docs_list = len(all_docs_list)

    while idx_f < len_first_list and idx_s < len_all_docs_list:
        first_doc_id = first_list[idx_f][0]
        second_doc_id = all_docs_list[idx_s][0]
        if first_doc_id == second_doc_id:
            idx_f += 1
            idx_s += 1
        else:
            result.append(all_docs_list[idx_s])
            idx_s += 1
    while idx_s < len_all_docs_list:
        result.append(all_docs_list[idx_s])
        idx_s += 1

    return result

def eval_OR(posting_file, dictionary, first, second):
    """
    Evaluates first OR second  [can be term or direct result]
    :param posting_file: postings.txt disk file
    :param dictionary: in memory dictionary
    :param first: term or result of which OR needs to be done
    :param second: term or result of which OR needs to be done
    :return: Result in format of posting list of a OR B
    """
    result = list()

    #  Get from posting if term otherwise use given result
    if isinstance(first, str):
        first_offset = dictionary.get_offset_of_term(first)
        if first_offset != -1:
            first_list = util.get_posting_list(posting_file, first_offset)
        else:
            first_list = []
    else:
        first_list = first

    if isinstance(second, str):
        second_offset = dictionary.get_offset_of_term(second)
        if second_offset != -1:
            second_list = util.get_posting_list(posting_file, second_offset)
        else:
            second_list = []
    else:
        second_list = second

    idx_f = 0
    idx_s = 0

    len_first_list = len(first_list)
    len_second_list = len(second_list)

    while idx_f < len_first_list and idx_s < len_second_list:
        first_doc_id = first_list[idx_f][0]
        second_doc_id = second_list[idx_s][0]
        if first_doc_id == second_doc_id:
            result.append(first_list[idx_f])
            idx_f += 1
            idx_s += 1
        elif first_doc_id < second_doc_id:
            result.append(first_list[idx_f])
            idx_f += 1
        else:
            result.append(second_list[idx_s])
            idx_s += 1

    while idx_f < len_first_list:
        result.append(first_list[idx_f])
        idx_f += 1

    while idx_s < len_second_list:
        result.append(second_list[idx_s])
        idx_s += 1

    return result

def eval_AND(posting_file, dictionary, first, second):
    """
    Evaluates first AND second  [can be term or direct result]
    Uses skip pointer if one of argument is directly a posting list with correct skips
    :param posting_file: postings.txt disk file
    :param dictionary: in memory dictionary
    :param first: term or result of which AND needs to be done
    :param second: term or result of which AND needs to be done
    :return: Result in format of posting list of a AND B
    """
    result = list()

    # Based on if its a term or intermediate result find the posting list and use skip pointer if possible
    if not isinstance(first, str) and not isinstance(second, str):
        result = eval_AND_Lists(first, second)
    elif isinstance(first, str) and not isinstance(second, str):
        offset = dictionary.get_offset_of_term(first)
        if offset != -1:
            term_list = util.get_posting_list(posting_file, offset)
        else:
            term_list = []
        result = eval_AND_List_And_Term(second, term_list)
    elif not isinstance(first, str) and isinstance(second, str):
        offset = dictionary.get_offset_of_term(second)
        if offset != -1:
            term_list = util.get_posting_list(posting_file, offset)
        else:
            term_list = []
        result = eval_AND_List_And_Term(first, term_list)
    else:

        first_offset = dictionary.get_offset_of_term(first)
        if first_offset != -1:
            first_list = util.get_posting_list(posting_file, first_offset)
        else:
            first_list = []

        second_offset = dictionary.get_offset_of_term(second)
        if second_offset != -1:
            second_list = util.get_posting_list(posting_file, second_offset)
        else:
            second_list = []

        idx_f = 0
        idx_s = 0

        len_first_list = len(first_list)
        len_second_list = len(second_list)

        while idx_f < len_first_list and idx_s < len_second_list:
            first_doc_id = first_list[idx_f][0]
            second_doc_id = second_list[idx_s][0]

            first_skip_idx = first_list[idx_f][1]
            second_skip_idx = second_list[idx_s][1]
            if first_doc_id == second_doc_id:
                result.append(first_list[idx_f])
                idx_f += 1
                idx_s += 1
            elif first_doc_id < second_doc_id:
                if first_skip_idx != 0 and first_skip_idx < len_first_list and first_list[first_skip_idx][0] <= second_doc_id:
                    idx_f = first_skip_idx
                else:
                    idx_f += 1
            else:
                if second_skip_idx != 0 and second_skip_idx < len_second_list and second_list[second_skip_idx][0] <= first_doc_id:
                    idx_s = second_skip_idx
                else:
                    idx_s += 1

    return result

def eval_AND_Lists(first_list, second_list):
    """
    Evaluates first_list AND second_list  [is direct result and hence no skip pointer]
    :param first_list: list of which AND needs to be done
    :param second_list: list of which AND needs to be done
    :return: Result in format of posting list of list() AND list()
    """

    result = list()
    idx_f = 0
    idx_s = 0

    len_first_list = len(first_list)
    len_second_list = len(second_list)

    skip_first_list = int(sqrt(len_first_list))
    skip_second_list = int(sqrt(len_second_list))

    while idx_f < len_first_list and idx_s < len_second_list:
        first_doc_id = first_list[idx_f][0]
        second_doc_id = second_list[idx_s][0]

        first_skip_idx = idx_f + skip_first_list
        second_skip_idx = idx_s + skip_second_list
        if first_doc_id == second_doc_id:
            result.append(first_list[idx_f])
            idx_f += 1
            idx_s += 1
        elif first_doc_id < second_doc_id:
            if first_skip_idx != 0 and first_skip_idx < len_first_list and first_list[first_skip_idx][0] <= second_doc_id:
                idx_f = first_skip_idx
            else:
                idx_f += 1
        else:
            if second_skip_idx != 0 and second_skip_idx < len_second_list and second_list[second_skip_idx][0] <= first_doc_id:
                idx_s = second_skip_idx
            else:
                idx_s += 1

    return result


def eval_AND_List_And_Term(res_list, term_list):
    """
    Evaluates first_list AND term_list [can use skip for term_list since directly queried from disk]
    :param res_list: list of which AND needs to be done
    :param term_list: term of which AND needs to be done. skip can be used for this
    :return: Result in format of posting list of list() AND term
    """
    result = list()
    idx_f = 0
    idx_s = 0

    len_res_list = len(res_list)
    len_term_list = len(term_list)

    while idx_f < len_res_list and idx_s < len_term_list:
        first_doc_id = res_list[idx_f][0]
        second_doc_id = term_list[idx_s][0]

        skip_ptr = term_list[idx_s][1]
        if first_doc_id == second_doc_id:
            result.append(res_list[idx_f])
            idx_f += 1
            idx_s += 1
        elif first_doc_id < second_doc_id:
            idx_f += 1
        else:
            if skip_ptr != 0 and skip_ptr < len_term_list and term_list[skip_ptr][0] <= first_doc_id:
                idx_s = skip_ptr
            else:
                idx_s += 1

    return result


def eval_AND_NOT(posting_file, dictionary, first, second):
    """
    first AND NOT second [using skip pointer]
    :param posting_file: postings.txt
    :param dictionary: Dictionary object in memory
    :param first: first postings list
    :param second: second postings list
    :return: merged list
    """
    result = list()

    # If the term being NOT is a string then we use skip pointer otherwise we cant since its intermediate result
    if not isinstance(first, str) and not isinstance(second, str):
        result = eval_AND_NOT_Lists(first, second)
    elif isinstance(first, str) and not isinstance(second, str):
        offset = dictionary.get_offset_of_term(first)
        if offset != -1:
            term_list = util.get_posting_list(posting_file, offset)
        else:
            term_list = []
        result = eval_AND_NOT_Lists(term_list, second)
    else:
        if isinstance(first, str):
            first_offset = dictionary.get_offset_of_term(first)
            if first_offset != -1:
                first_list = util.get_posting_list(posting_file, first_offset)
            else:
                first_list = []
        else:
            first_list = first

        second_offset = dictionary.get_offset_of_term(second)
        if second_offset != -1:
            second_list = util.get_posting_list(posting_file, second_offset)
        else:
            second_list = []

        idx_f = 0
        idx_s = 0

        len_first_list = len(first_list)
        len_second_list = len(second_list)

        while idx_f < len_first_list and idx_s < len_second_list:
            first_doc_id = first_list[idx_f][0]
            second_doc_id = second_list[idx_s][0]

            skip_ptr = second_list[idx_s][1]
            if first_doc_id == second_doc_id:
                idx_f += 1
                idx_s += 1
            elif first_doc_id < second_doc_id:
                result.append(first_list[idx_f])
                idx_f += 1
            else:
                if skip_ptr != 0 and skip_ptr < len_second_list and second_list[skip_ptr][0] <= first_doc_id:
                    idx_s = skip_ptr
                else:
                    idx_s += 1

        while idx_f < len_first_list:
            result.append(first_list[idx_f])
            idx_f += 1

    return result


def eval_AND_NOT_Lists(first_list, second_list):
    """
    first_list AND NOT second_list [not using skip pointer]
    :param first_list: first intermediate result list
    :param second_list: second intermediate result list
    :return: merged list
    """
    result = list()
    idx_f = 0
    idx_s = 0

    len_first_list = len(first_list)
    len_second_list = len(second_list)

    skip_second_list = int(sqrt(len_second_list))

    while idx_f < len_first_list and idx_s < len_second_list:
        first_doc_id = first_list[idx_f][0]
        second_doc_id = second_list[idx_s][0]

        second_skip_idx = idx_s + skip_second_list
        if first_doc_id == second_doc_id:
            idx_f += 1
            idx_s += 1
        elif first_doc_id < second_doc_id:
            result.append(first_list[idx_f])
            idx_f += 1
        else:
            if second_skip_idx != 0 and second_skip_idx < len_second_list and second_list[second_skip_idx][0] <= first_doc_id:
                idx_s = second_skip_idx
            else:
                idx_s += 1

    while idx_f < len_first_list:
        result.append(first_list[idx_f])
        idx_f += 1

    return result
