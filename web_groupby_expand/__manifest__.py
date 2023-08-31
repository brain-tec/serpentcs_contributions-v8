##############################################################################
# Copyright (c) 2021 braintec AG (https://braintec.com)
# All Rights Reserved
#
# Licensed under the AGPL-3.0 (http://www.gnu.org/licenses/agpl.html)
# See LICENSE file for full licensing details.
##############################################################################

{
    "name": "Web GroupBy Expand",
    "version": "15.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "category": "Web",
    "license": "AGPL-3",
    'summary': 'Expand all groups on single click',
    "depends": [
        "web",
    ],
    "data": [
    ],
    "assets": {
        "web.assets_backend": [
            "web_groupby_expand/static/src/js/web_groups_expand.js",
        ],
        "web.assets_qweb": [
            "web_groupby_expand/static/src/xml/web_groups_expand.xml",
        ],
    },
    "installable": True,
}
