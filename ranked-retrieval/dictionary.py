import pickle
from math import sqrt, log

class Dictionary(object):
    """
    Getter and Setter functions related to the dictionary
    Also used to store on disk and access it using pickle
    Stores normalised docs length and also the total num of docs
    """
    def __init__(self, disk_file):
        self.terms = {}  # Format : {term: (documentFrequency, offsetOfPostingList) E.g. {"hello": (4, 63)}
        self.disk_file = disk_file  # File name where dictionary is stored in disk
        self.num_of_docs = 0  # Total number of documents in corpus
        self.normalised_doc_length = {}  # Format : { doc_id: normalized_length } where normalized_length = sqrt(sum((1+log(tf)^2)))

    def get_terms(self):
        """
        Gets all terms dictionary
        :return: terms with frequency and offset
        """
        return self.terms

    def get_df(self, token):
        """
        Gets the Document frequency for a term.
        Returns -1 if term not present
        :param token: term
        :return: int representing documentFrequency for the term
        """
        if token in self.terms:
            return self.terms[token][0]
        else:
            return -1

    def add_term(self, term, docFreq, offset):
        """
        Add a term to in memory dictionary
        :param term: normalised term
        :param docFreq: document Frequency of term
        :param offset: offset in postings file for posting list of word
        """
        self.terms[term] = [docFreq, offset]

    def get_offset_of_term(self, term):
        """
        Gets offset to seek to for posting list in posting file
        :param term: normalised term
        :return: -1 if term not present and offset if term present
        """
        if term in self.terms:
            return self.terms[term][1]
        else:
            return -1

    def update_offset(self, term, offset):
        """
        Updates offset of where data stored in posting list
        :param term: normaised term
        :param offset: offset in postings file for posting list of word
        """
        self.terms[term][1] = offset

    def add_normalised_doc_length(self, doc_id, tf_for_doc):
        """
        Calculates and Sets the Document normalised length for a doc_id given.
        where normalized_length = sqrt(sum((1+log(tf)^2)))
        :param doc_id: docId for which it is to be set
        :param tf_for_doc: dict() with tf for a doc {term: freqForTerm}
        """
        tf = 0
        for term, freq in tf_for_doc.items():
            tf += pow((1 + log(freq, 10)), 2)
        self.normalised_doc_length[doc_id] = sqrt(tf)

    def get_normalised_doc_length(self, doc_id):
        """
        Gets the Document normalised length for a doc_id.
        :param doc_id: document ID
        :return: float Document normalised length of docId
        """
        return self.normalised_doc_length[doc_id]

    def add_doc_count(self):
        """
        Adds one to doc count of corpus
        """
        self.num_of_docs += 1

    def get_doc_count(self):
        """
        Gets the total number of docs in corpus
        :return: num_of_docs
        """
        return self.num_of_docs

    def save(self):
        """
        Saves dictionary dict() using pickle dump
        in dict format as {terms: {}, normalised_doc_length: {}, num_of_docs: int}
        """
        with open(self.disk_file, 'wb') as f:
            pickle.dump({
                "terms": self.terms,
                "normalised_doc_length": self.normalised_doc_length,
                "num_of_docs": self.num_of_docs }, f)
        f.close()

    def load(self):
        """
        Loads dictionary from disk and stores in the Dictionary in memory object
        in dict format as {terms: {}, normalised_doc_length: {}, num_of_docs: int}
        """
        with open(self.disk_file, 'rb') as f:
            res = pickle.load(f)
            self.terms = res["terms"]
            self.normalised_doc_length = res["normalised_doc_length"]
            self.num_of_docs = res["num_of_docs"]
        f.close()
