$(document).ready(function (e) {
});
function enrollment_cart_submit(){
   var formData = new FormData();
   $.ajax({
         url: "/student/enrollment/confirm",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
         {
         if (data.status_is != 'Error'){
                showNotify('Submitted Successfully','success','top-right');
                setTimeout(function(){location.replace("/student/enrollment/cart")}, 2000);
                //setTimeout(function(){location.reload()}, 3000);
            }
            else{
                showNotify(data.message,'danger','top-right');
            }
         },
         error: function()
          {
               showNotify('Something went wrong!','danger','top-right');
          }
    });
}
function course_req_del_card(id) {
    var formData = new FormData();
    formData.append('id',id);
    $.ajax({
         url: "/student/enrollment/cart/cancel",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
         {
         if (data.status_is != 'Error'){
                showNotify('Deleted Successfully','warning','top-right');
                setTimeout(function(){location.replace("/student/enrollment/cart")}, 2000);
                //setTimeout(function(){location.reload()}, 3000);
            }
            else{
                showNotify(data.message,'danger','top-right');
            }
         },
         error: function()
          {
               showNotify('Something went wrong!','danger','top-right');
          }
    });

}

function course_add_to_cart(id,type) {
        var formData = new FormData();
        formData.append('id',id);
        formData.append('course_type',type);
          $.ajax({
               url: "/student/enrollment/cart/save",
             type: "POST",
             dataType: "json",
             data: formData,
    beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
             contentType: false,
             processData:false,
             success: function(data)
              {
               if (data.status_is != 'Error'){
                 showNotify('Added to cart Successfully','success','top-right');
                 setTimeout(function(){location.replace("/student/enrollment/cards")}, 2000);
            }
            else{
                showNotify(data.message,'danger','top-right');
            }
             },
             error: function(data)
              {
                   showNotify('Unable to add course in cart','danger','top-right');
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