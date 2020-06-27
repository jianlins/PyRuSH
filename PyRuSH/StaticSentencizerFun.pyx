from spacy.tokens import Doc

cpdef cpredict(docs, sentencizer_fun):
    cdef list guesses
    cdef int s
    cdef int t
    guesses = []
    for doc in docs:
        if len(doc)==0:
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
            if token.idx <= span.begin < token.idx+len(token):
                doc_guesses[t]=True
                t+=1
                s+=1
            elif token.idx+len(token)<=span.begin:
                t+=1
            else:
                s+=1
        guesses.append(doc_guesses)
    return guesses

cpdef cset_annotations(docs, batch_tag_ids, tensors=None):
    if isinstance(docs, Doc):
        docs = [docs]
    for i, doc in enumerate(docs):
        doc_tag_ids = batch_tag_ids[i]
        for j, tag_id in enumerate(doc_tag_ids):
            # Don't clobber existing sentence boundaries
            if tag_id:
                doc[j].sent_start = True
            else:
                doc[j].sent_start = False

# cpdef csegment(doc, sentencizer_fun):
#     for token in doc:
#         token.is_sent_start = False
#     sentence_spans = sentencizer_fun(doc.text)
#     for span in sentence_spans:
#         sent = doc.char_span(span.begin, span.end)
#         sent[0].is_sent_start = True