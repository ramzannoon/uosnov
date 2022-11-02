$(function() {
    // set width for scrum board container
    altair_scrum_board.init();
    // draggable tasks
    altair_scrum_board.draggable_tasks();

    // filters
    var REGEX_EMAIL = '([a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*@' +
        '(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)';
    $('#select_filter').selectize({
        plugins: {
            'remove_button': {
                label: ''
            }
        },
        persist: false,
        maxItems: null,
        valueField: 'email',
        labelField: 'name',
        searchField: ['name', 'email'],
        options: [
            {email: 'brian@thirdroute.com', name: 'Brian Reavis'},
            {email: 'nikola@tesla.com', name: 'Nikola Tesla'},
            {email: 'someone@gmail.com'}
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                    (item.email ? '<span class="email">' + escape(item.email) + '</span>' : '') +
                    '</div>';
            },
            option: function(item, escape) {
                var label = item.name || item.email;
                var caption = item.name ? item.email : null;
                return '<div>' +
                    '<span class="label">' + escape(label) + '</span>' +
                    (caption ? '<span class="caption">' + escape(caption) + '</span>' : '') +
                    '</div>';
            }
        },
        createFilter: function(input) {
            var match, regex;

            // email@address.com
            regex = new RegExp('^' + REGEX_EMAIL + '$', 'i');
            match = input.match(regex);
            if (match) return !this.options.hasOwnProperty(match[0]);

            // name <email@address.com>
            regex = new RegExp('^([^<]*)\<' + REGEX_EMAIL + '\>$', 'i');
            match = input.match(regex);
            if (match) return !this.options.hasOwnProperty(match[2]);

            return false;
        },
        create: function(input) {
            if ((new RegExp('^' + REGEX_EMAIL + '$', 'i')).test(input)) {
                return {email: input};
            }
            var match = input.match(new RegExp('^([^<]*)\<' + REGEX_EMAIL + '\>$', 'i'));
            if (match) {
                return {
                    email : match[2],
                    name  : $.trim(match[1])
                };
            }
            alert('Invalid email address.');
            return false;
        },
        onDropdownOpen: function($dropdown) {
            $dropdown
                .hide()
                .velocity('slideDown', {
                    begin: function() {
                        $dropdown.css({'margin-top':'0'})
                    },
                    duration: 200,
                    easing: easing_swiftOut
                })
        },
        onDropdownClose: function($dropdown) {
            $dropdown
                .show()
                .velocity('slideUp', {
                    complete: function() {
                        $dropdown.css({'margin-top':''})
                    },
                    duration: 200,
                    easing: easing_swiftOut
                })
        }
    });
});

altair_scrum_board = {
    init: function() {
        var $scrumBoard = $('#scrum_board'),
            childWidth = $scrumBoard.children('div').width(),
            childsCount = $scrumBoard.children('div').length;

            $scrumBoard.width(childWidth * childsCount);
    },
    draggable_tasks: function() {

        var drake = dragula($('.scrum_column > div,.scrum_board_menu_inner').toArray());

        var containers = drake.containers,
            length = containers.length;

        for (var i = 0; i < length; i++) {
            $(containers[i]).addClass('dragula dragula-vertical');
        }

        drake.on('drop', function(el, target, source, sibling) {
            console.log(el);
            console.log(target);
            console.log(source);
        })

    }
};