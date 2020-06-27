# Copyright  2018  Department of Biomedical Informatics, University of Utah
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pathlib import Path
from typing import Union, List

from PyFastNER import FastCNER
from PyFastNER import Span
import logging
import logging.config
import os.path
import string

BEGIN = 'stbegin'
END = 'stend'


def initLogger():
    config_files = ['../../../conf/logging.ini', '../../conf/logging.ini', '../conf/logging.ini', 'conf/logging.ini',
                    'logging.ini']
    config_file = None
    for f in config_files:
        if os.path.isfile(f):
            config_file = f
            break
    if config_file is None:
        config_file = config_files[-1]
        print(config_file)
        with open(config_file, 'w') as f:
            f.write('''[loggers]
keys=root

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=WARNING
handlers=consoleHandler

[handler_consoleHandler]
class=StreamHandler
level=WARNING
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=
''')
    logging.config.fileConfig(config_file)


class RuSH:

    def __init__(self, rules: Union[str, List] = '', max_repeat: int = 50, auto_fix_gaps: bool = True,
                 enable_logger: bool = False):
        self.fastner = FastCNER(rules, max_repeat)
        self.fastner.span_compare_method = 'scorewidth'
        if enable_logger:
            # initLogger()
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
        self.auto_fix_gaps = auto_fix_gaps
        # for old RuSh rule format (doesn't have PSEUDO and ACTUAL column), make the conversion.
        if not self.fastner.full_definition:
            self.backCompatableParseRule()
        pass

    def backCompatableParseRule(self):
        for id, rule in self.fastner.rule_store.items():
            if rule.score % 2 != 0:
                rule.type = 'PSEUDO'
        self.fastner.constructRuleMap(self.fastner.rule_store)
        pass

    def segToSentenceSpans(self, text):
        output = []
        result = self.fastner.processString(text)

        # log important message for debugging use
        if self.logger is not None and self.logger.isEnabledFor(logging.DEBUG):
            text = text.replace('\n', ' ')
            for concept_type, spans in result.items():
                self.logger.debug(concept_type)
                for span in spans:
                    rule = self.fastner.rule_store[span.rule_id]
                    self.logger.debug('\t{0}-{1}:{2}\t{3}<{4}>\t[Rule {5}:\t{6}\t{7}\t{8}\t{9}]'.format(
                        span.begin, span.end, span.score, text[:span.begin],
                        text[span.begin:span.begin + 1],
                        rule.id, rule.rule, rule.rule_name,
                        rule.score, rule.type
                    ))

        begins = result[BEGIN]
        ends = result[END]

        if begins is None or len(begins) == 0:
            begins = [Span(0, 1)]

        if ends is None or len(ends) == 0:
            ends = [Span(len(text) - 1, len(text))]

        st_begin = 0
        st_started = False
        st_end = 0
        j = 0

        for i in range(0, len(begins)):
            if not st_started:
                st_begin = begins[i].begin
                if st_begin < st_end:
                    continue
                st_started = True
            elif begins[i].begin < st_end:
                continue

            if self.auto_fix_gaps and len(output) > 0 and st_begin > output[-1].end:
                self.fix_gap(output, text, output[-1].end, st_begin)

            for k in range(j, len(ends)):
                if i < len(begins) - 1 and k < len(ends) - 1 and begins[i + 1].begin < ends[k].begin + 1:
                    break
                st_end = ends[k].begin + 1
                j = k
                while st_end >= 1 and (text[st_end - 1].isspace() or ord(text[st_end - 1]) == 160):
                    st_end -= 1
                if st_end < st_begin:
                    continue
                elif st_started:
                    output.append(Span(st_begin, st_end))
                    st_started = False
                    if i == len(begins) - 1 or (k < len(ends) - 1 and begins[i + 1].begin > ends[k + 1].end):
                        continue
                    break
                else:
                    output[len(output) - 1] = Span(st_begin, st_end)
                    st_started = False

        if self.logger is not None and self.logger.isEnabledFor(logging.DEBUG):
            for sentence in output:
                self.logger.debug(
                    'Sentence({0}-{1}):\t>{2}<'.format(sentence.begin, sentence.end, text[sentence.begin:sentence.end]))

        return output

    @staticmethod
    def fix_gap(sentences: [], text: str, previous_end: int, this_begin: int):
        counter = 0
        begin = 0
        end = 0
        gap_chars = text[previous_end:this_begin]
        for i in range(0, this_begin - previous_end):
            this_char = gap_chars[i]
            if this_char.isalnum():
                end = i
                counter += 1
                if begin == 0:
                    begin = i
            elif this_char in string.punctuation:
                end = i
        # An arbitrary number to decide whether the gap is likely to be a sentence or not
        if counter > 5:
            begin += previous_end
            end = end + previous_end + 1
            sentences.append(Span(begin, end))
        pass
