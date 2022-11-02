$(document).ready(function (e) {
  $("#profile_home_update").on('submit',(function(e) {
      e.preventDefault();
      console.log('fff');
      var formData = new FormData(this);
       $.ajax({
           url: "/faculty/profile/update/save",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           console.log('ddd');
           if (data.status_is != 'Error'){
                showNotify('Updated Successfully','success','top-right');
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
}));
$("#faculty_update_credential").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/faculty/credentials/reset/save",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)

           {
           if (data.status_is != 'Error'){
                showNotify('Password Updated Successfully','success','top-center');


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
$("#modal_nok_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Added Successfully','success','top-right');
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
}));
$("#modal_nok_update").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/update",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Updated Successfully','success','top-right');
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
}));
$("#faculty_update_credential").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/faculty/credentials/reset/save",
         type: "POST",
         dataType: "json",
         data: formData,
beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)

           {
           if (data.status_is != 'Error'){
                showNotify('Password Updated Successfully','success','top-center');


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
 $("#modal_passport_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Added Successfully','success','top-right');
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
}));
$("#modal_skills_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Added Successfully','success','top-right');
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
}));
$("#modal_cert_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Added Successfully','success','top-right');
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
}));
$("#modal_family_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Added Successfully','success','top-right');
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
}));
$("#modal_family_child_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Added Successfully','success','top-right');
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
}));
$("#modal_experience_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Added Successfully','success','top-right');
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
}));
$("#modal_acad_save").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
       $.ajax({
           url: "/simpleModel/add",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Added Successfully','success','top-right');
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
}));

});

function rec_del(id,simpleModel) {
 var formData = new FormData();
        formData.append('id',id)
        formData.append('genericModel',simpleModel)
          $.ajax({
               url: "/simpleModel/del",
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

function profileHomeEdit(){
   //document.getElementsByClassName('profile_default_fields').style.display='none';

    def = document.getElementsByClassName('profile_default_fields');
    ed = document.getElementsByClassName('profile_edit_fields');
    for (i = 0; i < def.length; i++) {
    def[i].style.display = 'none';
}
for (i = 0; i < ed.length; i++) {
    ed[i].style.display = 'block';
}

}


// Edit button enable
function onEdittable(id){

    //document.getElementById('nok_rec_input'+id).style.display = 'none';
    //document.getElementById('nok_rec_input'+id).style.display = 'block';
     $("#updatebutton_fms" ).removeClass("disabled");
    var a = document.getElementsByClassName('nok_rec'+id)
    var b = document.getElementsByClassName('nok_rec_input'+id)
    for(i = 0; i < a.length; i++) {
            a[i].style.display = 'none';
            b[i].style.display = 'block';
            }

}


// notify


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