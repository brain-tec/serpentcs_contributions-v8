odoo.define('web_one2many_kanban.web_one2many_kanban', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var KanbanRecord = require('web.KanbanRecord');

KanbanRecord.include({
    _render: function () {
        var self = this;

        var o2x_field_names = [];

        _.each(this.fieldsInfo, function (field_info, field_nm) {
            if (field_info.mode === 'list' || field_info.mode === 'kanban') {
                o2x_field_names.push(field_nm);
            }
        })

        if (o2x_field_names.length > 0) {
            var o2x_records = [];

            _.each(o2x_field_names, function(o2x_field_name) {
                var record = self.qweb_context.record[o2x_field_name];
                if (record.type === 'one2many' && record.raw_value.length !== 0) {
                    // only fetch data where this one2many field actually contains records
                    o2x_records.push(record);
                }
            });

            var _super = this._super.bind(this);

            if (o2x_records.length === 0) {
                // no need to call the endpoint if there are no records to fetch data for
                return _super();
            }
            ajax.jsonRpc("/web/fetch_x2m_data", "call", {'o2x_records': o2x_records}).then(function (o2x_datas) {
                for (var i=0; i < o2x_datas.length; i++) {
                    o2x_records[i].raw_value = o2x_datas[i];
                }

                return _super();
            });
        } else {
            return self._super.apply(self, arguments);
        }
    }
});

});
