# -*- coding: utf-8 -*-

# Highlight Search Results in the Browser Add-on for Anki
#
# Copyright (C) 2017-2020  Aristotelis P. <https://glutanimate.com/>
# Copyright (C) 2006-2020 Ankitects Pty Ltd and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

from enum import Enum
from typing import Union, List, Tuple, Dict


class QueryLanguageVersion(Enum):
    ANKI2100 = 0
    ANKI2124 = 1


class SearchTokenizer:

    _operators_common: Tuple[str, ...] = ("or", "and", "+")
    _stripped_chars_common: str = '",*;'
    _ignored_values_common: Tuple[str, ...] = ("*", "_", "_*")

    _ignored_tags_common: Tuple[str, ...] = (
        # default query language:
        "added:",
        "deck:",
        "note:",
        "tag:",
        "mid:",
        "nid:",
        "cid:",
        "card:",
        "is:",
        "flag:",
        "rated:",
        "dupe:",
        "prop:",
        # added by add-ons:
        "seen:",
        "rid:",
    )

    _ignored_tags_by_version: Dict[QueryLanguageVersion, Tuple[str, ...]] = {
        QueryLanguageVersion.ANKI2100: tuple(),
        QueryLanguageVersion.ANKI2124: ("re:", "nc:"),
    }

    _quotes_by_version: Dict[QueryLanguageVersion, Tuple[str, ...]] = {
        QueryLanguageVersion.ANKI2100: ('"',),
        QueryLanguageVersion.ANKI2124: ('"', "'"),
    }

    def __init__(
        self,
        query_language_version: QueryLanguageVersion = QueryLanguageVersion.ANKI2124,
    ):
        self._query_language_version = query_language_version
        self._ignored_values = self._ignored_values_common
        self._operators = self._operators_common
        self._stripped_chars = self._stripped_chars_common
        self._ignored_tags = (
            self._ignored_tags_common
            + self._ignored_tags_by_version[query_language_version]
        )
        self._quotes = self._quotes_by_version[query_language_version]

    def tokenize(self, query: str) -> List[str]:
        """
        Tokenize search string

        Based on finder code in Anki versions 2.1.23 and lower
        (anki.find.Finder._tokenize)
        """

        _escape_supported = (
            self._query_language_version.value >= QueryLanguageVersion.ANKI2124.value
        )

        in_quote: Union[bool, str] = False
        in_escape: bool = False
        tokens: List[str] = []
        token: str = ""

        for c in query:
            # quoted text
            if c in self._quotes:
                if in_quote:
                    if c == in_quote and not in_escape:
                        in_quote = False
                    else:
                        token += c
                elif token:
                    # quotes are allowed to start directly after a :
                    if token[-1] == ":":
                        in_quote = c
                    else:
                        token += c
                else:
                    in_quote = c
            # escaped characters
            elif c == "\\" and _escape_supported:
                if in_escape:
                    # escaped "\"
                    token += c
                    in_escape = False
                else:
                    in_escape = True
            # separator (space and ideographic space)
            elif c in (" ", "\u3000"):
                if in_quote:
                    token += c
                elif token:
                    # space marks token finished
                    tokens.append(token)
                    token = ""
            # nesting
            elif c in ("(", ")"):
                if in_quote:
                    token += c
                else:
                    if c == ")" and token:
                        tokens.append(token)
                        token = ""
                    tokens.append(c)
            # negation
            elif c == "-":
                if token:
                    token += c
                elif not tokens or tokens[-1] != "-":
                    tokens.append("-")
            # normal character
            else:
                in_escape = False
                token += c
        # if we finished in a token, add it
        if token:
            tokens.append(token)

        return tokens

    def get_searchable_tokens(self, tokens: List[str]) -> List[str]:
        searchable_tokens: List[str] = []

        for token in tokens:
            if (
                token in self._operators
                or token.startswith("-")
                or token.startswith(self._ignored_tags)
            ):
                continue

            if ":" in token:
                value = token.split(":", 1)[1]
                if not value or value in self._ignored_values:
                    continue
            else:
                value = token

            value = value.strip(self._stripped_chars)

            searchable_tokens.append(value)

        return searchable_tokens
