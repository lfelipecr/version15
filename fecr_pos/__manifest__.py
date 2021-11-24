{
    "name": "FECR POS",
    "version": "14.0.1.0.0",
    "author": "Homebrewsoft",
    "website": "https://homebrewsoft.dev",
    "license": "LGPL-3",
    "price": 500,
    "currency": "USD",
    "depends": [
        "l10n_cr_electronic_invoice",  # https://gitlab.com/HomebrewSoft/fecr/fecr
        "point_of_sale",
    ],
    "data": [
        "data/data.xml",
        "data/pos_config.xml",
        "views/electronic_invoice_views.xml",
        "views/pos_templates.xml",
    ],
    "qweb": [
        "static/src/xml/pos.xml",
    ],
    "autoinstall": True,
}
