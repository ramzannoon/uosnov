odoo.define('odoocms_admission_portal.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
//var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');

var _t = core._t;
var QWeb = core.qweb;

var HrDashboard = AbstractAction.extend({
    template: 'HrDashboardMain',
    cssLibs: [
        '/odoocms_admission_portal/static/src/css/lib/nv.d3.css'
    ],
    jsLibs: [
        '/odoocms_admission_portal/static/src/js/lib/d3.min.js'
    ],
    events: {
        'click .total_registration':'total_registration',
        'click .invoice_downloaded':'invoice_downloaded',
        'click .invoice_uploaded':'invoice_uploaded',
        'click .academic_step':'academic_step',
        'click .admission_done':'admission_done',
        'click .voucher_verified':'voucher_verified',
        'click .voucher_unverified':'voucher_unverified',
        'click .applicant_final_score':'applicant_final_score',
        'click .applicant_submitted':'applicant_submitted',
    },

    init: function(parent, context) {
        this._super(parent, context);

        this.date_range = 'week';  // possible values : 'week', 'month', year'
        this.date_from = moment().subtract(1, 'week');
        this.date_to = moment();
//        this.dashboards_templates = ['LoginEmployeeDetails', 'ManagerDashboard', 'EmployeeDashboard'];
        this.dashboards_templates = ['LoginEmployeeDetails'];
        this.dashboards_templates2 = ['EmployeeWarning'];
        this.employee_birthday = [];
        this.upcoming_events = [];
        this.announcements = [];
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.fetch_data();
        });
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.render_dashboards();
            self.$el.parent().addClass('oe_background_grey');
        });
    },

    fetch_data: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'hr.employee',
                method: 'get_user_employee_details'
        }).then(function(result) {
            self.login_employee =  result[0];
        });

       // var def2 =  this._rpc({
       //         model: 'hr.employee',
       //         method: 'get_user_employee_details'
       // }).done(function(result) {
        //    self.students =  result[0];
        //});
        return $.when(def1);
    },

    render_dashboards: function() {
        var self = this;
        if (this.login_employee){
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}));
            });
            }
        else{
            self.$('.o_hr_dashboard').append(QWeb.render(this.dashboards_templates2[0], {widget: self}));
            }
    },

    /*render_graphs: function(){
        var self = this;
        if (this.login_employee){
            self.render_department_employee();
            self.render_leave_graph();
            self.update_join_resign_trends();
            self.update_monthly_attrition();
            self.update_leave_trend();
        }
    },*/

    total_registration: function(e){
        var self = this;
        var a1;

        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
         var reg_list =  this._rpc({
            model: 'odoocms.application',
            method: 'get_total_registration_list_view'
        }).then(function (result){
            a1 = result['registration_list_id'];
            self.do_action({
                name: _t("All Registrations"),
                type: 'ir.actions.act_window',
                res_model: 'odoocms.application',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[a1, 'list'],[false, 'form']],
                domain: [['register_id.state','=', 'application']],
            target: 'current'
            }, options)
        });
    },

    invoice_downloaded: function(e){
        var self = this;
        var a2;

        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var dwn_list =  this._rpc({
            model: 'odoocms.application',
            method: 'get_downloaded_list_view'
        }).then(function (result){
            a2 = result['downloaded_list_id'];
            self.do_action({
                name: _t("Fee Voucher Downloaded"),
                type: 'ir.actions.act_window',
                res_model: 'odoocms.application',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[a2, 'list'],[false, 'form']],
                domain: [['fee_voucher_state','!=','no']],
                target: 'current'
            }, options)
        });
    },

    invoice_uploaded: function(e){
        var self = this;
        var a3;

        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
         var dwn_list =  this._rpc({
            model: 'odoocms.application',
            method: 'get_upload_list_view'
        }).then(function (result){
            a3 = result['upload_list_id'];
            self.do_action({
                name: _t("Processing Fee Submitted"),
                type: 'ir.actions.act_window',
                res_model: 'odoocms.application',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[a3, 'list'],[false, 'form']],
                domain: [['fee_voucher_state', '=', 'upload']],
                target: 'current'
            }, options)
        });
    },

    voucher_verified: function(e){
        var self = this;
        var a4;

        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
         var dwn_list =  this._rpc({
            model: 'odoocms.application',
            method: 'get_verified_list_view'
        }).then(function (result){
            a4 = result['verified_list_id'];
            self.do_action({
                name: _t("Fee Verified"),
                type: 'ir.actions.act_window',
                res_model: 'odoocms.application',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[a4, 'list'],[false, 'form']],
                domain: [['fee_voucher_state', '=', 'verify']],
                target: 'current'
            }, options)
          });
    },

     voucher_unverified: function(e){
        var self = this;
        var a5;

        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
           var dwn_list =  this._rpc({
            model: 'odoocms.application',
            method: 'get_unverified_list_view'
        }).then(function (result){
            a5 = result['unverified_list_id'];
            self.do_action({
                name: _t("Fee UnVerified"),
                type: 'ir.actions.act_window',
                res_model: 'odoocms.application',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[a5, 'list'],[false, 'form']],
                domain: [['fee_voucher_state', '=', 'unverify']],
                target: 'current'
            }, options)
        });
    },

    applicant_final_score: function(e){
        var self = this;
        var a6;

        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
         var dwn_list =  this._rpc({
            model: 'odoocms.application',
            method: 'get_final_score_list_view'
        }).then(function (result){
            a6 = result['final_score_list_id'];
            self.do_action({
                name: _t("Applicant Final Score"),
                type: 'ir.actions.act_window',
                res_model: 'odoocms.application',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[2504, 'list'],[false, 'form']],
                domain: [['state','=', 'draft'],['fee_voucher_state', '=', 'verify']],
                target: 'current'
            }, options)
        });
    },

    applicant_submitted: function(e){
        var self = this;
        var a7;

        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
         var dwn_list =  this._rpc({
            model: 'odoocms.application',
            method: 'get_confirm_applications_list_view'
        }).then(function (result){
            a7 = result['confirm_applications_list_id'];
            self.do_action({
                name: _t("Application Submitted"),
                type: 'ir.actions.act_window',
                res_model: 'odoocms.application',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[a7, 'list'],[false, 'form']],
                domain: [['state','=', 'confirm']],
                target: 'current'
            }, options)
        });
    },

    academic_step: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        self.do_action({
            name: _t("On Academic Step"),
            type: 'ir.actions.act_window',
            res_model: 'odoocms.application',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['step','=', 'Academic Step Done']],
            target: 'current'
        }, options)
    },

    admission_done: function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Admission Granted"),
            type: 'ir.actions.act_window',
            res_model: 'odoocms.application',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['state','=', 'done']],
            target: 'current'
        }, options)
    },

});


core.action_registry.add('hr_dashboard', HrDashboard);

return HrDashboard;

});
