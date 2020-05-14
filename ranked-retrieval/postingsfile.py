import pickle
from collections import defaultdict


class PostingsFile(object):
    """
    Getter and Setter functions related to the postings and posting list
    Also used to store on disk and access it using pickle and until functions
    """
    def __init__(self, file_name):
        self.disk_file = file_name
        self.postings = defaultdict(list)

    def format_posting(self, temp_postings):
        """
        Fomrats from dict to optimised storable and readable data strcture
        {term: {docId: tf}} => [(docId, df)]
        :param temp_postings: of format {term: {docId: tf}}
        """
        for key, docs in temp_postings.items():
            for docId, tf in docs.items():
                self.postings[key].append((docId, tf))

    def save(self, dictionary):
        with open(self.disk_file, 'wb') as posting_file:
            for token, docs_list in sorted(self.postings.items()):
                offset = posting_file.tell()
                dictionary.add_term(token, len(docs_list), offset)
                pickle.dump(sorted(docs_list), posting_file)
        posting_file.close()

    def get_postings(self):
        """
        Gets postings in file
        :return: postings
        """
        return self.postings

    def get_posting_list(self, offset):
        """
        Gets posting list for a given offset in file
        :param offset: the offset to seek to in file
        :return: Posting list with TF [(1, 5), (10, 4)]
        """
        with open(self.disk_file, 'rb') as file:
            file.seek(offset)
            return pickle.load(file)

