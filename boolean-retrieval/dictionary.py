import pickle

class Dictionary(object):
    """
    Getter and Setter functions related to the dictionary
    Also used to store on disk and access it using pickle
    """
    def __init__(self, disk_file):
        self.terms = {}  # Format : {term: (documentFrequency, offsetOfPostingList) E.g. {"hello": (4, 63)}
        self.disk_file = disk_file  # File name where dictionary is stored in disk

    def get_terms(self):
        """
        Gets all terms dictionary
        :return: terms with frequency and offset
        """
        return self.terms

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

    def save(self):
        """
        Saves dictionary dict() using pickle dump
        """
        with open(self.disk_file, 'wb') as f:
            pickle.dump(self.terms, f)

    def load(self):
        """
        Loads dictionary from disk and stores in the Dictionary in memory object
        """
        with open(self.disk_file, 'rb') as f:
            self.terms = pickle.load(f)
