# Copyright Mozilla Foundation
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

import re
from ..model import Message, PatternMessage, SelectMessage
from ..model import Expression, VariableRef, Markup
from typing import Any

def count_strings(lst:list[str]) -> int:
    pattern = re.compile(r"(([\w']+-)*[\w']+)", re.UNICODE)
    s = ' '.join(lst)
    matches = pattern.findall(s)
    return len(matches)

ACCESSORS = { 
        Expression: 'arg',
        Markup: 'options'}

def get_accessor(exp:Expression) -> str:
    return ACCESSORS[type(exp)]

def count_var_refs(lst:list[Expression]) -> int:
    vars = set()
    for obj in lst:
        accessor = get_accessor(obj)
        item = getattr(obj, accessor)
        if isinstance(item, VariableRef):
            vars.add(item.name)
    return len(vars)

def _count_items(lsts: list[list[Any]]) -> int:
    """Collect strings and expressions from a list of lists,
    then compute the total word count."""
    strs, exprs = [], []
    for lst in lsts:
        for obj in lst:
            if isinstance(obj, str):
                strs.extend(obj.split())
            else:
                exprs.append(obj)
    return count_strings(strs) + count_var_refs(exprs)

def _pattern_message_word_count(msg: PatternMessage) -> int:
    return _count_items([msg.pattern])

def _select_message_word_count(msg: SelectMessage) -> int:
    return _count_items(msg.variants.values())

def word_count(message:Message) -> int:
    """
    This function estimates the number of words in a Message.
    
    :message: an instance of Message
    returns an int, representing the estimated word count.
    """
    wc = 0
    if isinstance(message, PatternMessage):
        wc = _pattern_message_word_count(message)
    elif isinstance(message, SelectMessage):
        wc = _select_message_word_count(message)
    else:
        raise(TypeError("Argument must be a Message"))
    return wc