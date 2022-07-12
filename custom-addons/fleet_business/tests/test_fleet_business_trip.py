# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged
from odoo import fields
@tagged('-standard','business','trip','demo')
class TestFleetBusinessTrip(TransactionCase):

    def test_user_create_business_trip(self):
        user = self.env.ref('base.user_demo')
        new_trip = self.env["fleet.business.trip"].with_user(user).create({
            'tag_ids': [
                self.env.ref('fleet_business.fleet_business_tag_priority').id,
                self.env.ref('fleet_business.fleet_business_tag_business').id,
            ],
            'vehicle_id': self.env.ref('fleet_business.business_vehicle_1').id,
            'driver_id': self.env.ref('fleet_business.dep_fleet_driver').id,
            'attending_employee_ids': [
                self.env.ref('fleet_business.dep_fleet_captain').id,
                self.env.ref('fleet_business.dep_fleet_driver_2').id,
            ],
            'return_time': fields.Datetime.add(fields.Datetime.today(), months=1),
            'intent': "a test for trip",
            'overseer_admin_id': self.env.ref('fleet_business.dep_management_member_fleet_business').id,
        })

        res_new_trip = self.env["fleet.business.trip"].browse(new_trip.id)
        print('---new_trip---\n',self.env["fleet.business.trip"].browse(new_trip.id).read(),'\n---end_new_trip---')
        self.assertEqual(res_new_trip, new_trip)