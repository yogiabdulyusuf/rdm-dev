{
    "name" : "Redemption and Point Management - Draw Module",
    "version" : "10.0.1.0",
    "author" : "Jakc",
    "category" : "Generic Modules/Redemption And Point Management",
    "depends" : ["jakc_redemption","jakc_redemption_schemas"],
    "init_xml" : [],
    "data" : [		
        "security/ir.model.access.csv",
       "view/jakc_redemption_draw_view.xml",
       "view/jakc_redemption_schemas_view.xml",
       "view/jakc_redemption_draw_menu.xml",                 
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}