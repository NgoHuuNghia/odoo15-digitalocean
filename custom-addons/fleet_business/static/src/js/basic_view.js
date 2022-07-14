odoo.define('fleet_business.basic_view', function (require) {
  "use strict";
  
  var session = require('web.session');
  var BasicView = require('web.BasicView');
  BasicView.include({
    init: function(viewInfo, params) {
        var self = this;
        this._super.apply(this, arguments);
        var model = self.controllerParams.modelName in ['res.partner','fleet.business.trip'] ? 'True' : 'False';
        if(model) {
            session.user_has_group('fleet.fleet_group_manager').then(function(has_group) {
                if(!has_group) {
                    self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                }
            });
        }
    },
  });
});