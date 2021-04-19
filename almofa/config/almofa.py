from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
    config = [
        {
            "label": _("Documents"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Sales Man Visit",
                    "description": _("Sales Man Visit"),
                },
            ],
        },
    ]
    return config
