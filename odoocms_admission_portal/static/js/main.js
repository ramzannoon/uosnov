$(function(){
odoo.define("website.ace", function (require) {
"use strict";

var AceEditor = require('web_editor.ace');

/**
 * Extends the default view editor so that the URL hash is updated with view ID
 */
var WebsiteAceEditor = AceEditor.extend({
    hash: '#advanced-view-editor',

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    do_hide: function () {
        this._super.apply(this, arguments);
        window.location.hash = "";
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _displayResource: function () {
        this._super.apply(this, arguments);
        this._updateHash();
    },
    /**
     * @override
     */
    _saveResources: function () {
        return this._super.apply(this, arguments).then((function () {
            var defs = [];
            if (this.currentType === 'xml') {
                // When saving a view, the view ID might change. Thus, the
                // active ID in the URL will be incorrect. After the save
                // reload, that URL ID won't be found and JS will crash.
                // We need to find the new ID (either because the view became
                // specific or because its parent was edited too and the view
                // got copy/unlink).
                var selectedView = _.findWhere(this.views, {id: this._getSelectedResource()});
                var context;
                this.trigger_up('context_get', {
                    callback: function (ctx) {
                        context = ctx;
                    },
                });
                defs.push(this._rpc({
                    model: 'ir.ui.view',
                    method: 'search_read',
                    fields: ['id'],
                    domain: [['key', '=', selectedView.key], ['website_id', '=', context.website_id]],
                }).then((function (view) {
                    if (view[0]) {
                        this._updateHash(view[0].id);
                    }
                }).bind(this)));
            }
            return Promise.all(defs).then((function () {
                window.location.reload();
                return new Promise(function () {});
            }));
        }).bind(this));
    },
    /**
     * @override
     */
    _resetResource: function () {
        return this._super.apply(this, arguments).then((function () {
            window.location.reload();
            return new Promise(function () {});
        }).bind(this));
    },
    /**
     * Adds the current resource ID in the URL.
     *
     * @private
     */
    _updateHash: function (resID) {
        window.location.hash = this.hash + "?res=" + (resID || this._getSelectedResource());
    },
});

return WebsiteAceEditor;
});

odoo.define('web_editor.base', function (require) {
'use strict';

// TODO this should be re-removed as soon as possible.

var ajax = require('web.ajax');
var session = require('web.session');

var domReady = new Promise(function(resolve) {
    $(resolve);
});

return {
    /**
     * Retrieves all the CSS rules which match the given parser (Regex).
     *
     * @param {Regex} filter
     * @returns {Object[]} Array of CSS rules descriptions (objects). A rule is
     *          defined by 3 values: 'selector', 'css' and 'names'. 'selector'
     *          is a string which contains the whole selector, 'css' is a string
     *          which contains the css properties and 'names' is an array of the
     *          first captured groups for each selector part. E.g.: if the
     *          filter is set to match .fa-* rules and capture the icon names,
     *          the rule:
     *              '.fa-alias1::before, .fa-alias2::before { hello: world; }'
     *          will be retrieved as
     *              {
     *                  selector: '.fa-alias1::before, .fa-alias2::before',
     *                  css: 'hello: world;',
     *                  names: ['.fa-alias1', '.fa-alias2'],
     *              }
     */
    cacheCssSelectors: {},
    getCssSelectors: function (filter) {
        if (this.cacheCssSelectors[filter]) {
            return this.cacheCssSelectors[filter];
        }
        this.cacheCssSelectors[filter] = [];
        var sheets = document.styleSheets;
        for (var i = 0; i < sheets.length; i++) {
            var rules;
            try {
                // try...catch because Firefox not able to enumerate
                // document.styleSheets[].cssRules[] for cross-domain
                // stylesheets.
                rules = sheets[i].rules || sheets[i].cssRules;
            } catch (e) {
                console.warn("Can't read the css rules of: " + sheets[i].href, e);
                continue;
            }
            if (!rules) {
                continue;
            }

            for (var r = 0 ; r < rules.length ; r++) {
                var selectorText = rules[r].selectorText;
                if (!selectorText) {
                    continue;
                }
                var selectors = selectorText.split(/\s*,\s*/);
                var data = null;
                for (var s = 0; s < selectors.length; s++) {
                    var match = selectors[s].trim().match(filter);
                    if (!match) {
                        continue;
                    }
                    if (!data) {
                        data = {
                            selector: match[0],
                            css: rules[r].cssText.replace(/(^.*\{\s*)|(\s*\}\s*$)/g, ''),
                            names: [match[1]]
                        };
                    } else {
                        data.selector += (', ' + match[0]);
                        data.names.push(match[1]);
                    }
                }
                if (data) {
                    this.cacheCssSelectors[filter].push(data);
                }
            }
        }
        return this.cacheCssSelectors[filter];
    },
    /**
     * List of font icons to load by editor. The icons are displayed in the media
     * editor and identified like font and image (can be colored, spinned, resized
     * with fa classes).
     * To add font, push a new object {base, parser}
     *
     * - base: class who appear on all fonts
     * - parser: regular expression used to select all font in css stylesheets
     *
     * @type Array
     */
    fontIcons: [{base: 'fa', parser: /\.(fa-(?:\w|-)+)::?before/i}],
    /**
     * Searches the fonts described by the @see fontIcons variable.
     */
    computeFonts: _.once(function () {
        var self = this;
        _.each(this.fontIcons, function (data) {
            data.cssData = self.getCssSelectors(data.parser);
            data.alias = _.flatten(_.map(data.cssData, _.property('names')));
        });
    }),
    /**
     * If a widget needs to be instantiated on page loading, it needs to wait
     * for appropriate resources to be loaded. This function returns a Promise
     * which is resolved when the dom is ready, the session is bound
     * (translations loaded) and the XML is loaded. This should however not be
     * necessary anymore as widgets should not be parentless and should then be
     * instantiated (directly or not) by the page main component (webclient,
     * website root, editor bar, ...). The DOM will be ready then, the main
     * component is in charge of waiting for the session and the XML can be
     * lazy loaded thanks to the @see Widget.xmlDependencies key.
     *
     * @returns {Promise}
     */
    ready: function () {
        return Promise.all([domReady, session.is_bound, ajax.loadXML()]);
    },
};
});

//==============================================================================

odoo.define('web_editor.context', function (require) {
'use strict';

// TODO this should be re-removed as soon as possible.

function getContext(context) {
    var html = document.documentElement;
    return _.extend({
        lang: (html.getAttribute('lang') || 'en_US').replace('-', '_'),

        // Unfortunately this is a mention of 'website' in 'web_editor' as there
        // was no other way to do it as this was restored in a stable version.
        // Indeed, the editor is currently using this context at the root of JS
        // module, so there is no way for website to hook itself before
        // web_editor uses it (without a risky refactoring of web_editor in
        // stable). As mentioned above, the editor should not use this context
        // anymore anyway (this was restored by the saas-12.2 editor revert).
        'website_id': html.getAttribute('data-website-id') | 0,
    }, context || {});
}
function getExtraContext(context) {
    var html = document.documentElement;
    return _.extend(getContext(), {
        editable: !!(html.dataset.editable || $('[data-oe-model]').length), // temporary hack, this should be done in python
        translatable: !!html.dataset.translatable,
        edit_translations: !!html.dataset.edit_translations,
    }, context || {});
}

return {
    get: getContext,
    getExtra: getExtraContext,
};
});

//==============================================================================

odoo.define('web_editor.ready', function (require) {
    'use strict';
    // TODO this should be re-removed as soon as possible.
    var base = require('web_editor.base');
    return base.ready();
});

    var step_number = 0;
    var fee_step_sequence = 0;
    var fee_verified = false;
    var app_status = 'draft';
    odoo.define('odoocms_admission_portal.step_number', function (require) {
        "use strict";
        var ajax = require('web.ajax');
        var core = require('web.core');
        var session = require('web.session');
        var base = require('web_editor.base');
        var _t = core._t;
        base.url_translations = '/website/translations';

        var _t = core._t;
            $.ajax({
                url: "/get/step",
                method: "POST",
                dataType: "json",
                data: {},
                success: function (data) {
                    step_number = data.step_number;
                    fee_step_sequence = data.fee_step_sequence;
                    fee_verified = data.fee_verified;
                    app_status = data.app_status;

                    $("#odoocms_admission_portal").steps({
                        bodyTag: "fieldset",
                        headerTag: "h2",
                        transitionEffect: "slideLeft",
                        titleTemplate: "<span class='number'>#index#</span> #title#",
                        labels: {
                            finish: "Submit Form",
                            next: "Save & Next",
                            previous: "Go Back",
                            loading: "Loading...",
                            templete:"odoocms_admission_portal",
                        },
                        onStepChanging: function (event, currentIndex, newIndex){
                            if (currentIndex > newIndex){return true; }
                            var form = $(this);
                            if (currentIndex < newIndex){}
                            return form.valid();
                        },
                        onStepChanged: function (event, currentIndex, priorIndex){
                              if(currentIndex == fee_step_sequence && !fee_verified){
                                $("#wizard .actions a[href='#next']").hide();
                                $("a[href='#next']").hide();
                             }
                             else{
                                $("#wizard .actions a[href='#next']").show();
                                $("a[href='#next']").show();
                             }
                        },
                        startIndex: step_number,
                        onFinishing: function (event, currentIndex){
                            var form = $(this);
                            form.validate().settings.ignore = ":disabled";
                            return form.valid();
                        },
                        onFinished: function (event, currentIndex){
                            var form = $(this);
                            $("#wizard .actions a[href='#finish']").hide();
                            $("a[href='#finish']").hide();
                        }
                    }).validate({
                         errorClass: "state-error",
                         validClass: "state-success",
                         errorElement: "em",
                         onkeyup: false,
                         onclick: false,
                         rules: {
                             matricpercentage: {
                                 max: 100,
                                 min: data.matric_min,
                             },
                             interpercentage: {
                                 max: 100,
                                 min: data.inter_min,
                             },
                             a_level_percentage: {
                                 max: 100,
                                 min: data.a_level_min,
                             },
                             physics_marks_per: {
                                 max: 100,
                                 min: data.physics_per_min,
                             },
                             math_marks_per: {
                                 max: 100,
                                 min: data.math_per_min,
                             },
                             computer_marks_per: {
                                 max: 100,
                                 min: data.computer_per_min,
                             },
                             chemistry_marks_per: {
                                 max: 100,
                                 min: data.chemistry_per_min,
                             },

                         },
                         messages: {
                             matricpercentage: {
                                 max:  "Percentage can't be greater than 100. Please check your marks.",
                                 min:  "Marks should be at least " + data.matric_min + "%."
                             },
                             interpercentage: {
                                 max:  "Percentage can't be greater than 100. Please check your marks.",
                                 min:  "Marks should be at least " + data.inter_min + "%."
                             },
                             a_level_percentage: {
                                 max:  "Percentage can't be greater than 100. Please check your marks.",
                                 min:  "Marks should be at least " + data.a_level_min + "%."
                             },
                             physics_marks_per: {
                                 max:  "Percentage can't be greater than 100. Please check your marks.",
                                 min:  "Marks should be at least " + data.physics_per_min + "%."
                             },
                             math_marks_per: {
                                 max:  "Percentage can't be greater than 100. Please check your marks.",
                                 min:  "Marks should be at least " + data.math_per_min + "%."
                             },
                             computer_marks_per: {
                                 max:  "Percentage can't be greater than 100. Please check your marks.",
                                 min:  "Marks should be at least " + data.computer_per_min + "%."
                             },
                             chemistry_marks_per: {
                                 max:  "Percentage can't be greater than 100. Please check your marks.",
                                 min:  "Marks should be at least " + data.chemistry_per_min + "%."
                             },
                         },
                         highlight: function(element, errorClass, validClass) {
                             $(element).closest('.field').addClass(errorClass).removeClass(validClass);
                         },
                         unhighlight: function(element, errorClass, validClass) {
                             $(element).closest('.field').removeClass(errorClass).addClass(validClass);
                         },
                         errorPlacement: function(error, element) {
                             if (element.is(":radio") || element.is(":checkbox")) {
                                 element.closest('.option-group').after(error);
                             } else {
                                 error.insertAfter(element.parent());
                             }
                         }

                     });

                     if(step_number == fee_step_sequence && !fee_verified){
                        $("#wizard .actions a[href='#next']").hide();
                        $("a[href='#next']").hide();
                     }
                     if(app_status != 'draft'){
                        $("#wizard .actions a[href='#finish']").hide();
                        $("a[href='#finish']").hide();
                     }
                },
                error: function (error) {
                   step_number = 0;
                }
            });
	});

});

