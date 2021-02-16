# -*- coding: utf-8 -*-
{
    'name': "WeightBridge",

    'summary': """
        WeightBridge is integrated with Odoo""",

    'description': """
       WeightBridge is integrated with Odoo using this module
    """,

    'author': "Egymentors",
    'website': "http://www.egymentors.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts','sale_management'],

    # always loaded
    'data': [
        'security/weightbridge.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/sequence.xml',
        'wizard/weight_bridge_line_create_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
