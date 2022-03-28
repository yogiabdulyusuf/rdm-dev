{
    "name" : "Redemption and Point Management - Customer Point Module",
    "version" : "10.0.1.0",
    "author" : "JakC",
    "category" : "Generic Modules/Redemption And Point Management",
    "depends" : ["jakc_redemption","jakc_redemption_customer"],
    "init_xml" : [],
    "data" : [
        "security/ir.model.access.csv",
        "view/jakc_redemption_customer_point_view.xml",
        "view/jakc_redemption_customer_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}