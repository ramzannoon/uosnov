$(document).ready(function (e) {

   $("#assessment_add_form").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
      $.ajax({
           url: "/faculty/assessment/configure/save",
         type: "POST",
         dataType: "json",
         data: formData,
beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
           processData:false,
         success: function(data)
          {
            var $this = document.getElementById('create_assessment_button');
            showNotify('Created Successfully','success','top-right');


//                 create_req_table(data);
            setInterval(function() {$("#body-overlay-documents").hide(); },100);
            location.reload();
           //  createAssessmentData(data);
//         setInterval(function() {$("#body-overlay-documents").hide(); },100);
         },
         error: function()
          {
            showNotify('Something went wrong!','danger','top-right');
          }
      });
   }));

   $("#upload_result_sheet").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
      $.ajax({
           url: "/result/sheet/upload",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
           processData:false,
         success: function(data)
          {
            if (data.status_is != 'Error'){
                showNotify('Saved Successfully','success','top-right');
                setTimeout(function(){location.reload()}, 5000);

            }
            else{
                showNotify(data.message,'danger','top-right');
            }

//         setInterval(function() {$("#body-overlay-documents").hide(); },100);
         },
         error: function()
          {
            showNotify('Something went wrong!','danger','top-right');
          }
      });
   }));

  $("#create_custom_class_shedule").on('submit',(function(e) {
      e.preventDefault();
      var formData = new FormData(this);
      $.ajax({
         url: "/faculty/class/save/schedule",
         type: "POST",
         dataType: "json",
         data: formData,
         beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
          success: function(data)
           {
           if (data.status_is != 'Error'){
                showNotify('Class Scheduled Successfully','success','top-right');
            }
            else{
                showNotify(data.error_message,'danger','top-right');
          }
         },
         error: function()
          {
            showNotify('Error occured during creation of class!','danger','top-right');
          }
      });
   }));
});
function updt_assessment(id){
var weightage = document.getElementById('ass_sub_weightage_'+id).value
var code = document.getElementById('ass_code_'+id).value
var name = document.getElementById('ass_name_'+id).value
var max_marks = document.getElementById('ass_max_marks_'+id).value
var assessmentdate = document.getElementById('classdate_'+id).value
var clo_id = document.getElementById('clo_id_'+id).value
var obe_weightage = document.getElementById('ass_obe_weightage_'+id).value
var visibility = document.getElementById('visibility_'+id).checked
var enable_obe = document.getElementById('add_obe_'+id).checked


 var formData = new FormData();
          formData.append('id',id);
          formData.append('weightage',weightage);
          formData.append('max_marks',max_marks);
          formData.append('name',name);
          formData.append('code',code);
          formData.append('assessmentdate',assessmentdate);
          formData.append('visibility',visibility);
          if(enable_obe){
          formData.append('enable_obe',enable_obe);
          formData.append('clo_id',clo_id);
          formData.append('obe_weightge',obe_weightage);
          }
          $.ajax({
             url: "/faculty/assessmentweightage/update",
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
//                 createAssessmentData(data);
            }
            else{
                showNotify(data.error_message,'danger','top-right');
            }

                // createAssessmentData(data);
    //         setInterval(function() {$("#body-overlay-documents").hide(); },100);
             },
             error: function()
              {
                   showNotify('Something wrong!','danger','top-right');
              }
          });
}
function del_assessment(id) {
        var formData = new FormData();
        formData.append('id',id)
          $.ajax({
               url: "/faculty/assessment/delete",
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
                setTimeout(function(){location.reload()}, 5000);
                 createAssessmentData(data);
            }
            else{

                showNotify(data.error_message,'danger','top-right');
            }
    //         setInterval(function() {$("#body-overlay-documents").hide(); },100);
             },
             error: function()
              {
              debugger;
                   showNotify('Something went wrong!','danger','top-right');
              }
          });

}

function update_sub_ass_button(){

}
function createAssessmentData(data) {

        var assess_conf_table = document.getElementById('table_assessment_conf');
        $('#table_assessment_conf tbody').empty();
        var newRowContent = "<tr></tr>";
        var i;
        for (i=0; i< data['assessments'].length; i++){
            $("#table_assessment_conf tbody").append(newRowContent);
           // if (data['assessments'][i]['assessment_len'] == 0){
                var last_column = '<td>' + '<a onclick="del_assessment('+ data['assessments'][i]['id']+')">'+'<i class="md-icon material-icons">'+'&#xE872;'+'</i>'
                                                                +'</a>'+'</td>'
           // }else{
                var last_column = '<td>' + '<span> N/A </span>'+'</td>'
          //  }
            assess_conf_table.children[1].children[i].innerHTML = '<td>'+data['assessments'][i]['assessment_type']+'</td>'+
                             '<td>'+data['assessments'][i]['name']+'</td>'+
                             '<td>'+data['assessments'][i]['code']+'</td>'+
                             '<td>'+data['assessments'][i]['max_marks']+'</td>'+
                             '<td>'+data['assessments'][i]['weightage']+'</td>'+
                             '<td>'+data['assessments'][i]['date']+'</td>'+
                             '<td>'+data['assessments'][i]['date_assessment']+'</td>'+
                             last_column
        }

}


function onEditAssComp(id){

    document.getElementById('ass_comp_weightage_'+id).style.display = 'none';
    document.getElementById('ass_comp_weightage_input_'+id).style.display = 'block';

   $("#update_assessment_weightage_button" ).removeClass("disabled");
}
function student_visibility_(id){
 var student_visibility = document.getElementsByName("student_visibility_"+id)[0].checked;
 var formData = new FormData();
 console.log('hi');
 formData.append('assessment_id',id)
  $.ajax({
             url: "/result/class/assessment/visibility",
             type: "POST",
             dataType: "json",
             data: formData,
             contentType: false,
             processData:false,
             success: function(data)
             {
               if (data.status_is != 'Error'){
                showNotify('Status Changed Successfully','success','top-right');
                setTimeout(function(){location.reload()}, 5000);
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
function include_in_gpa(id){
             var student_visibility = document.getElementsByName("student_visibility_"+id)[0].checked;
             var include_in_gpa = document.getElementsByName("include_in_gpa_"+id)[0].checked;
             var formData = new FormData();

             formData.append('student_visibility',student_visibility)
             formData.append('include_in_gpa',include_in_gpa)
             formData.append('assessment_id',id)

             $.ajax({
               url: "/result/class/grades/config/result/update",
             type: "POST",
             dataType: "json",
             data: formData,
             contentType: false,
               processData:false,
             success: function(data)
              {
               if (data.status_is != 'Error'){
                showNotify('Status Changed Successfully','success','top-right');
                setTimeout(function(){location.reload()}, 5000);

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

function updateTotal(){
    var weightage = 0;
    $.each($('.ass_comp_weightage'), function (index, value) {
        value = $(value)
        weightage += parseFloat (value.val());
        if(weightage > 100 || weightage < 100){
         document.getElementById('assessment_total_weightage').style.color = 'red';
         $("#update_assessment_weightage_button" ).addClass("disabled");
        }
        else{
        document.getElementById('assessment_total_weightage').style.color = 'black';
        $("#update_assessment_weightage_button" ).removeClass("disabled");
        }
    });
    document.getElementById('assessment_total_weightage').innerHTML = weightage
}

function assign_grades_submit(id){

 var formData = new FormData();
        formData.append('id',id)

          $.ajax({
               url: "/faculty/class/calculate/grades/id",
             type: "POST",
             dataType: "json",
             data: formData,
    beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
             contentType: false,
               processData:false,
             success: function(data)
              {

                 showNotify(data.message,data.color,'top-right');
                 setTimeout(function(){location.reload()}, 2000);

    //         setInterval(function() {$("#body-overlay-documents").hide(); },100);
             },
             error: function(data)
              {
                   showNotify(data.error_message,'danger','top-right');
              }
          });
}

function assign_xf_grades_submit(id){

 var formData = new FormData();
        formData.append('id',id)

          $.ajax({
               url: "/faculty/class/calculate/xf/grades/id",
             type: "POST",
             dataType: "json",
             data: formData,
    beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
             contentType: false,
               processData:false,
             success: function(data)
              {

                 showNotify(data.message,data.color,'top-right');
                 setTimeout(function(){location.reload()}, 2000);

    //         setInterval(function() {$("#body-overlay-documents").hide(); },100);
             },
             error: function(data)
              {
                   showNotify(data.error_message,'danger','top-right');
              }
          });
}

function final_result_submit(id){

 var formData = new FormData();
        formData.append('id',id)

          $.ajax({
               url: "/faculty/class/final/grades/id",
             type: "POST",
             dataType: "json",
             data: formData,
    beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
             contentType: false,
               processData:false,
             success: function(data)
              {

                 showNotify(data.message,data.color,'top-right');

    //         setInterval(function() {$("#body-overlay-documents").hide(); },100);
             },
             error: function(data)
              {
                   showNotify(data.error_message,'danger','top-right');
              }
          });
}



//$('#dt_default').DataTable( {
//    fixedColumns: true
//} );
//   $('#dt_default').DataTable( {
//       fixedColumns: {
//             leftColumns: 2
//                   }
//                 } );



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
        timeout: 6000,
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


 $(function() {
    // datatables
    altair_datatables.dt_default();
      altair_datatables.dt_grade();

});
       altair_datatables = {
          dt_default: function() {
        var $dt_default = $('#dt_default');
     //   if($dt_default.length) {
            $dt_default.DataTable( {

        scrollX:        true,
        scrollCollapse: true,
        paging:         true,
        fixedColumns: {
                leftColumns: 1
            },

    } );

       // }

    },
     dt_grade: function() {
        var $dt_grade = $('#dt_grade');
     //   if($dt_default.length) {
            $dt_grade.DataTable( {

        scrollX:        false,
        scrollCollapse: true,
        paging:         true,

    } );

       // }

    },
                    };