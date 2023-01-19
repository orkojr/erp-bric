odoo.define('web.OrgChart', function(require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var concurrency = require('web.concurrency');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var session = require('web.session');

    var QWeb = core.qweb;
    var _t = core._t;

    var FieldOrgChart = AbstractField.extend({

        events: {
            "click .o_department_redirect": "_onDepartmentRedirect",
            "click .o_department_sub_redirect": "_onDepartmentSubRedirect",
            "click .o_department_more_managers": "_onDepartmentMoreManager"
        },
        /**
         * @constructor
         * @override
         */
        init: function(parent, options) {
            this._super.apply(this, arguments);
            this.dm = new concurrency.DropMisordered();
            this.department = null;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        /**
         * Get the chart data through a rpc call.
         *
         * @private
         * @param {integer} department_id
         * @returns {Promise}
         */
        _getOrgData: function() {
            var self = this;
            return this.dm.add(this._rpc({
                route: '/hr_org_dep_chart/get_org_chart',
                params: {
                    department_id: this.department,
                    context: session.user_context,
                },
            })).then(function(data) {
                return data;
            });
        },
        /**
         * Get subordonates of an department through a rpc call.
         *
         * @private
         * @param {integer} department_id
         * @returns {Promise}
         */
        _getSubordinatesData: function(department_id, type) {
            return this.dm.add(this._rpc({
                route: '/hr_org_dep_chart/get_subordinates',
                params: {
                    department_id: department_id,
                    subordinates_type: type,
                    context: session.user_context,
                },
            }));
        },
        /**
         * @override
         * @private
         */
        _render: function() {
            if (!this.recordData.id) {
                return this.$el.html(QWeb.render("hr_org_dep_chart", {
                    managers: [],
                    children: [],
                }));
            } else if (!this.department) {
                // the widget is either dispayed in the context of a hr.department form or a res.users form
                this.department = this.recordData.department_ids !== undefined ? this.recordData.department_ids.res_ids[0] : this.recordData.id;
            }

            var self = this;
            return this._getOrgData().then(function(orgData) {
                if (_.isEmpty(orgData)) {
                    orgData = {
                        managers: [],
                        children: [],
                    }
                }
                orgData.view_department_id = self.recordData.id;
                self.$el.html(QWeb.render("hr_org_dep_chart", orgData));
                self.$('[data-toggle="popover"]').each(function() {
                    $(this).popover({
                        html: true,
                        title: function() {
                            var $title = $(QWeb.render('hr_orgchart_dep_popover_title', {
                                department: {
                                    name: $(this).data('emp-name'),
                                    id: $(this).data('emp-id'),
                                },
                            }));
                            $title.on('click',
                                '.o_department_redirect', _.bind(self._onDepartmentRedirect, self));
                            return $title;
                        },
                        container: this,
                        placement: 'left',
                        trigger: 'focus',
                        content: function() {
                            var $content = $(QWeb.render('hr_orgchart_dep_popover_content', {
                                department: {
                                    id: $(this).data('emp-id'),
                                    name: $(this).data('emp-name'),
                                    direct_sub_count: parseInt($(this).data('emp-dir-subs')),
                                    indirect_sub_count: parseInt($(this).data('emp-ind-subs')),
                                },
                            }));
                            $content.on('click',
                                '.o_department_sub_redirect', _.bind(self._onDepartmentSubRedirect, self));
                            return $content;
                        },
                        template: QWeb.render('hr_orgchart_dep_popover', {}),
                    });
                });
            });
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        _onDepartmentMoreManager: function(event) {
            event.preventDefault();
            this.department = parseInt($(event.currentTarget).data('department-id'));
            this._render();
        },
        /**
         * Redirect to the department form view.
         *
         * @private
         * @param {MouseEvent} event
         * @returns {Promise} action loaded
         */
        _onDepartmentRedirect: function(event) {
            var self = this;
            event.preventDefault();
            var department_id = parseInt($(event.currentTarget).data('department-id'));
            return this._rpc({
                model: 'hr.department',
                method: 'get_formview_action',
                args: [department_id],
            }).then(function(action) {
                return self.do_action(action);
            });
        },
        /**
         * Redirect to the sub department form view.
         *
         * @private
         * @param {MouseEvent} event
         * @returns {Promise} action loaded
         */
        _onDepartmentSubRedirect: function(event) {
            event.preventDefault();
            var department_id = parseInt($(event.currentTarget).data('department-id'));
            var department_name = $(event.currentTarget).data('department-name');
            var type = $(event.currentTarget).data('type') || 'direct';
            var self = this;
            if (department_id) {
                this._getSubordinatesData(department_id, type).then(function(data) {
                    var domain = [
                        ['id', 'in', data]
                    ];
                    return self._rpc({
                        model: 'hr.department',
                        method: 'get_formview_action',
                        args: [department_id],
                    }).then(function(action) {
                        action = _.extend(action, {
                            'name': _t('Team'),
                            'view_mode': 'kanban,list,form',
                            'views': [
                                [false, 'kanban'],
                                [false, 'list'],
                                [false, 'form']
                            ],
                            'domain': domain,
                            'context': {
                                'default_parent_id': department_id,
                            }
                        });
                        delete action['res_id'];
                        return self.do_action(action);
                    });
                });
            }
        },
    });

    field_registry.add('hr_org_dep_chart', FieldOrgChart);

    return FieldOrgChart;

});