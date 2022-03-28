{
    "name" : "Redemption and Point Management - Trans Rule Module",
    "version": "12.0.1.0",
    "author" : "JakC",
    "category" : "Generic Modules/Redemption And Point Management",
    "depends" : ["jakc_redemption","jakc_redemption_customer","jakc_redemption_tenant"],
    "init_xml" : [],
    "data" : [		
        "security/ir.model.access.csv",	      
        "view/jakc_redemption_trans_rule_view.xml",
        "view/jakc_redemption_trans_rule_menu.xml",            
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}