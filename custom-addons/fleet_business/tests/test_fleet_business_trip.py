# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged
from odoo import fields
@tagged('-standard','business','trip','demo')
class TestFleetBusinessTrip(TransactionCase):

    def test_user_create_fleet_business_trip(self):
        user = self.env.ref('base.user_demo')
        admin_manager = self.env.ref('base.user_admin')
        fleet_captain = self.env.ref('fleet_business.dep_fleet_captain')
        new_trip = self.env["fleet.business.trip"].with_user(user).create({
            'tag_ids': [
                (4, self.env.ref('fleet_business.fleet_business_tag_priority').id),
                (4, self.env.ref('fleet_business.fleet_business_tag_business').id),
            ],
            'vehicle_id': self.env.ref('fleet_business.business_vehicle_1').id,
            'driver_id': self.env.ref('fleet_business.dep_fleet_driver').id,
            'attending_employee_ids': [
                (4, user.employee_id.id),
                (4, fleet_captain.id),
                (4, self.env.ref('fleet_business.dep_fleet_driver_2').id),
            ],
            'pick_address_id': self.env.company.partner_id.id,
            'return_time': fields.Datetime.add(fields.Datetime.today(), months=1),
            'intent': "a test for trip",
        })
        #$ test correctly created
        res_new_trip = self.env["fleet.business.trip"].browse(new_trip.id)
        self.assertEqual(res_new_trip, new_trip)
        def res_new_trip_curr_deciding_overseer_record(): return self.env["fleet.business.trip"].browse(new_trip.id).curr_deciding_overseer_id

        #$ test first journal and first mail
        new_trip.action_create_first_journal_and_request_first_approval()
        res_new_trip_first_journal = self.env["fleet.business.trip"].browse(new_trip.id).journal_line_ids[0]
        self.assertEqual(res_new_trip_first_journal,new_trip.journal_line_ids[0])

        #$ test overseers approved action, assigning admin and check curr_deciding_overseer
        new_trip.action_approval_manager_approved()
        new_trip.with_user(admin_manager).write({
            'overseer_admin_id': admin_manager.employee_id.id,
        })
        self.assertEqual(res_new_trip_curr_deciding_overseer_record(), new_trip.overseer_admin_id)
        new_trip.action_approval_admin_approved()
        self.assertEqual(res_new_trip_curr_deciding_overseer_record(), new_trip.overseer_fleet_id)
        new_trip.action_approval_fleet_approved()
        self.assertEqual(res_new_trip_curr_deciding_overseer_record(), new_trip.overseer_creator_id)

        #$ test final approval
        new_trip.action_approval_creator_approved()
        self.assertFalse(res_new_trip_curr_deciding_overseer_record())
        res_new_trip_state = self.env["fleet.business.trip"].browse(new_trip.id).state
        self.assertEqual(res_new_trip_state, 'approved')

        #$ test automated actions
        new_trip.action_update_state_and_send_mass_mail_reminder('ready')
        new_trip.action_update_state_and_send_mass_mail_reminder('departing')
        #! new_trip.action_update_state_and_send_mass_mail_reminder('returning') make that computed datetime yo
        new_trip.action_update_state_and_send_mass_mail_reminder('late')

        #$ test returned and finishing actions
        new_trip.with_user(admin_manager).action_update_state_returned()
        new_trip.with_user(user).action_rate_driver()