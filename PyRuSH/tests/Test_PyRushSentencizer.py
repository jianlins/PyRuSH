import unittest
import os

from PyRuSH import PyRuSHSentencizer
from spacy.lang.en import English


class TestRuSH(unittest.TestCase):

    def setUp(self):
        pwd = os.path.dirname(os.path.abspath(__file__))
        self.rush = PyRuSHSentencizer(str(os.path.join(pwd, '../../conf/rush_rules.tsv')))

    def test_doc(self):
        nlp = English()
        nlp.add_pipe(self.rush)
        doc = nlp("This is a sentence. This is another sentence.")
        print('\n'.join([str(s) for s in doc.sents]))
        print('\nTotal sentences: {}'.format(len([s for s in doc.sents])))
        print('\ndoc is an instance of {}'.format(type(doc)))
