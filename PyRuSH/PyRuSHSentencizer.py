# ******************************************************************************
#  MIT License
#
#  Copyright (c) 2020 Jianlin Shi
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
#  files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
#  modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ******************************************************************************
from spacy import Language
from spacy.pipeline import Sentencizer

from .RuSH import RuSH
from .StaticSentencizerFun import cpredict, cset_annotations


@Language.factory("medspacy_pyrush")
class PyRuSHSentencizer(Sentencizer):
    def __init__(self, nlp: Language, name: str = "medspacy_pyrush", rules_path: str = '', max_repeat: int = 50,
                 auto_fix_gaps: bool = True) -> Sentencizer:
        """

        @param rules_path: The string of the rule file path or rules themselves. By default, it will look for
        rush_rules.tsv in the site_packages/conf folder.
        @param max_repeat: Total number of replicates that allows to be handled by "+" wildcard.
        @param auto_fix_gaps: If gaps are caused by malcrafted rules, try to fix them.
            However, this has no control of sentence end,
             TODO: need to see how the downsteam spacy components make use of doc.c
        """
        self.nlp = nlp
        self.name = name
        if rules_path is None or rules_path == '':
            import os
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = str(os.path.join(root, 'conf', 'rush_rules.tsv'))
        self.rules_path = rules_path
        self.rush = RuSH(rules=rules_path, max_repeat=max_repeat, auto_fix_gaps=auto_fix_gaps)

    @classmethod
    def from_nlp(cls, nlp, **cfg):
        return cls(**cfg)

    def __call__(self, doc):
        tags = self.predict([doc])
        cset_annotations([doc], tags)
        return doc

    def predict(self, docs):
        """Apply the pipeline's model to a batch of docs, without
        modifying them.
        """
        guesses = cpredict(docs, self.rush.segToSentenceSpans)
        return guesses

    def set_annotations(self, docs, batch_tag_ids, tensors=None):
        """
        This function overwrite spacy's Sentencizer.

        @param batch_tag_ids: a list of doc's tags (a list of boolean values)
        @param tensors: a place holder for future extensions
        """
        cset_annotations(docs, batch_tag_ids, tensors)
