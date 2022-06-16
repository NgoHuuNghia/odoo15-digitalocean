# See LICENSE file for full copyright and licensing details.
"""Multi Image model."""

import logging
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """product model."""

    _inherit = 'product.product'

    in_active_part = fields.Boolean('In-Active Part?')
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',
                                      string='Vehicle Make')


class FleetOperations(models.Model):
    """Fleet Operations model."""

    _inherit = 'fleet.vehicle'
    _order = 'id desc'
    _rec_name = 'name'

    def copy(self, default=None):
        """Overridden copy method."""
        if not default:
            default = {}
        if self.state == 'write-off':
            raise UserError(_('You can\'t duplicate this record '
                              'because it is already write-off'))
        return super(FleetOperations, self).copy(default=default)

    @api.model
    def vehicle_service_reminder_send_mail(self):
        """Method to Send Next Service Reminder to vehicle driver."""
        fleet_vehicles = self.env['fleet.vehicle'].search([
            ('next_service_date', '=', fields.Date.today())])
        for vehicle in fleet_vehicles:
            if vehicle.driver_id and vehicle.driver_id.email:
                res = self.env.ref('fleet_operations.fleet_email_template')
                res.send_mail(vehicle.id, force_send=True)
        return True

    def update_history(self):
        """Method use update color engine,battery and tire history."""
        mod_obj = self.env['ir.model.data']
        wizard_view = ""
        res_model = ""
        view_name = ""
        context = self.env.context
        context = dict(context)
        if context.get('history', False):
            if context.get("history", False) == "color":
                wizard_view = "update_color_info_form_view"
                res_model = "update.color.info"
                view_name = "Update Color Info"
            elif context.get("history", False) == "engine":
                wizard_view = "update_engine_info_form_view"
                res_model = "update.engine.info"
                view_name = "Update Engine Info"
            elif context.get('history', False) == 'vin':
                wizard_view = "update_vin_info_form_view"
                res_model = "update.vin.info"
                view_name = "Update Vin Info"
            elif context.get('history', False) == 'tire':
                wizard_view = "update_tire_info_form_view"
                res_model = "update.tire.info"
                view_name = "Update Tire Info"
            elif context.get('history', False) == 'battery':
                wizard_view = "update_battery_info_form_view"
                res_model = "update.battery.info"
                view_name = "Update Battery Info"

        model_data_ids = mod_obj.search([('model', '=', 'ir.ui.view'),
                                         ('name', '=', wizard_view)])
        resource_id = model_data_ids.read(['res_id'])[0]['res_id']
        context.update({'vehicle_ids': self._ids})
        # self.env.args = cr, uid, misc.frozendict(context)
        return {
            'name': view_name,
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': res_model,
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def set_released_state(self):
        """Method to set released state."""
        for vehicle in self:
            if vehicle.state == 'complete':
                vehicle.write({'state': 'released',
                               'last_change_status_date': fields.Date.today(),
                               'released_date': fields.Date.today()})
            else:
                raise UserError(_('Vehicle status will only set to released '
                                  'if it is in completed state.'))
        return True

    def name_get(self):
        """
        Method will be called when you view an M2O field in a form.

        And return name whatever we want to search.
        """
        if not len(self._ids):
            return []
        res = []
        for vehicle in self:
            vehicle_unique_id = vehicle.name or ""
            vehicle_unique_id += "-"
            vehicle_unique_id += vehicle.model_id and \
                                 vehicle.model_id.name or ""
            res.append((vehicle['id'], vehicle_unique_id))
        return res

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        """Overwritten this method for the bypass base domain."""
        vehicle_ids = self.search(args, limit=limit)
        return vehicle_ids.name_get()

    def return_action_too_open(self):
        """
        The xml view specified in xml_id.

        For the current vehicle.
        """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']. \
                for_xml_id('fleet_operations', xml_id)
            res.update(
                context=dict(self.env.context,
                             default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False

    @api.constrains('tire_issuance_date', 'battery_issuance_date')
    def check_tire_issuance_date(self):
        """Method to check tire issuance date."""
        for vehicle in self:
            if vehicle.tire_issuance_date and vehicle.battery_issuance_date:
                if vehicle.battery_issuance_date < \
                        vehicle.acquisition_date and \
                        vehicle.tire_issuance_date < vehicle.acquisition_date:
                    raise ValidationError(
                        _('Tire Issuance Date And Battery Issuance Date Should'
                          ' Be Greater Than Registration Date.'))
            if vehicle.tire_issuance_date and \
                    vehicle.tire_issuance_date < vehicle.acquisition_date:
                raise ValidationError(_('Tire Issuance Date Should Be '
                                        'Greater Than Registration Date.'))
            if vehicle.battery_issuance_date and \
                    vehicle.battery_issuance_date < vehicle.acquisition_date:
                raise ValidationError(_('Battery Issuance Date Should Be '
                                        'Greater Than Registration Date.'))

    @api.constrains('warranty_period')
    def check_warranty_date(self):
        """Method to check warranty date."""
        for vehicle in self:
            if vehicle.warranty_period and \
                    vehicle.warranty_period < vehicle.acquisition_date:
                raise ValidationError(_('Warranty Period Should Be '
                                        'Greater Than Registration Date.'))

    @api.constrains('driver_id')
    def check_duplicate_driver(self):
        for vehicle in self:
            if vehicle.driver_id and self.search_count([
                ('driver_id', '=', vehicle.driver_id.id),
                ('id', '!=',vehicle.id),
                ('state', '!=', 'write-off')
            ]) > 1:
                raise ValidationError(_(
                    "Driver can be allocated to one vehicle only!"
                ))

    @api.constrains('date_sold', 'acquisition_date')
    def check_sold_date(self):
        """Method to check sold date."""
        for vehicle in self:
            if vehicle.acquisition_date and vehicle.date_sold:
                if vehicle.date_sold < vehicle.acquisition_date:
                    raise ValidationError(_('Sold Date Should Be '
                                            'Greater Than Registration Date.'))

    @api.constrains('date_sold', 'transfer_date')
    def check_transfer_date(self):
        """Method to check transfer date."""
        for vehicle in self:
            if vehicle.transfer_date and vehicle.date_sold:
                if vehicle.transfer_date < vehicle.date_sold:
                    raise ValidationError(_('Transfer Date Should Be '
                                            'Greater Than Sold Date.'))

    @api.constrains('start_date_insurance', 'end_date_insurance')
    def check_insurance_end_date(self):
        """Method to check insurance date."""
        for vehicle in self:
            if vehicle.start_date_insurance and vehicle.end_date_insurance:
                if vehicle.end_date_insurance < vehicle.start_date_insurance:
                    raise ValidationError(_('Insurance end date should be '
                                            'greater than start date.'))

    @api.constrains('start_date_insurance', 'acquisition_date')
    def check_insurance_start_date(self):
        """Method to check insurance start date."""
        for vehicle in self:
            if vehicle.start_date_insurance and vehicle.acquisition_date:
                if vehicle.start_date_insurance < vehicle.acquisition_date:
                    raise ValidationError(_('Insurance start date should be '
                                            'greater than registration date.'))

    def _get_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search([
                ('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search([
                ('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if record.odometer < vehicle_odometer.value:
                raise UserError(
                    _('You can\'t enter odometer less than previous '
                      'odometer %s !') % vehicle_odometer.value)
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date,
                        'vehicle_id': record.id}
                fleet_vehicle_odometer_obj.create(data)

    @api.onchange('f_brand_id')
    def _onchange_brand(self):
        if self.f_brand_id:
            self.image_128 = self.f_brand_id.image_128
        else:
            self.image_128 = False

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for model in self:
            if model.model_id:
                model.model_year = model.model_id.model_year or 0
                model.transmission = model.model_id.transmission or False
                model.seats = model.model_id.seats or 0
                model.doors = model.model_id.doors or 0
                model.color = model.model_id.color or ""
                model.trailer_hook = model.model_id.trailer_hook or 0
                model.fuel_type = model.model_id.default_fuel_type or False
                model.co2 = model.model_id.default_co2 or 0.0
                model.co2_standard = model.model_id.co2_standard or ""
                model.power = model.model_id.power or 0
                model.horsepower = model.model_id.horsepower or 0
                model.horsepower_tax = model.horsepower_tax or 0.0



    @api.depends('model_id', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            if record.model_id and record.model_id.brand_id:
                lic_plate = record.license_plate
                if not record.license_plate:
                    lic_plate = ''
                record.name = \
                    record.model_id.brand_id.name + '/' + \
                    record.model_id.name + '/' + lic_plate

    name = fields.Char(compute="_compute_vehicle_name", string="Vehicle-ID",
                       store=True)
    odometer_check = fields.Boolean('Odometer Change', default=True)
    fuel_qty = fields.Char(string='Fuel Quality')
    oil_name = fields.Char(string='Oil Name')
    oil_capacity = fields.Char(string='Oil Capacity')
    fleet_id = fields.Integer(string='Fleet ID',
                              help="Take this field for data migration")
    f_brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Make')
    model_no = fields.Char(string='Model No', translate=True)
    license_plate = fields.Char(string='License Plate',
                                translate=True, size=32,
                                help='License plate number of the vehicle.\
                                (ie: plate number for a vehicle)')
    active = fields.Boolean(string='Active', default=True)
    dealer_id = fields.Many2one('res.partner', string='Dealer')
    mileage = fields.Integer(string='Mileage(K/H)')
    description = fields.Text(string='About Vehicle', translate=True)
    engine_size = fields.Char(string='Engine Size', size=16)
    cylinders = fields.Integer(string='No of Cylinders')
    front_tire_size = fields.Float(string='Front Tire Size')
    front_tire_pressure = fields.Integer(string='Front Tire Pressure')
    rear_tire_size = fields.Float(string='Rear Tire Size')
    rear_tire_pressure = fields.Integer(string='Rear Tire Pressure')
    last_service_date = fields.Date(string='Last Service', readonly=True)
    next_service_date = fields.Date(string='Next Service', readonly=True)
    last_odometer = fields.Float(string='Last Service Odometer')
    last_odometer_unit = fields.Selection([('kilometers', 'Kilometers'),
                                           ('miles', 'Miles')],
                                          string='Last Odometer Unit',
                                          help='Unit of the odometer ')
    due_odometer = fields.Float(string='Next Service Odometer', readonly=True)
    due_odometer_unit = fields.Selection([('kilometers', 'Kilometers'),
                                          ('miles', 'Miles')],
                                         string='Due Odometer Units',
                                         help='Unit of the odometer ')
    left_wiper_blade = fields.Char(string='Wiper Blade(L)', size=8)
    right_wiper_blade = fields.Char(string='Wiper Blade(R)', size=8)
    rr_wiper_blade = fields.Char(string='Wiper Blade(RR)', size=8)
    vehicle_length = fields.Integer(string='Length(mm)')
    vehicle_width = fields.Integer(string='Width(mm)')
    vehicle_height = fields.Integer(string='Height(mm)')
    fuel_capacity = fields.Float(string='Fuel Capacity')
    date_sold = fields.Date(string='Date Sold')
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    transfer_date = fields.Date(string='Transfer Date')
    monthly_deprication = fields.Float(string='Deprication(Monthly)')
    resale_value = fields.Float(string='Current value')
    salvage_value = fields.Float(string='Salvage Value')
    warranty_period = fields.Date(string='Warranty Upto')
    insurance_company_id = fields.Many2one('res.partner',
                                           string='Insurance Company',
                                           domain=[('insurance', '=', True)])
    insurance_type_id = fields.Many2one('insurance.type',
                                        string='Insurance Type')
    policy_number = fields.Char(string='Policy Number', size=32)
    payment = fields.Float(string='Payment')
    start_date_insurance = fields.Date(string='Start Date')
    end_date_insurance = fields.Date(string='End Date')
    payment_deduction = fields.Float(string='Deduction')
    fleet_attach_ids = fields.One2many('ir.attachment', 'attachment_id',
                                       string='Fleet Attachments')
    sale_purchase_attach_ids = fields.One2many('ir.attachment',
                                               'attachment_id_2',
                                               string='Attachments')
    odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer',
                            string='Last Odometer',
                            help='Odometer measure of the vehicle at the \
                                moment of this log')
    vehical_color_id = fields.Many2one('color.color', string='Vehicle Color')
    vehicle_location_id = fields.Many2one('res.country.state',
                                          string='Registration State')
    vehical_division_id = fields.Many2one('vehicle.divison', string='Division')
    driver_id = fields.Many2one('res.partner', 'Driver')
    driver_identification_no = fields.Char(string='Driver ID', size=64)
    driver_contact_no = fields.Char(string='Driver Contact Number', size=64)
    main_type = fields.Selection([('vehicle', 'Vehicle'),
                                  ('non-vehicle', 'Non-Vehicle')],
                                 default='vehicle', string='Main Type')
    vechical_type_id = fields.Many2one('vehicle.type', string='Vechical Type')
    engine_no = fields.Char(string='Engine No', size=64)
    multi_images = fields.Many2many('ir.attachment',
                                    'fleet_vehicle_attachment_rel',
                                    'vehicle_id',
                                    'attachment_id', string='Multi Images')
    state = fields.Selection([('inspection', 'Draft'),
                              ('in_progress', 'In Service'),
                              ('contract', 'On Contract'),
                              ('rent', 'On Rent'), ('complete', 'Completed'),
                              ('released', 'Released'),
                              ('write-off', 'Write-Off')],
                             string='Vehicle State', default='inspection')
    is_id_generated = fields.Boolean(string='Is Id Generated?', default=False)
    increment_odometer = fields.Float(string='Next Increment Odometer')
    last_change_status_date = fields.Date(string='Last Status Changed Date',
                                          readonly=True)
    pending_repair_type_ids = fields.One2many('pending.repair.type',
                                              'vehicle_rep_type_id',
                                              string='Pending Repair Types',
                                              readonly=True)
    released_date = fields.Date(string='Released Date', readonly=True)
    tire_size = fields.Char(string='Tire Size', size=64)
    tire_srno = fields.Char(string='Tire S/N', size=64)
    tire_issuance_date = fields.Date(string='Tire Issuance Date')
    battery_size = fields.Char(string='Battery Size', size=64)
    battery_srno = fields.Char(string='Battery S/N', size=64)
    battery_issuance_date = fields.Date(string='Battery Issuance Date')
    color_history_ids = fields.One2many('color.history', 'vehicle_id',
                                        string="Color History", readonly=True)
    engine_history_ids = fields.One2many('engine.history', 'vehicle_id',
                                         string="Engine History",
                                         readonly=True)
    vin_history_ids = fields.One2many('vin.history', 'vehicle_id',
                                      string="Vin History", readonly=True)
    tire_history_ids = fields.One2many('tire.history', 'vehicle_id',
                                       string="Tire History", readonly=True)
    battery_history_ids = fields.One2many('battery.history', 'vehicle_id',
                                          string="Battrey History",
                                          readonly=True)
    is_color_set = fields.Boolean(string='Is Color Set?')
    is_engine_set = fields.Boolean(string='Is Engine Set')
    is_vin_set = fields.Boolean(string='Is Vin Set?')
    is_tire_size_set = fields.Boolean(string='Is Tire Size set?')
    is_tire_srno_set = fields.Boolean(string='Is Tire Srno set?')
    is_tire_issue_set = fields.Boolean(string='Is Tire Issue set?')
    is_battery_size_set = fields.Boolean(string='Is battery Size set?')
    is_battery_srno_set = fields.Boolean(string='Is battery Srno set?')
    is_battery_issue_set = fields.Boolean(string='Is battery Issue set?')
    last_service_by_id = fields.Many2one('res.partner',
                                         string="Last Service By")
    work_order_ids = fields.One2many('fleet.vehicle.log.services',
                                     'vehicle_id', string='Service Order')
    reg_id = fields.Many2one('res.users', string='Registered By')
    vehicle_owner = fields.Many2one('res.users', string='Vehicle Owner')
    updated_by = fields.Many2one('res.users', string='Updated By')
    updated_date = fields.Date(string='Updated date')
    work_order_close = fields.Boolean(string='Work Order Close', default=True)
    fmp_id_editable = fields.Boolean(string='Vehicle ID Editable?')

    _sql_constraints = [('vehilce_unique', 'unique(vin_sn)',
                         'The vehicle is already exist with this vin no.!'),
                        ('fmp_unique', 'unique(name)',
                         'The vehicle is already exist with this Vehicle ID!')]

    income_acc_id = fields.Many2one("account.account",
                                    string="Income Account")
    expence_acc_id = fields.Many2one("account.account",
                                     string="Expense Account")

    @api.model
    def default_get(self, fields):
        """Method to default get."""
        res = super(FleetOperations, self).default_get(fields)
        res['acquisition_date'] = date.today().strftime('%Y-%m-%d')
        return res

    @api.model
    def create(self, vals):
        """Create method override."""
        if not vals.get('model_id', False):
            raise UserError(_('Model is not selected for this vehicle!'))
        vals.update({'fmp_id_editable': True})
        seq = self.env['ir.sequence'].next_by_code('fleet.vehicle')
        vals.update({'name': seq})
        if self._uid:
            vals.update({'reg_id': self._uid})
        if not vals.get('acquisition_date', False):
            vals.update({'acquisition_date': fields.Date.today()})
        if not vals.get('last_change_status_date', False):
            vals.update({'last_change_status_date': fields.Date.today()})

        # checking once vin, color and engine number will be set than field
        # automatically become readonly.

        if vals.get('odometer_unit'):
            vals.update({'odometer_check': False})
        if vals.get('vin_sn', False):
            vals.update({'is_vin_set': True})
        if vals.get('vehical_color_id', False):
            vals.update({'is_color_set': True})
        if vals.get('engine_no', False):
            vals.update({'is_engine_set': True})
        if vals.get('tire_size', False):
            vals.update({'is_tire_size_set': True})
        if vals.get('tire_srno', False):
            vals.update({'is_tire_srno_set': True})
        if vals.get('tire_issuance_date', False):
            vals.update({'is_tire_issue_set': True})

        if vals.get('battery_size', False):
            vals.update({'is_battery_size_set': True})
        if vals.get('battery_srno', False):
            vals.update({'is_battery_srno_set': True})
        if vals.get('battery_issuance_date', False):
            vals.update({'is_battery_issue_set': True})

        return super(FleetOperations, self).create(vals)

    def write(self, vals):
        """
        Function write an entry in the open chatter whenever.

        we change important information.

        on the vehicle like the model, the drive, the state of the vehicle.

        or its license plate.
        """
        vals.update({'fmp_id_editable': True})
        if self._uid:
            vals.update({'updated_by': self.env.user.id})
            vals.update({'updated_date': fields.Date.today()})

        if vals.get('tire_size', False):
            vals.update({'is_tire_size_set': True})
        if vals.get('tire_srno', False):
            vals.update({'is_tire_srno_set': True})
        if vals.get('tire_issuance_date', False):
            vals.update({'is_tire_issue_set': True})

        if vals.get('battery_size', False):
            vals.update({'is_battery_size_set': True})
        if vals.get('battery_srno', False):
            vals.update({'is_battery_srno_set': True})
        if vals.get('battery_issuance_date', False):
            vals.update({'is_battery_issue_set': True})

        return super(FleetOperations, self).write(vals)

    @api.onchange('driver_id')
    def get_driver_id_no(self):
        """Method to get driver id no."""
        if self.driver_id:
            driver = self.driver_id
            self.driver_identification_no = driver.d_id or ''
            self.driver_contact_no = driver.mobile
        else:
            self.driver_identification_no = ''
            self.driver_contact_no = ''


class ColorHistory(models.Model):
    """Model color history."""

    _name = 'color.history'
    _description = 'Color History for Vehicle'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    previous_color_id = fields.Many2one('color.color', string="Previous Color")
    current_color_id = fields.Many2one('color.color', string="New Color")
    changed_date = fields.Date(string='Change Date')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')


class EngineHistory(models.Model):
    """Model Engine History."""

    _name = 'engine.history'
    _description = 'Engine History for Vehicle'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    previous_engine_no = fields.Char(string='Previous Engine No')
    new_engine_no = fields.Char(string='New Engine No')
    changed_date = fields.Date(string='Change Date')
    note = fields.Text('Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')


class VinHistory(models.Model):
    """Model Vin History."""

    _name = 'vin.history'
    _description = 'Vin History'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    previous_vin_no = fields.Char(string='Previous Vin No', translate=True)
    new_vin_no = fields.Char(string='New Vin No', translate=True)
    changed_date = fields.Date(string='Change Date')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')


class TireHistory(models.Model):
    """Model Tire History."""

    _name = 'tire.history'
    _description = 'Tire History for Vehicle'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    previous_tire_size = fields.Char(string='Previous Tire Size', size=124,
                                     translate=True)
    new_tire_size = fields.Char(string="New Tire Size", size=124,
                                translate=True)
    previous_tire_sn = fields.Char(string='Previous Tire Serial', size=124,
                                   translate=True)
    new_tire_sn = fields.Char(string="New Tire Serial", size=124)
    previous_tire_issue_date = fields.Date(
        string='Previous Tire Issuance Date')
    new_tire_issue_date = fields.Date(string='New Tire Issuance Date')
    changed_date = fields.Date(string='Change Date')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')


class BatteryHistory(models.Model):
    """Model Battery History."""

    _name = 'battery.history'
    _description = 'Battery History for Vehicle'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    previous_battery_size = fields.Char(string='Previous Battery Size',
                                        size=124)
    new_battery_size = fields.Char(string="New Battery Size", size=124)
    previous_battery_sn = fields.Char(string='Previous Battery Serial',
                                      size=124)
    new_battery_sn = fields.Char(string="New Battery Serial", size=124)
    previous_battery_issue_date = fields.Date(
        string='Previous Battery Issuance Date')
    new_battery_issue_date = fields.Date(string='New Battery Issuance Date')
    changed_date = fields.Date(string='Change Date')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')


class PendingRepairType(models.Model):
    """Model Pending Repair Type."""

    _name = 'pending.repair.type'
    _description = 'Pending Repair Type'

    vehicle_rep_type_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    repair_type_id = fields.Many2one('repair.type', string="Repair Type")
    name = fields.Char(string='Work Order #', translate=True)
    categ_id = fields.Many2one("service.category", string="Category")
    issue_date = fields.Date(string="Issue Date")
    state = fields.Selection([('complete', 'Complete'),
                              ('in-complete', 'Pending')], string="Status")
    user_id = fields.Many2one('res.users', string="By")


class VehicleDivision(models.Model):
    """Model Vehicle Division."""

    _name = 'vehicle.divison'
    _description = 'Vehicle Division'

    code = fields.Char(string='Code', size=3, translate=True)
    name = fields.Char(string='Name', required=True, translate=True)

    _sql_constraints = [('vehicle.divison_uniq', 'unique(name)',
                         'This divison is already exist!')]


class VehicleType(models.Model):
    """Model Vehicle Type."""

    _name = 'vehicle.type'
    _description = 'Vehicle Type'

    code = fields.Char(string='Code', translate=True)
    name = fields.Char(string='Name', required=True,
                       translate=True)

    @api.constrains('name')
    def _check_unique_vehicle_type(self):
        for vehicle_type in self:
            if self.search_count([
                ('id', '!=', vehicle_type.id),
                ('name', 'ilike', vehicle_type.name.strip())
            ]):
                raise UserError(_('Vehicle type with this name already exists!'))


class VehicleLocation(models.Model):
    """Model Vehicle Location."""

    _name = 'vehicle.location'
    _description = 'Vehicle Location'

    code = fields.Char(string='Code', size=3, translate=True)
    name = fields.Char(string='Name', size=64, required=True,
                       translate=True)


class VehicleDepartment(models.Model):
    """Model Vehicle Department."""

    _name = 'vehicle.department'
    _description = 'Vehicle Department'

    code = fields.Char(string='Code', size=10, translate=True)
    name = fields.Char(string='Name', size=132, required=True, translate=True)


class ColorColor(models.Model):
    """Model Color."""

    _name = 'color.color'
    _description = 'Colors'

    code = fields.Char(string='Code', translate=True)
    name = fields.Char(string='Name', required=True, translate=True)

    @api.constrains('name')
    def check_color(self):
        """Method to check duplicate value."""
        for rec in self:
            if self.env['color.color'].search_count([
                ('name', 'ilike', rec.name.strip()),
                ('id', '!=', rec.id)
            ]):
                raise ValidationError(_("This color already exist"))


class IrAttachment(models.Model):
    """Model Ir Attachment."""

    _inherit = 'ir.attachment'

    attachment_id = fields.Many2one('fleet.vehicle')
    attachment_id_2 = fields.Many2one('fleet.vehicle')


class FleetWittenOff(models.Model):
    """Model Fleet Witten Off."""

    _name = 'fleet.wittenoff'
    _description = 'Wittenoff Vehicles'
    _order = 'id desc'
    _rec_name = 'vehicle_id'

    name = fields.Char(string="Name")
    fleet_id = fields.Integer(string='Fleet ID',
                              help="Take this field for data migration")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                 required=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env['res.company']._default_currency_id(),
        string='Currency',
        help="The optional other currency if it is a multi-currency entry."
    )
    vehicle_fmp_id = fields.Char(string='Vehicle ID', size=64)
    vin_no = fields.Char(string='Vin No', size=64, translate=True)
    color_id = fields.Many2one('color.color', string='Color')
    vehicle_plate = fields.Char(string='Vechicle Plate No.', translate=True)
    report_date = fields.Date(string='Report Date')
    odometer = fields.Float(string='Odometer')
    cost_esitmation = fields.Float(string='Cost Estimation')
    note_for_cause_damage = fields.Text(string='Cause of Damage',
                                        translate=True)
    note = fields.Text(string='Note', translate=True)
    cancel_note = fields.Text(string='Cancel Note', translate=True)
    multi_images = fields.Many2many('ir.attachment',
                                    'fleet_written_off_attachment_rel',
                                    'writeoff_id',
                                    'attachment_id', string='Multi Images')
    damage_type_ids = fields.Many2many('damage.types',
                                       'fleet_wittenoff_damage_types_rel',
                                       'write_off_id', 'damage_id',
                                       string="Damage Type")
    repair_type_ids = fields.Many2many('repair.type',
                                       'fleet_wittenoff_repair_types_rel',
                                       'write_off_id', 'repair_id',
                                       string="Repair Type")
    location_id = fields.Many2one('vehicle.location', string='Location')
    driver_id = fields.Many2one('res.partner', string='Driver')
    write_off_type = fields.Selection([
        ('general_accident', 'General Accident'),
        ('insurgent_attack', 'Insurgent Attack')],
        string='Write-off Type', default='general_accident')
    contact_no = fields.Char(string='Driver Contact Number')
    odometer_unit = fields.Selection([('kilometers', 'Kilometers'),
                                      ('miles', 'Miles')],
                                     string='Odometer Unit',
                                     help='Unit of the odometer ')
    province_id = fields.Many2one('res.country.state', 'Registration State')
    division_id = fields.Many2one('vehicle.divison', 'Division')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('cancel', 'Cancelled')],
                             string='State', default='draft')
    date_cancel = fields.Date(string='Date Cancelled')
    cancel_by_id = fields.Many2one('res.users', string="Cancelled By")

    @api.constrains('cost_esitmation')
    def check_estimation_cost(self):
        for cost in self:
            if cost.cost_esitmation < 0:
                raise ValidationError(_(
                    "Expense to repair cost should not be negative!"
                ))

    def write(self, vals):
        """Override write method and update values."""
        for fleet_witten in self:
            if fleet_witten.vehicle_id:
                vals.update(
                    {'vin_no': fleet_witten.vehicle_id and
                               fleet_witten.vehicle_id.vin_sn or "",
                     'vehicle_fmp_id': fleet_witten.vehicle_id and
                                       fleet_witten.vehicle_id.name or "",
                     'color_id': fleet_witten.vehicle_id and
                                 fleet_witten.vehicle_id.vehical_color_id and
                                 fleet_witten.vehicle_id.vehical_color_id.id or False,
                     'vehicle_plate': fleet_witten.vehicle_id and
                                      fleet_witten.vehicle_id.license_plate or "",
                     'province_id': fleet_witten.vehicle_id and
                                    fleet_witten.vehicle_id.vehicle_location_id and
                                    fleet_witten.vehicle_id.vehicle_location_id.id or False,
                     'division_id': fleet_witten.vehicle_id and
                                    fleet_witten.vehicle_id.vehical_division_id and
                                    fleet_witten.vehicle_id.vehical_division_id.id or False,
                     'driver_id': fleet_witten.vehicle_id and
                                  fleet_witten.vehicle_id.driver_id and
                                  fleet_witten.vehicle_id.driver_id.id or False,
                     'contact_no': fleet_witten.vehicle_id and
                                   fleet_witten.vehicle_id.driver_id and
                                   fleet_witten.vehicle_id.driver_id.mobile or "",
                     'odometer': fleet_witten.vehicle_id and
                                 fleet_witten.vehicle_id.odometer or 0.0,
                     'odometer_unit': fleet_witten.vehicle_id and
                                      fleet_witten.vehicle_id.odometer_unit or False,
                     })
        return super(FleetWittenOff, self).write(vals)

    @api.model
    def default_get(self, fields):
        """Default get method update in state changing record."""
        vehicle_obj = self.env['fleet.vehicle']
        res = super(FleetWittenOff, self).default_get(fields)
        if self._context.get('active_ids', False):
            for vehicle in vehicle_obj.browse(self._context['active_ids']):
                if vehicle.state == 'write-off':
                    raise UserError(_("This vehicle is already in "
                                      "write-off state!"))
                elif vehicle.state == 'in_progress' or \
                        vehicle.state == 'complete':
                    raise UserError(_("You can\'t write-off this vehicle "
                                      "which is in Progress or Complete state!"
                                      ))
                # elif vehicle.state == 'inspection':
                #     raise UserError(_("You can\'t write-off this "
                #                       "vehicle which is in Inspection"))
                elif vehicle.state == 'rent':
                    raise UserError(_("You can\'t write-off this "
                                      "vehicle which is On Rent."))
                res.update({'contact_no': vehicle.driver_contact_no or ''})
        return res

    @api.onchange('vehicle_id')
    def get_vehicle_info(self):
        """Method to get vehicle information."""
        if self.vehicle_id:
            vehicle = self.vehicle_id
            self.province_id = vehicle.vehicle_location_id and \
                               vehicle.vehicle_location_id.id or False
            self.driver_id = \
                vehicle.driver_id and vehicle.driver_id.id or False
            self.contact_no = vehicle.driver_contact_no or ''
            self.vin_no = vehicle.vin_sn or ''
            self.vehicle_fmp_id = vehicle.name or ''
            self.color_id = vehicle.vehical_color_id and \
                            vehicle.vehical_color_id.id or False
            self.vehicle_plate = vehicle.license_plate or ''
            self.odometer = vehicle.odometer or 0.0
            self.odometer_unit = vehicle.odometer_unit or False
            self.division_id = vehicle.vehical_division_id and \
                               vehicle.vehical_division_id.id or False

    def cancel_writeoff(self):
        """Button method in cancel state in the write off."""
        return {
            'name': 'Write Off Cancel Form',
            'res_model': 'writeoff.cancel.reason',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'
        }

    def confirm_writeoff(self):
        """Confirm button method in the writeoff state."""
        for wr_off in self:
            if wr_off.vehicle_id:
                wr_off.vehicle_id.write(
                    {'state': 'write-off',
                     'last_change_status_date': fields.Date.today(),
                     })
            wr_off.write({
                'state': 'confirm',
                'name': self.env['ir.sequence'].
                    next_by_code('vehicle.writeoff.sequnce'),
            })

    def action_set_to_draft(self):
        """Button method to set state in draft."""
        for wr_off in self:
            wr_off.write({
                'state': 'draft',
            })

    def get_usd_currency(self):
        """Method to get usd currency."""
        currency_obj = self.env['res.currency']
        usd_ids = currency_obj.search([('name', '=', 'USD')])
        if not usd_ids:
            raise UserError(
                _("Please, check USD Currency is not in your list!"))
        usd = usd_ids and usd_ids[0] or False
        return usd


class FleetVehicleModel(models.Model):
    """Model Fleet Vehicle."""

    _inherit = 'fleet.vehicle.model'
    _rec_name = 'name'

    name = fields.Char(string='Model name',
                       required=True, translate=True)
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Make',
                               required=True, help='Brand of the vehicle')

    image_128 = fields.Image(string="Image", readonly=False)

    _sql_constraints = [('model_brand_name_uniq', 'unique(name,brand_id)',
                         'Model with this brand Name and Make is '
                         'already exist!')]


class FleetVehicleModelBrand(models.Model):
    """Model Fleet Vehicle Model Brand."""

    _inherit = 'fleet.vehicle.model.brand'

    name = fields.Char(string='Make', size=64, required=True,
                       translate=True)

    @api.constrains('name')
    def _check_duplicate_model_brand(self):
        """Method to check duplicate damage type."""
        for model in self:
            if self.search_count([
                ('name', 'ilike', model.name.strip()),
                ('id', '!=', model.id)
            ]):
                raise ValidationError(_("Model Brand with this name already exists!"))


class FleetVehicleAdvanceSearch(models.TransientModel):
    """Model fleet vehicle advance search."""

    _name = 'fleet.vehicle.advance.search'
    _description = 'Vehicle Advance Search'
    _rec_name = 'fmp_id'

    fmp_id = fields.Many2one('fleet.vehicle', string="Vehicle ID")
    vehicle_location_id = fields.Many2one('res.country.state',
                                          string='Province')
    state = fields.Selection([('inspection', 'Inspection'),
                              ('in_progress', 'In Progress'),
                              ('complete', 'Completed'),
                              ('released', 'Released'),
                              ('write-off', 'Write-Off')], string='Status')
    vehical_color_id = fields.Many2one('color.color', string='Color')
    vin_no = fields.Char(string='Vin No', size=64)
    engine_no = fields.Char(string='Engine No', size=64)
    last_service_date = fields.Date(string='Last Service From')
    last_service_date_to = fields.Date(string='Last Service To')
    next_service_date = fields.Date(string='Next Service From')
    next_service_date_to = fields.Date(string='Next Service To')
    acquisition_date = fields.Date(string="Registration From")
    acquisition_date_to = fields.Date(string="Registration To")
    release_date_from = fields.Date(string='Released From')
    release_date_to = fields.Date(string='Released To')
    driver_identification_no = fields.Char(string='Driver ID', size=64)
    vechical_type_id = fields.Many2one('vehicle.type', string='Vechical Type')
    division_id = fields.Many2one('vehicle.divison', string="Division")
    make_id = fields.Many2one("fleet.vehicle.model.brand", string="Make")
    model_id = fields.Many2one("fleet.vehicle.model", string="Model")

    # @api.constrains('acquisition_date', 'acquisition_date_to')
    # def check_registration_date(self):
    #     """Method to check registration date."""
    #     for vehicle in self:
    #         if vehicle.acquisition_date_to and \
    #                 vehicle.acquisition_date_to < vehicle.acquisition_date:
    #             raise ValidationError('Registration To Date Should Be '
    #                                   'Greater Than Registration From Date.')
    #
    # @api.constrains('last_service_date', 'last_service_date_to')
    # def check_last_service_date(self):
    #     """Method to check last service date."""
    #     for vehicle in self:
    #         if vehicle.last_service_date_to and \
    #                 vehicle.last_service_date_to < vehicle.last_service_date:
    #             raise ValidationError('Last Service To Date Should Be '
    #                                   'Greater Than Last Service From Date.')
    #
    # @api.constrains('next_service_date', 'next_service_date_to')
    # def check_next_service_date(self):
    #     """Method to check next service date."""
    #     for vehicle in self:
    #         if vehicle.next_service_date_to and \
    #                 vehicle.next_service_date_to < vehicle.next_service_date:
    #             raise ValidationError('Next Service To Date Should Be '
    #                                   'Greater Than Next Service From Date.')
    #
    # @api.constrains('release_date_from', 'release_date_to')
    # def check_released_date(self):
    #     """Method to check released date."""
    #     for vehicle in self:
    #         if vehicle.release_date_to and \
    #                 vehicle.release_date_to < vehicle.release_date_from:
    #             raise ValidationError('Released To Date Should Be '
    #                                   'Greater Than Released From Date.')
    #
    # def get_vehicle_detail_by_advance_search(self):
    #     """Method to get vehicle detail by advance search."""
    #     domain = []
    #     vehicle_obj = self.env['fleet.vehicle']
    #     vehicle_ids = []
    #     for vehicle in self:
    #         if vehicle.make_id:
    #             vehicle_ids = vehicle_obj.search([
    #                 ('f_brand_id', '=', vehicle.make_id.id)])
    #         if vehicle.model_id:
    #             vehicle_ids = vehicle_obj.search([
    #                 ('model_id', '=', vehicle.model_id.id)])
    #
    #         if vehicle.state:
    #             domain += ('state', '=', vehicle.state),
    #         if vehicle.fmp_id:
    #             domain += ('id', '=', vehicle.fmp_id.id),
    #         if vehicle.vehicle_location_id:
    #             domain += [('vehicle_location_id', '=',
    #                         vehicle.vehicle_location_id.id)]
    #         if vehicle.division_id:
    #             domain += [('vehical_division_id', '=',
    #                         vehicle.division_id.id)]
    #         if vehicle.vechical_type_id:
    #             domain += [('vechical_type_id', '=',
    #                         vehicle.vechical_type_id.id)]
    #         if vehicle.vehical_color_id:
    #             domain += [('vehical_color_id', '=',
    #                         vehicle.vehical_color_id.id)]
    #         if vehicle.vin_no:
    #             domain += [('vin_sn', '=', vehicle.vin_no)]
    #         if vehicle.engine_no:
    #             domain += [('engine_no', '=', vehicle.engine_no)]
    #         if vehicle.driver_identification_no:
    #             domain += [('driver_identification_no', '=',
    #                         vehicle.driver_identification_no)]
    #         if vehicle.last_service_date and vehicle.last_service_date_to:
    #             domain += [('last_service_date', '>=',
    #                         vehicle.last_service_date)]
    #             domain += [('last_service_date', '<=',
    #                         vehicle.last_service_date_to)]
    #         elif vehicle.last_service_date:
    #             domain += [('last_service_date', '=',
    #                         vehicle.last_service_date)]
    #         if vehicle.next_service_date and vehicle.next_service_date_to:
    #             domain += [('next_service_date', '>=',
    #                         vehicle.next_service_date)]
    #             domain += [('next_service_date', '<=',
    #                         vehicle.next_service_date_to)]
    #         elif vehicle.next_service_date:
    #             domain += [('next_service_date', '=',
    #                         vehicle.next_service_date)]
    #         if vehicle.acquisition_date and vehicle.acquisition_date_to:
    #             domain += [('acquisition_date', '>=',
    #                         vehicle.acquisition_date)]
    #             domain += [('acquisition_date', '<=',
    #                         vehicle.acquisition_date_to)]
    #         elif vehicle.acquisition_date:
    #             domain += [('acquisition_date', '=', vehicle.acquisition_date)]
    #         if vehicle.release_date_from and vehicle.release_date_to:
    #             domain += [('released_date', '>=', vehicle.release_date_from)]
    #             domain += [('released_date', '<=', vehicle.release_date_to)]
    #         elif vehicle.release_date_from:
    #             domain += [('released_date', '=', vehicle.release_date_from)]
    #         if vehicle.make_id or vehicle.model_id:
    #             vehicle_ids = sorted(set(vehicle_ids.ids))
    #             domain += [('id', 'in', vehicle_ids)]
    #         return {
    #             'name': _('Vehicle Registration'),
    #             'view_type': 'form',
    #             "view_mode": 'tree,form',
    #             'res_model': 'fleet.vehicle',
    #             'type': 'ir.actions.act_window',
    #             'nodestroy': True,
    #             'domain': domain,
    #             'context': self._context,
    #             'target': 'current',
    #         }
    #     return True


class VehicleUniqueSequence(models.Model):
    """Model Vehicle Unique Sequence."""

    _name = 'vehicle.unique.sequence'
    _description = 'Vehicle Unique Sequence'

    name = fields.Char(string='Name', size=124, translate=True)
    vehicle_location_id = fields.Many2one('res.country.state',
                                          string='Location ')
    make_id = fields.Many2one('fleet.vehicle.model.brand', string='Make')
    sequence_id = fields.Many2one('ir.sequence', string='Sequence')

    _sql_constraints = [
        ('location_make_name_uniq',
         'unique (vehicle_location_id,make_id,sequence_id)',
         'Location, Make and Sequence all should be \
                unique for unique sequence!')
    ]


class NextIncrementNumber(models.Model):
    """Model Next Increment NUmber."""

    _name = 'next.increment.number'
    _description = 'Next Increment Number'

    name = fields.Char(string='Name', size=64, translate=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle Id')
    number = fields.Float(string='Odometer Increment')

    @api.constrains('number')
    def check_odometer_number(self):
        for rec in self:
            if rec.number < 0.0:
                raise ValidationError(_(
                    'You can not add negative value '
                    'for odometer number of vehicle!'
                ))

    @api.constrains('vehicle_id')
    def _check_vehicle_id(self):
        """Method to check last service date."""
        next_number = self.env['next.increment.number']
        for increment in self:
            if next_number.search_count([
                ('vehicle_id', '=', increment.vehicle_id.id),
                ('id', '!=', increment.id)
            ]):
                raise ValidationError(
                    _('You can not add more than one odometer '
                      'increment configuration for same vehicle.!!!'))


class NextServiceDays(models.Model):
    """Model Next Service Days."""

    _name = 'next.service.days'
    _description = 'Next Service days'

    name = fields.Char(string='Name', translate=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle Id')
    days = fields.Integer(string='Days')

    @api.constrains('days')
    def check_service_days(self):
        for rec in self:
            if rec.days < 0:
                raise ValidationError(_(
                    'You can not add negative value '
                    'next service days!'
                ))

    @api.constrains('vehicle_id')
    def _check_vehicle_id(self):
        """Method to check last service date."""
        for service in self:
            if self.search_count([
                ('vehicle_id', '=', service.vehicle_id.id),
                ('id', '!=', service.id)
            ]):
                raise ValidationError(
                    _('You can not add more than one next '
                      'service days configuration for same vehicle.!!!'))


class DamageTypes(models.Model):
    """Model Damage Types."""

    _name = 'damage.types'
    _description = 'Damage Types'

    name = fields.Char(string='Name', translate=True)
    code = fields.Char(string='Code')

    @api.constrains('name', 'code')
    def _check_duplicate_damage_type(self):
        """Method to check duplicate damage type."""
        for damage in self:
            if self.search_count([
                ('name', 'ilike', damage.name.strip()),
                ('code', 'ilike', damage.code.strip()),
                ('id', '!=', damage.id)
            ]):
                raise ValidationError(_("You can\'t add duplicate"
                                        " damage types !"))


# TODO
# class VehicleFuelLog(models.Model):
#     """Model Vehicle Fuel Log."""

#     _inherit = 'fleet.vehicle.log.fuel'

#     _order = 'id desc'

#     def _get_odometer(self):
#         fleetvehicalodometer = self.env['fleet.vehicle.odometer']
#         for record in self:
#             vehicle_odometer = fleetvehicalodometer.search([
#                 ('vehicle_id', '=', record.vehicle_id.id)], limit=1,
#                 order='value desc')
#             if vehicle_odometer:
#                 record.odometer = vehicle_odometer.value
#             else:
#                 record.odometer = 0

#     def _set_odometer(self):
#         fleetvehicalodometer = self.env['fleet.vehicle.odometer']
#         for record in self:
#             vehicle_odometer = fleetvehicalodometer.search(
#                 [('vehicle_id', '=', record.vehicle_id.id)],
#                 limit=1, order='value desc')
#             if record.odometer < vehicle_odometer.value:
#                 raise Warning(_('You can\'t enter odometer less than previous'
#                               'odometer %s !') % (vehicle_odometer.value))
#             if record.odometer:
#                 date = fields.Date.context_today(record)
#                 data = {'value': record.odometer, 'date': date,
#                         'vehicle_id': record.vehicle_id.id}
#                 fleetvehicalodometer.create(data)

#     @api.onchange('vehicle_id')
#     def _onchange_vehicle(self):
#         if not self.vehicle_id:
#             return {}
#         if self.vehicle_id:
#             self.odometer = self.vehicle_id.odometer
#             self.odometer_unit = self.vehicle_id.odometer_unit
#             self.purchaser_id = self.vehicle_id.driver_id.id

#     odometer = fields.Float(
#         compute='_get_odometer',
#         inverse='_set_odometer',
#         string='Last Odometer',
#         help='Odometer measure of the vehicle at the moment of this log')
#     odometer_unit = fields.Selection(
#         related='vehicle_id.odometer_unit',
#         help='Unit of the odometer ', store=True)
#     make = fields.Many2one(related='vehicle_id.f_brand_id',
#                            string='Make', store=True)
#     model = fields.Many2one(related='vehicle_id.model_id',
#                             string='Model', store=True)
#     current_fuel = fields.Float(string='Current Fuel', size=64)
#     fuel_type = fields.Selection(related='vehicle_id.fuel_type',
#                                  store=True,
#                                  help='Fuel Used by the vehicle')

#     @api.model
#     def default_get(self, fields):
#         """Vehicle fuel log default get the records."""
#         res = super(VehicleFuelLog, self).default_get(fields)
#         fleet_obj = self.env['fleet.vehicle']
#         if self._context:
#             ctx_keys = self._context.keys()
#             if 'active_model' in ctx_keys:
#                 if 'active_id' in ctx_keys:
#                     vehicle_id = self.env[self._context[
#                         'active_model']].browse(
#                         self._context['active_id'])
#                     if vehicle_id.state != 'write-off':
#                         res.update({'vehicle_id': self._context['active_id']})
#                     else:
#                         res['vehicle_id'] = False
#             if 'vehicle_id' in ctx_keys:
#                 vehicle_id = fleet_obj.browse(self._context['vehicle_id'])
#                 if vehicle_id.state != 'write-off':
#                     res.update({'vehicle_id': self._context['vehicle_id']})
#         return res

#     def copy(self, default=None):
#         """
#         Method copy for can not duplicate records.

#         In the vehicle fuel log.
#         """
#         if not default:
#             default = {}
#         raise Warning(_('You can\'t duplicate record!'))

# TODO
# class FleetVehicleCost(models.Model):
#     """Model Fleet Vehicle Cost."""

#     _inherit = 'fleet.vehicle.cost'

#     @api.model
#     def default_get(self, fields):
#         """Default get method is set vehilce id."""
#         res = super(FleetVehicleCost, self).default_get(fields)
#         fleet_obj = self.env['fleet.vehicle']
#         if self._context.get('active_id', False):
#             vehicle_id = fleet_obj.browse(self._context['active_id'])
#             if vehicle_id.state == 'write-off':
#                 res['vehicle_id'] = False
#         return res


class FleetVehicleOdometer(models.Model):
    """Model Fleet Vehicle Odometer."""

    _inherit = 'fleet.vehicle.odometer'
    _description = 'Odometer log for a vehicle'
    _order = 'date desc'

    def _compute_vehicle_log_name_get_fnc(self):
        for record in self:
            name = record.vehicle_id and record.vehicle_id.name or False
            if record.date:
                if not name:
                    name = "New/" + str(record.date)
                name = name + ' / ' + str(record.date)
            record.name = name

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        """Method to onchange vehicle."""
        if self.vehicle_id:
            odometer_unit = self.vehicle_id.odometer_unit
            value = self.vehicle_id.odometer
            self.unit = odometer_unit
            self.value = value

    name = fields.Char(compute="_compute_vehicle_log_name_get_fnc", string='Name',
                       store=True)
    date = fields.Date(string='Date', default=fields.Date.today())
    value = fields.Float(string='Odometer Value', group_operator="max")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                 required=True)
    make = fields.Many2one(related='vehicle_id.f_brand_id',
                           string='Make', store=True)
    model = fields.Many2one(related='vehicle_id.model_id',
                            string='Model', store=True)
    unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit",
                            readonly=True)

    @api.model
    def default_get(self, fields):
        """Method default get."""
        res = super(FleetVehicleOdometer, self).default_get(fields)
        # cr, uid, context = self.env.args
        context = self.env.context
        # context = dict(context)
        fleet_obj = self.env['fleet.vehicle']
        if self._context.get('active_id'):
            vehicle_id = fleet_obj.browse(context['active_id'])
            if vehicle_id.state == 'write-off':
                res['vehicle_id'] = False
        return res


class ReportHeading(models.Model):
    """Model Report Heading."""

    _name = 'report.heading'
    _description = 'Report Heading'

    @api.depends('image')
    def _get_image(self):
        return dict((p.id, tools.image_get_resized_images(p.image))
                    for p in self)

    def _set_image(self):
        if self.image_small:
            self.image = \
                tools.image_resize_image_small(self.image_small,
                                               size=(102, 50))
        elif self.image_medium:
            self.image = \
                tools.image_resize_image_small(self.image_medium,
                                               size=(102, 50))

    name = fields.Char(string='Title', size=128, translate=True)
    revision_no = fields.Char(string='Rev. No.', size=64, translate=True)
    document_no = fields.Char(string='Document No.', size=64, translate=True)
    image = fields.Binary(string="Image",
                          help="This field holds the image used as image \
                            for the Report , limited to 1024x1024px.")
    image_medium = fields.Binary(compute="_get_image", inverse='_set_image',
                                 string="Medium-sized image",
                                 help="Medium-sized image of the Report. \
                                 It is automatically resized as a 128x128px \
                                image, with aspect ratio preserved, "
                                      "only when the image exceeds one of those \
                                 sizes. Use this field in form views or \
                                 some kanban views.")
    image_small = fields.Binary(compute="_get_image", inverse='_set_image',
                                string="Report image",
                                help="Small-sized image of the Report. \
                                It is automatically "
                                     "resized as a 64x64px image, \
                                with aspect ratio preserved. "
                                     "Use this field anywhere a small \
                                image is required.")


class ResCompany(models.Model):
    """Model Res Company."""

    _inherit = 'res.company'

    name = fields.Char(related='partner_id.name', string='Company Name',
                       required=True, store=True, translate=True)


class InsuranceType(models.Model):
    """Model Insurance Type."""

    _name = 'insurance.type'
    _description = 'Vehicle Insurance Type'

    name = fields.Char(string='Name')
