$(document).ready(function (e) {
    // Grading scheme
    $('input[type=radio][class=study_scheme]').on('change', function() {
     var grading_courses = $('#select_demo_1');
     var scheme_courses = $('#select_demo_2');

         switch($(this).val()) {
            case 'grade':
               grading_courses.removeAttr("disabled");
               grading_courses.prop("required", true);
               scheme_courses.removeAttr("required");
               scheme_courses.prop("disabled", true);
               scheme_courses.val('');
              break;
            case 'scheme':
              scheme_courses.removeAttr("disabled");
              scheme_courses.prop("required", true);
              grading_courses.prop("disabled", true);
              grading_courses.removeAttr("required");
              grading_courses.val('');
              break;
          }

});

  $("#dfsdf").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
      $.ajax({
           url: "/student/coursedrop/save",
         type: "POST",
         dataType: "json",
         data: formData,
beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
           processData:false,
         success: function(data)
          {
//            var $this = document.getElementById('create_assessment_button');
            showNotify('Created Successfully','success','top-right');
//             createAssessmentData(data);
//         setInterval(function() {$("#body-overlay-documents").hide(); },100);
         },
         error: function()
          {
            showNotify('Something went wrong!','danger','top-right');
          }
      });
   }));

});

function clearance_cancel_req(id) {
 var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/student/clearance/req/cancel",
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
                setTimeout(function(){location.reload()}, 3000);
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
function term_defer_del_req(id) {
        var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/student/term/defer/request/cancel",
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
                setTimeout(function(){location.reload()}, 3000);
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
function alternate_delete_req(id){
var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/student/request/alternate/course/delete",
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
                showNotify(data.message,'danger','top-right');
            }
             },
             error: function()
              {
                   showNotify('Something went wrong!','danger','top-right');
              }
          });
}
function retest_cancel_req(id) {
        var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/student/retest/req/cancel",
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
                showNotify(data.message,'danger','top-right');
            }
             },
             error: function()
              {
                   showNotify('Something went wrong!','danger','top-right');
              }
          });

}
function igrade_cancel_req(id) {
        var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/student/igrade/req/cancel",
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
                showNotify(data.message,'danger','top-right');
            }
             },
             error: function()
              {
                   showNotify('Something went wrong!','danger','top-right');
              }
          });

}
function degree_cancel_req(id) {
        var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/student/degree/req/cancel",
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
                showNotify(data.message,'danger','top-right');
            }
             },
             error: function()
              {
                   showNotify('Something went wrong!','danger','top-right');
              }
          });

}
function transcrip_cancel_req(id) {
        var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/student/transcript/req/cancel",
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
                showNotify(data.message,'danger','top-right');
            }
             },
             error: function()
              {
                   showNotify('Something went wrong!','danger','top-right');
              }
          });

}
function term_resume_del_req(id) {
        var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/student/term/resume/request/cancel",
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
                setTimeout(function(){location.reload()}, 3000);
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

function drop_req_del(id) {
    var formData = new FormData();
    formData.append('id',id);
    $.ajax({
         url: "/student/coursedrop/cancel",
         type: "POST",
         dataType: "json",
         data: formData,
         //  beforeSend: function(){$("#body-overlay-documents").show();},
         contentType: false,
         processData:false,
         success: function(data)
         {  if (data.status_is != 'Error'){
                showNotify('Deleted Successfully','warning','top-right');
                setTimeout(function(){location.reload()}, 3000);
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
function create_req_table(data){
    var assess_conf_table = document.getElementById('course_drop_table');
    $('#course_drop_table tbody').empty();
    var newRowContent = "<tr></tr>";
    var i;
    //        for (i=0; i< data['assessments'].length; i++){
    //         $("#course_drop_table tbody").append(newRowContent);
    //
    //        }
}

function course_req_del(id, course, course_type) {
    var formData = new FormData();
    formData.append('id',id);
    formData.append('course_type',course_type);
    formData.append('course',course);

    $.ajax({
         url: "/student/enrollment/cancel",
         type: "POST",
         dataType: "json",
         data: formData,
         //  beforeSend: function(){$("#body-overlay-documents").show();},
         contentType: false,
         processData:false,
         success: function(data)
         {
         if (data.status_is != 'Error'){
                showNotify('Deleted Successfully','warning','top-right');
                setTimeout(function(){location.reload()}, 3000);
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
