# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged
from odoo import fields
@tagged('-standard','business','rent','demo')
class TestFleetBusinessTrip(TransactionCase):

    def test_user_create_fleet_business_rent(self):
        user = self.env.ref('base.user_demo')
        admin_manager = self.env.ref('base.user_admin')
        fleet_captain = self.env.ref('fleet_business.dep_fleet_captain')
        new_trip = self.env["fleet.business.rent"].with_user(user).create({
            'type_of_transportation': 'plane',
            'tag_ids': [
                self.env.ref('fleet_business.fleet_business_tag_priority').id,
                self.env.ref('fleet_business.fleet_business_tag_business').id,
            ],
            'attending_employee_ids': [
                user.employee_id.id,
                fleet_captain.id,
                self.env.ref('fleet_business.dep_fleet_driver_2').id,
            ],
            'pick_address_id': self.env.company.partner_id.id,
            'return_time': fields.Datetime.add(fields.Datetime.today(), months=1),
            'intent': "a test for trip",
        })
        #$ test correctly created
        res_new_trip = self.env["fleet.business.rent"].browse(new_trip.id)
        self.assertEqual(res_new_trip, new_trip)
        def res_new_trip_curr_deciding_overseer_record(): return self.env["fleet.business.rent"].browse(new_trip.id).curr_deciding_overseer_id

        #$ test first journal and first mail
        new_trip.action_create_first_journal_and_request_first_approval()
        res_new_trip_first_journal = self.env["fleet.business.rent"].browse(new_trip.id).journal_line_ids[0]
        self.assertEqual(res_new_trip_first_journal,new_trip.journal_line_ids[0])

        #$ test overseers approved action, assigning admin and check curr_deciding_overseer
        new_trip.action_approval_manager_approved()
        new_trip.with_user(admin_manager).write({
            'overseer_admin_id': admin_manager.employee_id.id,
        })

        #$ test ticket template actions
        new_trip.with_user(admin_manager).action_prepare_going_and_returning_ticket_template()
        self.assertFalse(new_trip.two_way_ticket_ids)
        res_new_trip_going_ticket_ids = self.env['fleet.business.rent.going.ticket'].search([('fleet_business_rent_id','=',new_trip.id)])
        self.assertEqual(res_new_trip_going_ticket_ids, new_trip.going_ticket_ids)
        res_new_trip_returning_ticket_ids = self.env['fleet.business.rent.returning.ticket'].search([('fleet_business_rent_id','=',new_trip.id)])
        self.assertEqual(res_new_trip_returning_ticket_ids, new_trip.returning_ticket_ids)

        new_trip.with_user(admin_manager).action_prepare_two_way_ticket_template()
        self.assertFalse(new_trip.going_ticket_ids)
        self.assertFalse(new_trip.returning_ticket_ids)
        res_new_trip_two_way_ticket_ids = self.env['fleet.business.rent.two.way.ticket'].search([('fleet_business_rent_id','=',new_trip.id)])
        self.assertEqual(res_new_trip_two_way_ticket_ids, new_trip.two_way_ticket_ids)

        self.assertEqual(res_new_trip_curr_deciding_overseer_record(), new_trip.overseer_admin_id)
        new_trip.action_approval_admin_approved()
        self.assertEqual(res_new_trip_curr_deciding_overseer_record(), new_trip.overseer_creator_id)

        # #$ test final approval
        new_trip.action_approval_creator_approved()
        self.assertFalse(res_new_trip_curr_deciding_overseer_record())
        res_new_trip_state = self.env["fleet.business.rent"].browse(new_trip.id).state
        self.assertEqual(res_new_trip_state, 'approved')

        #$ test automated actions
        new_trip.action_update_state_and_send_mass_mail_reminder('ready')
        new_trip.action_update_state_and_send_mass_mail_reminder('departing')
        #! new_trip.action_update_state_and_send_mass_mail_reminder('returning') make that computed datetime yo
        new_trip.action_update_state_and_send_mass_mail_reminder('late')

        # #$ test returned and finishing actions
        new_trip.with_user(admin_manager).action_update_state_returned()

        print(new_trip.read())