"""
This type stub file was generated by pyright.
"""

import json
from os import path
from typing import Dict, List
from .conversion import char_to_unified, unified_to_char
from .emoji_char import EmojiChar
from .replacement import get_emoji_regex, replace_colons
from .search import all_doublebyte, find_by_name, find_by_shortname

emoji_short_names: Dict[str, EmojiChar] = ...
__all__ = ["unified_to_char", "char_to_unified", "EmojiChar", "replace_colons", "get_emoji_regex", "all_doublebyte", "find_by_shortname", "find_by_name", "emoji_data", "emoji_short_names"]
