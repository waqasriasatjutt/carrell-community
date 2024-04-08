# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
import itertools

from odoo import api, fields, models, Command


class FollowersInherit(models.Model):
    """ mail_followers holds the data related to the follow mechanism inside
    Odoo. Partners can choose to follow documents (records) of any kind
    that inherits from mail.thread. Following documents allow to receive
    notifications for new messages. A subscription is characterized by:

    :param: res_model: model of the followed objects
    :param: res_id: ID of resource (may be 0 for every objects)
    """
    _inherit = 'mail.followers'

    @api.model
    def default_get(self, fields):
        defaults = super(FollowersInherit, self).default_get(fields)
        # Define your default subtype_ids here
        default_subtype_ids = [(0, 0, {'name': 'Discussions'}),(0, 0, {'name': 'Stage Changed'}),
                                (0, 0, {'name': 'Opportunity Won'}),(0, 0, {'name': 'Opportunity Lost'}),
                                (0, 0, {'name': 'Note'}),(0, 0, {'name': 'Opportunity Restored'}),(0, 0, {'name': 'Activities'})]
        defaults['subtype_ids'] = default_subtype_ids
        return defaults