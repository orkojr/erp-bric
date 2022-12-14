odoo.define('jk_dashboard.Dashboard', function(require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var PosDashboard = AbstractAction.extend({

        template: 'Dashboard',


    });

    core.action_registry.add('jk_dashboard_tag', PosDashboard);

    return PosDashboard;
});