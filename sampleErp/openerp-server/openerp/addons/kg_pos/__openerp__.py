##############################################################################


{
    'name': 'Canteen Management',
    'version': '1.0.1',
    'category': 'Point Of Sale',
    'sequence': 6,
    'summary': 'Touchscreen Interface for Shops',
    'description': """
Quick and Easy sale process
===========================

This module allows you to manage your shop sales very easily with a fully web based touchscreen interface.
It is compatible with all PC tablets and the iPad, offering multiple payment methods. 

Product selection can be done in several ways: 

* Using a barcode reader
* Browsing through categories of products or via a text search.

Main Features
-------------
* Fast encoding of the sale
* Choose one payment method (the quick way) or split the payment between several payment methods
* Computation of the amount of money to return
* Create and confirm the picking list automatically
* Allows the user to create an invoice automatically
* Refund previous sales
    """,
    'author': 'OpenERP SA',
    'images': ['images/cash_registers.jpeg', 'images/pos_analysis.jpeg','images/register_analysis.jpeg','images/sale_order_pos.jpeg','images/product_pos.jpeg'],
    'depends': ['point_of_sale'],
    'installable': True,
    'application': True,
    'auto_install': False,
}


