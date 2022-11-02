// Redirect to the Board by clicking on the Activities on the Chatter Form
odoo.define('mail.Chatter.activity', function (require) {
    "use strict";

    var chatter = require('mail.Chatter');

    chatter.include({
        events: _.extend({}, chatter.prototype.events, {
            'click .o_chatter_button_list_activity': '_onListActivity',
        }),
        _onListActivity: function () {
            this._rpc({
                model: this.record.model,
                method: 'redirect_to_activities',
                args: [[]],
                kwargs: {
                    'id':this.record.res_id,
                    'model':this.record.model,
                },
                context: this.record.getContext(),
            }).then($.proxy(this, "do_action"));
        },
    });
});


