{
    "name": "FECR",
    "version": "14.0.7.13",
    "category": "Accounting",
    "summary": "Factura electrónica para Costa Rica",
    "author": "XALACHI",
    "website": "https://github.com/xalachi/fecr",
    "license": "LGPL-3",
    "price": 500,
    "currency": "USD",
    "depends": [
        "account",
        "base_iban",
        "l10n_cr",
        "l10n_cr_accounting",
        "l10n_cr_cabys",
        "l10n_cr_currency_exchange",
        "l10n_cr_territories",
        "uom",
        "sale",
        "fetchmail"
    ],
    "data": [
        # security
        "security/ir.model.access.csv",
        "security/groups.xml",
        #"security/rule.xml",
        # templates
        # data
        "data/decimal_precision_einv.xml",
        "data/aut_ex_data.xml",
        "data/reference_document_data.xml",
        "data/config_settings.xml",
        "data/currency_data.xml",
        "data/identification_type_data.xml",
        "data/ir_cron_data.xml",
        "data/product_category_data.xml",
        "data/sequence.xml",  # Special case, this calls a function
        "data/account_journal.xml",
        "data/product_data.xml",
        "data/res.currency.xml",
        "data/uom_category.xml",
        "data/uom_data.xml",
        # reports
        "reports/account_move.xml",
        # views
        "views/account_move_views.xml",
        "views/account_journal_views.xml",
        "views/identification_type_views.xml",
        "views/res_company_views.xml",
        "views/account_invoice_import_config_views.xml",
        "views/account_invoice_import_config_extend_views.xml", #Nuevo
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/resolution_views.xml",
        "views/uom_views.xml",
        "views/res_partner_exonerated_views.xml",
        "views/fetchmail_views.xml",

        #Vistas para exoneración
        "views/sale_views.xml",
        "views/account_move_exoneration.xml",
        # wizard
        "wizard/account_move_reversal_view.xml",
        "views/account_tax_views.xml",  # Nuevo 18-10-2021
        "wizard/account_report_iva_wizard.xml",  # Nuevo 14-10-2021
    ],
    "external_dependencies": {
        "python": [
            "cryptography",
            "jsonschema",
            "OpenSSL",
            "phonenumbers",
            "PyPDF2",
            "suds",
            "xades",
            "xmlsig",
        ],
    },
    "description": [
        "static/description/description/screenshot.jpg",
        "static/description/description/config.jpg",
    ],
}
