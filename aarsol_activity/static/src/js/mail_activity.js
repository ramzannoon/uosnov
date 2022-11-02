// We do not want to show the activities that have been completed.
odoo.define('mail.Activity.done', function(require) {
"use strict";

    var mailUtils = require('mail.utils');
    var core = require('web.core');
    var utils = require('mail.utils');
    var time = require('web.time');
    var mail_activity = require('mail.Activity');

    var QWeb = core.qweb;
    var _t = core._t;

    // We are forced here to override the method, as there is no possibility to inherit it.
    var setDelayLabel = function(activities) {
        var today = moment().startOf('day');
        _.each(activities, function(activity) {
            var to_display = '';
            var deadline = moment(activity.date_deadline).startOf('day');
            var diff = deadline.diff(today, 'days', true); // true means no rounding
            if(diff === 0){
                to_display = _t('Today');
            }else{
                if(diff < 0){ // overdue
                    if(diff === -1){
                        to_display = _t('Yesterday');
                    }else{
                        to_display = _.str.sprintf(_t('%d days overdue'), Math.abs(diff));
                    }
                }else{ // due
                    if(diff === 1){
                        to_display = _t('Tomorrow');
                    }else{
                        to_display = _.str.sprintf(_t('Due in %d days'), Math.abs(diff));
                    }
                }
            }
            activity.label_delay = to_display;
        });
        // We do not want to show the activities that have been completed.
        var open_activities = _.filter(activities, function(activity){
            return activity.done !== true
        });
        return open_activities;
    };

    var Activity = mail_activity.include({
        _render: function () {
            _.each(this._activities, function (activity) {
                var note = mailUtils.parseAndTransform(activity.note || '', mailUtils.inline);
                var is_blank = (/^\s*$/).test(note);
                if (!is_blank) {
                    activity.note = mailUtils.parseAndTransform(activity.note, mailUtils.addLink);
                } else {
                    activity.note = '';
                }
            });
            var activities = setDelayLabel(this._activities);
            if (activities.length) {
                var nbActivities = _.countBy(activities, 'state');
                this.$el.html(QWeb.render('mail.activity_items2', {
                    activities: activities,
                    nbPlannedActivities: nbActivities.planned,
                    nbTodayActivities: nbActivities.today,
                    nbOverdueActivities: nbActivities.overdue,
                    dateFormat: time.getLangDateFormat(),
                    datetimeFormat: time.getLangDatetimeFormat(),
                }));
            } else {
                this.$el.empty();
            }
        },
    });

    var BasicActivity = mail_activity.include({
        events: _.extend({}, mail_activity.prototype.events, {
            'click .o_mark_approval': '_onMarkApproval',
        }),
        _markActivityDoneAndScheduleNext: function (params) {
            var activityID = params.activityID;
            var feedback = params.feedback;
            var self = this;
            this._rpc({
                model: 'mail.activity',
                method: 'action_feedback_schedule_next',
                args: [[activityID]],
                kwargs: {feedback: feedback},
                context: this.record.getContext(),
            }).then(
                function (result) {
                    if (result.action) {
                        self.do_action(result.action, {
                            on_close: function () {
                                self.trigger_up('reload');
                            },
                        });
                    } else if (result.info) {
                        self.do_notify("Activity",result.info);
                        self.trigger_up('reload');
                    } else if (result.warning) {
                        self.do_warn("Activity",result.warning);    // ,true
                        self.trigger_up('reload');
                    }
                    else if (result) {
                        self.do_action(result, {
                            on_close: function () {
                                self.trigger_up('reload');
                            },
                        });
                    } else {
                        self.trigger_up('reload');
                    }
                }
            );
        },

        _markActivityDoneAndSchedulePrev: function (params) {
            var activityID = params.activityID;
            var feedback = params.feedback;
            var self = this;
            this._rpc({
                model: 'mail.activity',
                method: 'action_feedback_schedule_prev',
                args: [[activityID]],
                kwargs: {feedback: feedback},
                context: this.record.getContext(),
            }).then(
                function (result) {
                    if (result.action) {
                        self.do_action(result.action, {
                            on_close: function () {
                                self.trigger_up('reload');
                            },
                        });
                    } else if (result.info) {
                        self.do_notify("Activity",result.info);
                        self.trigger_up('reload');
                    } else if (result.warning) {
                        self.do_warn("Activity",result.warning);  // ,true
                        self.trigger_up('reload');
                    }
                    else if (result) {
                        self.do_action(result, {
                            on_close: function () {
                                self.trigger_up('reload');
                            },
                        });
                    } else {
                        self.trigger_up('reload');
                    }
                }
            );
        },

        _onMarkActivityApprovalActions: function ($btn, $form, activityID) {
            var self = this;
            debugger;
            $form.find('#activity_feedback').val(self._draftFeedback[activityID]);
            $form.on('click', '.o_activity_popover_approve', function (ev) {
                ev.stopPropagation();
                var feedback = _.escape($form.find('#activity_feedback').val());
                self._markActivityDone({
                    activityID: activityID,
                    feedback: feedback,
                });
            });
            $form.on('click', '.o_activity_popover_approve_next', function (ev) {
                ev.stopPropagation();
                var feedback = _.escape($form.find('#activity_feedback').val());
                debugger;
                if (feedback == ''){
                    self.do_warn('Feedback','Please Provide the Comments!');
                } else {
                        self._markActivityDoneAndScheduleNext({
                        activityID: activityID,
                        feedback: feedback,
                    });
                }

            });
            $form.on('click', '.o_activity_popover_approve_prev', function (ev) {
                ev.stopPropagation();
                var feedback = _.escape($form.find('#activity_feedback').val());
                debugger;
                if (feedback == ""){
                    self.do_warn('Feedback','Please Provide the Comments!');
                } else {
                    self._markActivityDoneAndSchedulePrev({
                        activityID: activityID,
                        feedback: feedback,
                    });
                }
            });
            $form.on('click', '.o_activity_popover_unapprove', function (ev) {
                ev.stopPropagation();
                var feedback = _.escape($form.find('#activity_feedback').val());
                debugger;
                if (feedback == ''){
                    self.do_warn('Feedback','Please Provide the Comments!');
                } else {
                    self._markActivityUnapprove({
                        activityID: activityID,
                        feedback: feedback,
                    });
                }
            });
            $form.on('click', '.o_activity_popover_discard', function (ev) {
                ev.stopPropagation();
                if ($btn.data('bs.popover')) {
                    $btn.popover('hide');
                } else if ($btn.data('toggle') == 'collapse') {
                    self.$('#o_activity_form_' + activityID).collapse('hide');
                }
            });


        },
        _onMarkApproval: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();
            var self = this;
            var $markApprovalBtn = $(ev.currentTarget);
            var activityID = $markApprovalBtn.data('activity-id');
            var activityCategory = $markApprovalBtn.data('activity-category');
            var previousActivityTypeID = $markApprovalBtn.data('previous-activity-type-id') || false;
            var forceNextActivity = $markApprovalBtn.data('force-next-activity');
            var forcePrevActivity = $markApprovalBtn.data('force-prev-activity');
            if (!$markApprovalBtn.data('bs.popover')) {
                $markApprovalBtn.popover({
                    template: $(Popover.Default.template).addClass('o_mail_activity_feedback')[0].outerHTML, // Ugly but cannot find another way
                    container: $markApprovalBtn,
                    title : _t("Remarks"),
                    html: true,
                    trigger: 'manual',
                    placement: 'right', // FIXME: this should work, maybe a bug in the popper lib
                    content : function () {
                        var $popover = $(QWeb.render('mail.activity_approval_form', {
                            previous_activity_type_id: previousActivityTypeID,
                            force_next: forceNextActivity,
                            force_prev: forcePrevActivity,
                            activity_category: activityCategory
                        }));
                        self._onMarkActivityApprovalActions($markApprovalBtn, $popover, activityID);
                        return $popover;
                    },
                }).on('shown.bs.popover', function () {
                    var $popover = $($(this).data("bs.popover").tip);
                    $(".o_mail_activity_feedback.popover").not($popover).popover("hide");
                    $popover.addClass('o_mail_activity_feedback').attr('tabindex', 0);
                    $popover.find('#activity_feedback').focus();
                    self._bindPopoverFocusout($(this));
                }).popover('show');
            } else {
                var popover = $markApprovalBtn.data('bs.popover');
                if ($('#' + popover.tip.id).length === 0) {
                   popover.show();
                }
            }
        },
        _markActivityDone: function (params) {
            var activityID = params.activityID;
            var feedback = params.feedback || false;
            var attachmentIds = params.attachmentIds || [];

            var self = this;
            if (feedback == ''){
                self.do_warn('Feedback','Please Provide the Comments!');
            } else {
                return this._post_function(activityID)
                    .then(this._sendActivityFeedback(activityID, feedback))
                    .then(this._reload.bind(this, { activity: true, thread: true }));
            }
        },
        _post_function: function (activityID) {
            return this._rpc({
                model: 'mail.activity',
                method: 'action_post_function',
                args: [[activityID]],
                context: this.record.getContext(),
            });
        },
        _markActivityUnapprove: function (params) {
            var activityID = params.activityID;
            var feedback = params.feedback;
            debugger;
            if (feedback == ''){
                self.do_warn('Feedback','Please Provide the Comments!');
            } else {
                this._cancel_function(activityID)
                    .then(this._sendActivityFeedback(activityID, feedback))
                    .then(this._reload.bind(this, { activity: true, thread: true }));
            }
        },
        _cancel_function: function (activityID) {
            debugger;
            return this._rpc({
                model: 'mail.activity',
                method: 'unlink',
                args: [[activityID]],
                context: this.record.getContext(),
            });
        },

    });
});
