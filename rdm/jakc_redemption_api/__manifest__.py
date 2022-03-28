{
    "name" : "Redemption and Point Management - API Module",
    "version": "12.0.1.0",
    "author" : "WEHA",
    "category" : "Generic Modules/Redemption And Point Management",
    "depends" : ["jakc_redemption",
                 "jakc_redemption_customer"],
    "data" : [ 
        "data/ir_config_param.xml",
        "views/res_company_api_settings_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}