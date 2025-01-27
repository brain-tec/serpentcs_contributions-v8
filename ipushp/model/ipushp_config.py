# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BusinessCategory(models.Model):
    _name = "business.category"
    _description = "Business Category"

    name = fields.Char("Name", required=True)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         'A Business Category with the same name already exists.')
    ]
   


class Relation(models.Model):
    _name = "relation.relation"
    _description = "Employee Relation"

    name = fields.Char("Name")
