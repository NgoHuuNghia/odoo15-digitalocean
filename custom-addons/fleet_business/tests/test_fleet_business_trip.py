# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged, new_test_user
from odoo import fields

@tagged('business','trip')
class TestFleetBusinessTrip(TransactionCase):

    def test_user_create_business_trip(self):
        user = new_test_user(self.env, "test base user", groups="base.group_user")
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
        })

        res_new_trip = self.env["fleet.business.trip"].browse(new_trip.id)
        self.assertEqual(res_new_trip, new_trip)