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
cpdef cpredict(docs, sentencizer_fun):
    cdef list guesses
    cdef int s
    cdef int t
    guesses = []
    for doc in docs:
        if len(doc) == 0:
            guesses.append([])
            continue
        doc_guesses = [False] * len(doc)
        sentence_spans = sentencizer_fun(doc.text)
        s = 0
        t = 0
        while s < len(sentence_spans) and t < len(doc):
            span = sentence_spans[s]
            token = doc[t]
            if len(token.text.strip()) == 0:
                t += 1
                continue
            if token.idx <= span.begin < token.idx + len(token):
                doc_guesses[t] = True
                t += 1
                s += 1
            elif token.idx + len(token) <= span.begin:
                t += 1
            else:
                s += 1
        guesses.append(doc_guesses)
    return guesses

cpdef cset_annotations(docs, batch_tag_ids, tensors=None):
    if type(docs) !=list:
        docs = [docs]
    for i, doc in enumerate(docs):
        doc_tag_ids = batch_tag_ids[i]
        for j, tag_id in enumerate(doc_tag_ids):
            # Don't clobber existing sentence boundaries
            if tag_id:
                doc[j].sent_start = True
            else:
                doc[j].sent_start = False

# The function 'char_span' will try to match the tokens in the backend, as it might be less efficient when match
# sentences where it does not assume the sentences are sorted. Also, it will return None if not find a match rather
# than looking around. Thus, abandon this method.

# cpdef csegment(doc, sentencizer_fun):
#     for token in doc:
#         token.is_sent_start = False
#     sentence_spans = sentencizer_fun(doc.text)
#     for span in sentence_spans:
#         sent = doc.char_span(span.begin, span.end)
#         sent[0].is_sent_start = True
