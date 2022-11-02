odoo.define('report_xml.ReportActionManager', function(require){
    'use strict';

var ActionManager = require('web.ActionManager');

    ActionManager.include({
        _executeReportAction: function (action, options) {
            if (action.report_type === 'qweb-xml') {
                return this._triggerDownload(action, options, 'xml');
            }
            if (action.report_type === 'qweb-xls') {
                return this._triggerDownload(action, options, 'xls');
            }
            if (action.report_type === 'qweb-ppt') {
                return this._triggerDownload(action, options, 'ppt');
            }
            if (action.report_type === 'qweb-pptp') {
                return this._triggerDownload(action, options, 'pptp');
            }
            if (action.report_type === 'qweb-doc') {
                return this._triggerDownload(action, options, 'doc');
            }
            if (action.report_type === 'qweb-docp') {
                return this._triggerDownload(action, options, 'docp');
            }
            return this._super(action, options);
        },
        _makeReportUrls: function (action) {
            var reportUrls = this._super(action);
            reportUrls.xml = reportUrls.text.replace('/report/text/', '/report/xml/');
            reportUrls.xls = reportUrls.text.replace('/report/text/', '/report/xls/');
            reportUrls.ppt = reportUrls.text.replace('/report/text/', '/report/ppt/');
            reportUrls.pptp = reportUrls.text.replace('/report/text/', '/report/pptp/');
            reportUrls.doc = reportUrls.text.replace('/report/text/', '/report/doc/');
            reportUrls.docp = reportUrls.text.replace('/report/text/', '/report/docp/');
            return reportUrls;
        },
    });
});
