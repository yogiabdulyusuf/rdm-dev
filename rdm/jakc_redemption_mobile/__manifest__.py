{
    "name" : "Redemption and Point Management - Mobile Extended",
    "version" : "12.0.1.0",
    "author" : "WEHA Consultant",
    "category" : "Generic Modules/Redemption And Point Management",
    "depends" : ["base_setup",
                 "base",
                 "jakc_redemption",
                 "jakc_redemption_customer",
                 "jakc_redemption_tenant"],
    "init_xml" : [],
    "data" : [
        "security/ir.model.access.csv",
        "views/jakc_redemption_mobile_menu.xml",
        "views/jakc_redemption_mobile_banner_view.xml",
        "views/jakc_redemption_mobile_event_view.xml",
        "views/jakc_redemption_mobile_promo_view.xml",
        

    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}