# -*- coding: utf-8 -*-
{
    'name': "Warehouse Rental Management",

    'summary': """""",

    'description': """
    """,

    'author': "AbdulRahman Mongy",
    'website': "",

    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'account', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/wro_views.xml',
        'views/warehouse_stage.xml',
        'views/product.xml',
        'views/sale_order.xml',
    ],

    'installable': True,
    'application': True,
}
