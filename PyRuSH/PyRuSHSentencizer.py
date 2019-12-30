from spacy import util
from spacy.pipeline import Sentencizer
from PyRuSH import RuSH

from .StaticSentencizerFun import cpredict, cset_annotations


class PyRuSHSentencizer(Sentencizer):
    def __init__(self, rules_path: str = '', max_repeat: int = 50, auto_fix_gaps: bool = True):
        self.rules_path = rules_path
        self.rush = RuSH(rules_path=rules_path, max_repeat=max_repeat, auto_fix_gaps=auto_fix_gaps)

    @classmethod
    def from_nlp(cls, nlp, **cfg):
        return cls(**cfg)

    def __call__(self, doc, token_compatible=True):
        if token_compatible:
            # this approach only works for spacy >=2.2.3
            # however, this has no control of sentence end, TODO: need to see how the downsteam spacy components make use of doc.c
            tags = self.predict([doc])
            self.set_annotations([doc], tags)
            return doc
        else:
            for token in doc:
                token.is_sent_start = False
            sentence_spans = self.rush.segToSentenceSpans(doc.text)
            for span in sentence_spans:
                sent = doc.char_span(span.begin, span.end)
                sent[0].is_sent_start = True
            return doc

    # maybe able to omit
    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in util.minibatch(stream, size=batch_size):
            docs = list(docs)
            tag_ids = self.predict(docs)
            self.set_annotations(docs, tag_ids)
            yield from docs

    def predict(self, docs):
        """Apply the pipeline's model to a batch of docs, without
        modifying them.
        """
        guesses = cpredict(docs, self.rush.segToSentenceSpans)
        return guesses

    # maybe able to omit
    def set_annotations(self, docs, batch_tag_ids, tensors=None):
        cset_annotations(docs, batch_tag_ids, tensors)
