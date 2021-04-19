# -*- coding: utf-8 -*-
# Copyright (c) 2021, Greycube and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr
from frappe.model.document import Document
import json


class SalesManVisit(Document):
    pass


@frappe.whitelist()
def get_client_location(party):
    location = frappe.db.get_value("Customer", party, "client_location_cf")
    if location:
        for loc in json.loads(location).get("features", []):
            return ",".join(
                [cstr(d) for d in loc.get("geometry", {}).get("coordinates")]
            )
    return ""
