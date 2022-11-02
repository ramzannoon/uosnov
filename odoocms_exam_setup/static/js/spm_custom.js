

// custom callback
function notify_callback() {
    return alert('Notify closed!');
}

function executeCallback(callback) {
    window[callback]();
}

function showNotify(message,status,pos) {
    debugger;
    thisNotify = UIkit.notify({
        message: message,
        status:status,
        timeout: 5000,
        group: null,
        pos: pos,
    });
    if(
        (
            ($window.width() < 768)
            && (
                (thisNotify.options.pos == 'bottom-right')
                || (thisNotify.options.pos == 'bottom-left')
                || (thisNotify.options.pos == 'bottom-center')
            )
        )
        || (thisNotify.options.pos == 'bottom-right')
    ) {
        var thisNotify_height = $(thisNotify.element).outerHeight();
        var spacer = $window.width() < 768 ? -6 : 8;
        $body.find('.md-fab-wrapper').css('margin-bottom',thisNotify_height + spacer);
    }
}