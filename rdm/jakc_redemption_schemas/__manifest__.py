{
    "name" : "Redemption and Point Management - Schemas Module",
    "version": "10.0.1.0",
    "author" : "JakC",
    "category" : "Generic Modules/Redemption And Point Management",
    "depends" : ["jakc_redemption","jakc_redemption_customer","jakc_redemption_tenant","jakc_redemption_trans_rule"],
    "init_xml" : [],
    "data" : [
        "security/ir.model.access.csv",
        "view/jakc_redemption_schemas_view.xml",
        "view/jakc_redemption_schemas_menu.xml",
        "view/jakc_redemption_schemas_scheduler.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}