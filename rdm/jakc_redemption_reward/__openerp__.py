{
    "name" : "Redemption and Point Management - Reward Module",
    "version" : "10.0.1.0",
    "author" : "JakC",
    "category" : "Generic Modules/Redemption And Point Management",
    "depends" : ["base_setup","base","jakc_redemption_customer","jakc_redemption_customer_point"],
    "init_xml" : [],
    "data" : [
        "view/jakc_redemption_reward_view.xml",
        "view/jakc_redemption_reward_menu.xml",
        "view/jakc_redemption_customer_view.xml",
        "view/jakc_redemption_reward_config_view.xml",
        "view/jakc_redemption_reward_config_menu.xml",
        "view/jakc_redemption_reward_scheduler.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}