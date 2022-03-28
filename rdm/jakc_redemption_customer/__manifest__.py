{
    "name" : "Redemption and Point Management - Customer Module",
    "version": "10.0.1.0",
    "author" : "JakC",
    "category" : "Generic Modules/Redemption And Point Management",
    "depends" : ["jakc_redemption","mass_mailing"],
    "init_xml" : [],
    "data" : [	
        "security/ir.model.access.csv",
        "view/jakc_redemption_customer_view.xml",
        "view/jakc_redemption_customer_config_view.xml",
        "view/jakc_redemption_customer_menu.xml",
        "wizard/wizard_customer_change_password_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}