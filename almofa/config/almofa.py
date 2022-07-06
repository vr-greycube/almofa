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
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "name": "Almofa Net Profit",
                    "description": _("Almofa Net Profit"),
                    "is_query_report": True,
                },
            ],
        },
    ]
    return config
