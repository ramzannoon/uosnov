
$(document).ready(function (e) {
$("#resume_profile").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/student/resume/builder/profile",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)

           {
           if (data.status_is != 'Error'){
                showNotify('Updated Successfully','success','top-center');
                setTimeout(function(){location.replace("/student/resume/builder/home")}, 1500);
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
}));
$("#resume_objective").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/student/resume/builder/objective",
         type: "POST",
         dataType: "json",
         data: formData,
        beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Updated Successfully','success','top-center');
                setTimeout(function(){location.replace("/student/resume/builder/home")}, 1500);
            }
            else{
                showNotify(data.message,'danger','top-right');
          }
         },
         error: function()
          {
            showNotify('Something went wrong!','danger','bottom-right');
          }
      });
}));
/**Code for Professional Exp (Add/Edit)**/
$("#resume_exp_add").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/student/resume/builder/profExp/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)

           {
           if (data.status_is != 'Error'){
                 showNotify('Updated Successfully','success','top-center');
                setTimeout(function(){location.replace("/student/resume/builder/home")}, 1500);
            }
            else{
                showNotify(data.message,'danger','bottom-right');
          }
         },
         error: function()
          {
            showNotify('Something went wrong!','danger','bottom-right');
          }
      });
}));
/**Code for Projects (Add/Edit)**/
$("#modal_prof_accom_add_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/student/resume/builder/project/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)

           {
           if (data.status_is != 'Error'){
                 showNotify('Updated Successfully','success','top-center');
                setTimeout(function(){location.replace("/student/resume/builder/home")}, 1500);
            }
            else{
                showNotify(data.message,'danger','bottom-right');
          }
         },
         error: function()
          {
            showNotify('Something went wrong!','danger','bottom-right');
          }
      });
}));
$(".modal_personal_edu_update").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/student/resume/education/update",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)

           {
           if (data.status_is != 'Error'){
                 showNotify('Updated Successfully','success','top-center');
                setTimeout(function(){location.replace("/student/resume/builder/home")}, 1500);
            }
            else{
                showNotify(data.message,'danger','bottom-right');
          }
         },
         error: function()
          {
            showNotify('Something went wrong!','danger','bottom-right');
          }
      });
}));

$("#resume_reference").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/student/resume/reference/update",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)

           {
           if (data.status_is != 'Error'){
                 showNotify('Updated Successfully','success','top-center');
                setTimeout(function(){location.replace("/student/resume/builder/home")}, 1500);
            }
            else{
                showNotify(data.message,'danger','bottom-right');
          }
         },
         error: function()
          {
            showNotify('Something went wrong!','danger','bottom-right');
          }
      });
}));


});
function rec_del(id,simpleModel) {
 var formData = new FormData();
        formData.append('id',id)
        formData.append('genericModel',simpleModel)
          $.ajax({
               url: "/resume/del",
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
                setTimeout(function(){location.reload()}, 1500);
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

