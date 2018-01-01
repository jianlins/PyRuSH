# PyFastNER

PyFastNER is the python implementation of [FastNER](https://github.com/jianlins/FastNER), which is orginally developed 
using Java. It uses hash function to process multiple rules at the same time. Similar to FastNER, PyFastNER 
supports token-based rules (FastNER--under developing) and character-based rules
 ([FastCNER](https://github.com/jianlins/PyFastNER/blob/master/nlp/FastCNER.py)). It is licensed under the 
 [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

### Install:
```bash
pip install PyFastNER
```
 
### Examples:
Here is a simiple example of using external dictionary to find matches in an input string. It will return 
a dictionary of spans grouped by the named entity types.
```python
from nlp.FastCNER import FastCNER
# initiate fastner using external rule file
fastner = FastCNER('conf/crule_test.tsv')
# process an input string
res = fastner.processString('Pt came with fever, T 102.0F.')
# display processed results
for type in res.keys():
	for span in res[type]:
		print(span)
```

Here is another example if you need process a sentence within a document, where you just need to tell the offset of
the sentence to the beginning of the document.
```python
from nlp.FastCNER import FastCNER
fastner = FastCNER('conf/crule_test.tsv')
res = fastner.processString('Pt came with fever, T 102.0F.',134)
```

For more examples, please refer to [TestFastCNER.py](https://github.com/jianlins/PyFastNER/blob/master/test/TestFastCNER.py)
