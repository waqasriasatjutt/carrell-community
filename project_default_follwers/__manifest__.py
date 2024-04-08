# Copyright 2021-2022 My GameMates
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Follwers Default all values",
    "summary": "Followers for mail should have all values by default",
    "version": "16.0.1.0.1",
    "category": "Customer Relationship Management",
    "author": "WAQAS RIASAT",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": ["base","mail"],
    "data": [
                    #   'data/mail_message_subtype_data.xml',
                      'views/follow_default.xml',
        'views/follower_defaults_actions.xml',

    ],
}
