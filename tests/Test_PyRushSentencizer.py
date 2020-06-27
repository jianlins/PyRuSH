import unittest
import os

from PyRuSH import PyRuSHSentencizer
from spacy.lang.en import English


class TestRuSH(unittest.TestCase):

    def setUp(self):
        pwd = os.path.dirname(os.path.abspath(__file__))
        self.rush = PyRuSHSentencizer(str(os.path.join(pwd, 'rush_rules.tsv')))

    def test_doc(self):
        nlp = English()
        nlp.add_pipe(self.rush)
        doc = nlp("This is a sentence. This is another sentence.")
        print('\n'.join([str(s) for s in doc.sents]))
        print('\nTotal sentences: {}'.format(len([s for s in doc.sents])))
        print('\ndoc is an instance of {}'.format(type(doc)))

    def test_doc2(self):
        input_str='''        

        
        Ms. ABCD is a 69-year-old lady, who was admitted to the hospital with chest pain and respiratory insufficiency.  She has chronic lung disease with bronchospastic angina.
We discovered new T-wave abnormalities on her EKG.  There was of course a four-vessel bypass surgery in 2001.  We did a coronary angiogram.  This demonstrated patent vein grafts and patent internal mammary vessel and so there was no obvious new disease.
She may continue in the future to have angina and she will have nitroglycerin available for that if needed.
Her blood pressure has been elevated and so instead of metoprolol, we have started her on Coreg 6.25 mg b.i.d.  This should be increased up to 25 mg b.i.d. as preferred antihypertensive in this lady's case.  She also is on an ACE inhibitor.
So her discharge meds are as follows:
1.  Coreg 6.25 mg b.i.d.
2.  Simvastatin 40 mg nightly.
3.  Lisinopril 5 mg b.i.d.
4.  Protonix 40 mg a.m.
5.  Aspirin 160 mg a day.
6.  Lasix 20 mg b.i.d.
7.  Spiriva puff daily.
8.  Albuterol p.r.n. q.i.d.
9.  Advair 500/50 puff b.i.d.
10.  Xopenex q.i.d. and p.r.n.
I will see her in a month to six weeks.  She is to follow up with Dr. X before that.
        


 Ezoic - MTSam Sample Bottom Matched Content - native_bottom 




 End Ezoic - MTSam Sample Bottom Matched Content - native_bottom
'''
        pwd = os.path.dirname(os.path.abspath(__file__))
        self.rush = PyRuSHSentencizer(str(os.path.join(pwd, 'rush_rules.tsv')))
        nlp = English()
        nlp.add_pipe(self.rush)
        doc = nlp(input_str)
        sents=[s for s in doc.sents]
        for sent in sents:
            print('>'+str(sent)+'<')


