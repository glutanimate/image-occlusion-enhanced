# -*- coding: utf-8 -*-
####################################################
##                                                ##
##           Image Occlusion Enhanced             ##
##                                                ##
##      Copyright (c) Glutanimate 2016-2019       ##
##       (https://github.com/Glutanimate)         ##
##                                                ##
##         Based on Image Occlusion 2.0           ##
##         Copyright (c) 2012-2015 tmbb           ##
##           (https://github.com/tmbb)            ##
##                                                ##
####################################################

# This source code file takes most of its contents from
# Anki's original 'anki.lang' module with the following
# changes:
# - change location of language files and remove os specific handling
# - get the initialization language from Anki's currently set language
# - use Anki's code and variables whenever possible
# - remove unneeded functions and variables
#
# Modifications were made on 2020-02-23.
# Link to original file at time of creation:
# https://github.com/dae/anki/blob/241b7ea005e2360ea8c1e0a1dd91d8b4dda4bf0e/anki/lang.py

"""
Handle translation.
"""

import os
import gettext

import anki.lang
from aqt import mw

# TODO maybe remove the table and 'mungeCode' once Anki 2.1.16 is released and
#  replace with calls to the API to reduce copied code
# compatibility with old versions
compatMap = {
    "af": "af_ZA",
    "ar": "ar_SA",
    "bg": "bg_BG",
    "ca": "ca_ES",
    "cs": "cs_CZ",
    "da": "da_DK",
    "de": "de_DE",
    "el": "el_GR",
    "en": "en_US",
    "eo": "eo_UY",
    "es": "es_ES",
    "et": "et_EE",
    "eu": "eu_ES",
    "fa": "fa_IR",
    "fi": "fi_FI",
    "fr": "fr_FR",
    "gl": "gl_ES",
    "he": "he_IL",
    "hr": "hr_HR",
    "hu": "hu_HU",
    "hy": "hy_AM",
    "it": "it_IT",
    "ja": "ja_JP",
    "ko": "ko_KR",
    "mn": "mn_MN",
    "ms": "ms_MY",
    "nl": "nl_NL",
    "nb": "nb_NL",
    "no": "nb_NL",
    "oc": "oc_FR",
    "pl": "pl_PL",
    "pt": "pt_PT",
    "ro": "ro_RO",
    "ru": "ru_RU",
    "sk": "sk_SK",
    "sl": "sl_SI",
    "sr": "sr_SP",
    "sv": "sv_SE",
    "th": "th_TH",
    "tr": "tr_TR",
    "uk": "uk_UA",
    "vi": "vi_VN",
}

# global defaults
currentLang = None
currentTranslation = None


def localTranslation():
    "Return the translation local to this thread, or the default."
    return currentTranslation


def _(str):
    return localTranslation().gettext(str)


def ngettext(single, plural, n):
    return localTranslation().ngettext(single, plural, n)


def langDir():
    filedir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(filedir, "locale"))


def setLang(lang):
    lang = mungeCode(lang)
    trans = gettext.translation(
        "anki-image-occlusion-enhanced", langDir(), languages=[lang], fallback=True
    )
    global currentLang, currentTranslation
    currentLang = lang
    currentTranslation = trans


def mungeCode(code):
    code = code.replace("-", "_")
    if code in compatMap:
        code = compatMap[code]

    return code


if not currentTranslation:
    if hasattr(anki.lang, "getLang"):
        # backwards compatibility Anki < 2.1.22
        # (commit 6c9e9eb3300707f534af5b57e45a0cec7ed91401)
        setLang(anki.lang.getLang())
    else:
        setLang(anki.lang.currentLang or mw.pm.meta["defaultLang"] or "en_US")
