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
from icu import BreakIterator, Locale

def count_strings(str_list: list[str], locale: str) -> list[str]:
    text = ' '.join(str_list)
    bi = BreakIterator.createWordInstance(Locale(locale))
    bi.setText(text)
    tokens = []
    start = bi.first()
    for end in bi:
        chunk = text[start:end]
        if chunk.strip() and any(c.isalnum() for c in chunk):
            tokens.append(chunk)
        start = end
    return len(tokens)

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

def _count_items(lsts: list[list[Any]], locale:str) -> int:
    """Collect strings and expressions from a list of lists,
    then compute the total word count."""
    strs, exprs = [], []
    for lst in lsts:
        for obj in lst:
            if isinstance(obj, str):
                strs.extend(obj.split())
            else:
                exprs.append(obj)
    return count_strings(strs, locale) + count_var_refs(exprs)

def _pattern_message_word_count(msg: PatternMessage, locale:str) -> int:
    return _count_items([msg.pattern], locale)

def _select_message_word_count(msg: SelectMessage, locale:str) -> int:
    return _count_items(msg.variants.values(), locale)

def word_count(message:Message, locale:str="en") -> int:
    """
    This function estimates the number of words in a Message.
    
    :message: an instance of Message
    returns an int, representing the estimated word count.
    """
    wc = 0
    if isinstance(message, PatternMessage):
        wc = _pattern_message_word_count(message, locale)
    elif isinstance(message, SelectMessage):
        wc = _select_message_word_count(message, locale)
    else:
        raise(TypeError("Argument must be a Message"))
    return wc