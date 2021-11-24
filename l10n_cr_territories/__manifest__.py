{
    "name": "L10N CR Territories",  # TODO
    "version": "14.0.0.1.0",  # TODO
    "author": "HomebrewSoft",
    "website": "https://homebrewsoft.dev",  # TODO
    "license": "LGPL-3",
    "depends": [
        'account',
        'l10n_cr',],  # TODO Check
    "data": [  # TODO Check
        # security
        "security/ir.model.access.csv",
        # data
        "data/res.country.county.csv",
        "data/res.country.district.csv",
        "data/res.country.neighborhood.csv",
        "data/res.country.state.csv",
        # reports
        # views
        "views/res_company.xml",
        "views/res_country_county.xml",
        "views/res_country_district.xml",
        "views/res_country_neighborhood.xml",
        "views/res_partner.xml",
    ],
}
