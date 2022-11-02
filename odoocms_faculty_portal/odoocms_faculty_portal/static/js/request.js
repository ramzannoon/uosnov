function industry_req_del(id){
var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/faculty/ic/placement/request/cancel",
             type: "POST",
             dataType: "json",
             data: formData,
    beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
             contentType: false,
               processData:false,
             success: function(data)
              {
               if (data.status_is != 'Error'){
                 showNotify('Request cancel successfully','warning','top-right');
                setTimeout(function(){location.reload()}, 2000);
            }
            else{
                showNotify(data.error_message,'danger','top-right');
            }
             },
             error: function()
              {
                   showNotify('Something went wrong!','danger','top-right');
              }
          });
}

// custom callback
function notify_callback() {
    return alert('Notify closed!');
}

function executeCallback(callback) {
    window[callback]();
}

function showNotify(message,status,pos) {
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