# See LICENSE file for full copyright and licensing details.

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    """Inherited the sale order model."""

    _inherit = "sale.order"

    def action_confirm(self):
        """overridden the method to check sale order line having zero unit price."""
        zero_price = [
            x.product_id.name for x in self.order_line if not x.price_unit > 0.0
        ]
        if zero_price and self.env.user.has_group('sale_restrict.group_sales_restrict_user_validation'):
            message = (
                    _("Please specify unit price for the following products:") + "\n"
            )
            message += "\n".join(map(str, zero_price))
            raise UserError(message.rstrip())
        return super(SaleOrder, self).action_confirm()
