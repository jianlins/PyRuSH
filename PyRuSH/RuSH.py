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
import logging
import logging.config
import os.path
from typing import Union, List

from PyFastNER import FastCNER
from PyFastNER import Span

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
                 min_sent_chars: int = 5,
                 enable_logger: bool = False):
        self.fastner = FastCNER(rules, max_repeat)
        self.fastner.span_compare_method = 'scorewidth'
        if enable_logger:
            initLogger()
            self.logger = logging.getLogger(__name__)
            print(self.logger.level)
        else:
            self.logger = None
        self.auto_fix_gaps = auto_fix_gaps
        # for old RuSh rule format (doesn't have PSEUDO and ACTUAL column), make the conversion.
        if not self.fastner.full_definition:
            self.backCompatableParseRule()
        self.min_sent_chars = min_sent_chars
        pass

    def backCompatableParseRule(self):
        for id, rule in self.fastner.rule_store.items():
            if rule.score % 2 != 0:
                rule.type = 'PSEUDO'
        self.fastner.constructRuleMap(self.fastner.rule_store)
        pass

    def segToSentenceSpans(self, text):
        output = []
        result = {BEGIN: [], END: []}
        self.fastner.process(text, 0, result)

        # log important message for debugging use
        if self.logger is not None and self.logger.isEnabledFor(logging.DEBUG):
            text = text.replace('\n', ' ')
            for concept_type, spans in result.items():
                self.logger.debug(concept_type)
                for span in spans:
                    rule = self.fastner.rule_store[span.rule_id]
                    self.logger.debug(
                        '\t{0}-{1}:{2}\t{3}<{4}>\t[Rule {5}:\t{6}\t{7}\t{8}\t{9}]'.format(span.begin, span.end,
                                                                                          span.score,
                                                                                          text[:span.begin],
                                                                                          text[
                                                                                          span.begin:span.begin + 1],
                                                                                          rule.id, rule.rule,
                                                                                          rule.rule_name,
                                                                                          rule.score, rule.type))
        begins = result[BEGIN]
        ends = result[END]

        st_begin = 0
        st_started = False
        st_end = 0
        j = 0

        for i in range(0, len(begins)):
            token = begins[i]
            if not st_started:
                st_begin = token.begin
                if st_begin < st_end:
                    continue
                st_started = True
            elif token.begin < st_end:
                continue

            if self.auto_fix_gaps and len(output) > 0 and st_begin > output[-1].end:
                self.fix_gap(output, text, output[-1].end, st_begin, self.min_sent_chars)
            elif self.auto_fix_gaps and len(output) == 0 and st_begin > 0:
                self.fix_gap(output, text, 0, st_begin, self.min_sent_chars)

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
        # fix beginning and ending gaps, in case the existing rules will miss some cases
        if self.auto_fix_gaps:
            if len(output) > 0:
                begin_trimed_gap = RuSH.trim_gap(text, 0, output[0].begin)
                if begin_trimed_gap is not None:
                    if output[0].begin <= ends[0].begin:
                        output[0].begin = begin_trimed_gap.begin
                    else:
                        output.insert(0, begin_trimed_gap)
                end_trimed_gap = RuSH.trim_gap(text, output[-1].end, len(text))
                if end_trimed_gap is not None:
                    if end_trimed_gap.width > self.min_sent_chars:
                        output.append(end_trimed_gap)
                    else:
                        output[-1].end = end_trimed_gap.end
            else:
                trimed_gap = RuSH.trim_gap(text, 0, len(text))
                if trimed_gap is not None and trimed_gap.width > self.min_sent_chars:
                    output.append(trimed_gap)

        if self.logger is not None and self.logger.isEnabledFor(logging.DEBUG):
            for sentence in output:
                self.logger.debug(
                    'Sentence({0}-{1}):\t>{2}<'.format(sentence.begin, sentence.end, text[sentence.begin:sentence.end]))

        return output

    @staticmethod
    def fix_gap(sentences: [], text: str, previous_end: int, this_begin: int, min_sent_chars: int = 5):
        trimed_gap = RuSH.trim_gap(text, previous_end, this_begin)
        if trimed_gap is None:
            return
        if trimed_gap.width > min_sent_chars:
            sentences.append(trimed_gap)
        elif len(sentences) > 0:
            sentences[-1].end = trimed_gap.end

    @staticmethod
    def trim_gap(text: str, previous_end: int, this_begin: int) -> Span:
        begin = -1
        alnum_begin = -1
        end = 0
        gap_chars = list(text[previous_end:this_begin])
        # trim left
        for i in range(0, this_begin - previous_end):
            this_char = gap_chars[i]
            if not this_char.isspace():
                begin = i
                break
        for i in range(this_begin - previous_end - 1, begin, -1):
            this_char = gap_chars[i]
            if this_char.isalnum() or this_char == '.' or this_char == '!' or this_char == '?' or this_char == ')' or this_char \
                    == ']' or this_char == '\"':
                end = i
                break
        if end > begin != -1:
            return Span(begin + previous_end, end + previous_end + 1)
        else:
            return None
