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

from PyFastNER import Span
from py4j.java_gateway import JavaGateway
import os
from pathlib import Path


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
                 enable_logger: bool = False, py4jar: str = 'lib/py4j0.10.9.7.jar',
                 rushjar: str = 'lib/rush-2.0.0.0-jdk1.8-jar-with-dependencies.jar',
                 java_path: str = 'java'):

        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not Path(py4jar).exists():
            py4jar = str(os.path.join(root, 'lib', 'py4j0.10.9.7.jar'))
        if not Path(rushjar).exists():
            rushjar = str(os.path.join(root, 'lib', 'rush-2.0.0.0-jdk1.8-jar-with-dependencies.jar'))
        self.gateway = JavaGateway.launch_gateway(jarpath=py4jar,
                                                            classpath=rushjar,
                                                            java_path=java_path, die_on_exit=True, use_shell=False)
        if isinstance(rules, List):
            rules = '\n'.join(rules)
        self.jrush = self.gateway.jvm.edu.utah.bmi.nlp.rush.core.RuSH(rules)
        if enable_logger:
            initLogger()
            self.gateway.jvm.py4j.GatewayServer.turnLoggingOn()
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
        self.min_sent_chars = min_sent_chars
        pass

    def segToSentenceSpans(self, text):
        output = [Span(s.getBegin(), s.getEnd()) for s in self.jrush.segToSentenceSpans(text)]

        # log important message for debugging use
        if self.logger is not None and self.logger.isEnabledFor(logging.DEBUG):
            text = text.replace('\n', ' ')
        if len(output)>0:
            for i, span in enumerate(output):
                if i==0:
                    span=RuSH.trim_gap(text, 0, span.begin)
                else:
                    previous=output[i-1]
                    span=RuSH.trim_gap(text, previous.end, span.begin)
                if span is not None:
                    output[i]=span
        return output

    def shutdownJVM(self):
        self.gateway.shutdown()

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