# -*- coding: utf-8 -*-

# Image Occlusion Enhanced Add-on for Anki
#
# Copyright (C) 2016-2022  Aristotelis P. <https://glutanimate.com/>
# Copyright (C) 2012-2015  Tiago Barroso <tmbb@campus.ul.pt>
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

from .consts import MODULE_ADDON

from aqt import mw
from aqt.editor import Editor
from aqt.reviewer import Reviewer

editor_html = f"""
<link rel="stylesheet" href="/_addons/{MODULE_ADDON}/web/editor.css">
<script src="/_addons/{MODULE_ADDON}/web/editor.js"></script>
"""

reviewer_html = f"""
<script src="/_addons/{MODULE_ADDON}/web/reviewer.js"></script>
"""


def on_webview_will_set_content(web_content, context):
    if isinstance(context, Editor):
        web_content.body += editor_html
    elif isinstance(context, Reviewer):
        web_content.body += reviewer_html


def on_main_window_did_init():
    """Add our custom user styles to the editor HTML
    Need to delay this to avoid interferences with other add-ons that might
    potentially overwrite editor HTML"""
    from aqt.gui_hooks import webview_will_set_content

    webview_will_set_content.append(on_webview_will_set_content)


def setup_webview_injections():
    from aqt.gui_hooks import main_window_did_init

    main_window_did_init.append(on_main_window_did_init)
    mw.addonManager.setWebExports(__name__, r"web.*")
