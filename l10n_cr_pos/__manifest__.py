# -*- coding: utf-8 -*-
{
    'name': "POS Electrónico",
    'summary': """
        Punto de Venta - Electrónico""",

    'description': """
        Envío a Hacienda de compobantes electrónicos mediante POS.
    """,
    'author': "Jhonny Mack Merino Samillán",
    'company': 'BigCloud',
    'maintainer': 'Jhonny M. / BigCloud',
    'website': "https://www.bigcloud.com",
    'category': 'POS / Envío-electrónico',
    'version': '14.0.3.5',
    'depends': ["l10n_cr_electronic_invoice", "point_of_sale",],
    'data': [
        #'security/ir.model.access.csv',
        'reports/mail_template_pos.xml',
        'data/cron.xml',
        'data/pos_config.xml',
        'data/pos_mail_template.xml',
        'views/pos_js.xml',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
        #'views/pos_report.xml',
        'views/pos_payment_method_views.xml',

    ],
    'qweb': ['static/src/xml/OrderReceipt.xml','static/src/xml/ClientDetailsEdit.xml'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
