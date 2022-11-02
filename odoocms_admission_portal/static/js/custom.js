function alphaOnly(event) {
  var key = event.keyCode;
  return ((key >= 65 && key <= 90) || (key >= 97 && key <= 122) || (key == 32) || (key == 8) || (key == 9));
};
function on_change_test_center(id) {
    var formData = new FormData();
    formData.append('id',id)
    $.ajax({
        url: "/admissiononline/testcenter/change",
        type: "POST",
        dataType: "json",
        data: formData,
        contentType: false,
        processData:false,
        success: function(data)
        {
            if (data.test_type == 'pbt' && data.schedule.length > 0)
            {
                $("#test_schedule_div").show();
                $("#pbt").empty();
                $("#cbt").empty();
                //$("#pbt").append("<b>Test Type:</b>"+" "+"Paper Based Test"+"<br/><br/><br/>"+"<b>Test Date:</b>"+ " " + data.schedule[0].date + "<br/>" + "<b>Test Time:</b>" + " " + data.schedule[0].time );
                $("#pbt").append("<b>Test Type:</b>"+" "+"Paper Based Test"+"<br/><br/>"+"Please choose: <br/><br/>")
                for(i=0; i < data.schedule.length;i++){
                    $("#pbt").append(
                        "<input type='radio' required='true' onchange='on_change_test_time()' value='"+data.schedule[i].id+"'  name='test_timing' id='time"+i+"'>" + " " + "<b>Test Date:</b>"+ " " + data.schedule[i].date + "<b>Test Time:</b>" + " " + data.schedule[i].time + "<br/><br/>"
                    );
                }
           }
           else if(data.test_type == 'cbt' && data.schedule.length > 0)
           {
                $("#test_schedule_div").show();
                $("#cbt").empty();
                $("#pbt").empty();
                $("#cbt").append("<b>Test Type:</b>"+" "+"Computer Based Test"+"<br/><br/>"+"Please choose: <br/><br/>")
                for(i=0; i < data.schedule.length;i++){
                    $("#cbt").append(
                      "<input type='radio' required='true' onchange='on_change_test_time()' value='"+data.schedule[i].id+"' name='test_timing' id='time"+i+"'>" + " " + "<b>Test Date:</b>"+ " " + data.schedule[i].date + "<b>Test Time:</b>" + " " + data.schedule[i].time + "<br/><br/>"
                );
           }
           } else {
                $("#cbt").empty();
                $("#pbt").empty();
                $("#test_schedule_div").hide();
           }
        },
        error: function() {
            console.log('error');
        }
    });
}

function on_change_test_time(){
  var time = $("input[type='radio'][name='test_timing']:checked").val();
  var center = $("#test_center option:selected").val();
  console.log('sending');
   var formData = new FormData();
        formData.append('time_id',time)
         formData.append('center_id',center)
          $.ajax({
             url: "/admissiononline/testcenter/save",
             type: "POST",
             dataType: "json",
             data: formData,
             contentType: false,
             processData:false,
             success: function(data)
              {

            },
		  	error: function()
	    	{
	    	console.log('error');
	    	}
          });
  //console.log(rate_value);
}

function onchange_province(){
console.log('province_dom');
    province_id = document.getElementById('province_id').value
    var formData = new FormData();
    formData.append('province_id',province_id)
    $.ajax({
        url: "/admissiononline/province/change",
        type: "POST",
        dataType: "json",
        data: formData,
        contentType: false,
        processData:false,
        success: function(data){
            $("#domicile_id").empty();
            for(j=0; j< data.domiciles.length; j++){
               $("#domicile_id").append(" <option value="+data.domiciles[j].id+" > " + data.domiciles[j].name + "</option>");
            }
        }
    });
}

function discipline_program(id, current_dis=1){

    var formData = new FormData();
    formData.append('id',id)
    formData.append('current_dis', current_dis)
    $.ajax({
        url: "/admissiononline/discipline/change",
        type: "POST",
        dataType: "json",
        data: formData,
        contentType: false,
        processData:false,
        success: function(data){
          const element = document.getElementById("save_preference");
           const element2 = document.getElementById("save_preference_lbl");

          if(element){
                element2.style.display = "block";
               element.setAttribute('required',true);
               element.setAttribute('aria-required',true);
                                }

           if (data.discipline_programs != '' && data.current_dis == 1){
               $("#applicant_preferences_list").empty();
               var choices = `<div class='section colm colm4'>
                   <label for=''>Program Preference1*</label>
                   <label class="field select">
                       <select name="choice_1_1" id="choice_1_1" onchange="program_preference(my_id= this.value,1,1)" required="True">
                           <option value="" selected="Selected">None</option>
                       </select>
                       <i class="arrow double"></i>
                    </label>
               </div>`;
               $("#applicant_preferences_list").append(choices);
               for(j=0; j< data.discipline_programs.length; j++){
                       $("#choice_1_1").append(" <option value="+data.discipline_programs[j].id+" > " + data.discipline_programs[j].name + "</option>");
               }
               if ($('#more_discipline').length){
                    $('#more_discipline').prop('checked', false);
                    $('#div_more_discipline').empty();
               }

           } else if(data.discipline_programs != '' && data.current_dis == 2){
                $("#applicant_preferences_list_2").empty();
                var choices = `<div class='section colm colm4'>
                   <label for=''>Program Preference1*</label>
                   <label class="field select">
                            <select name="choice_2_1" id="choice_2_1" onchange="program_preference(my_id= this.value,2,1)" required="True">
                                <option value="" selected="Selected">None</option>
                            </select>
                            <i class="arrow double"></i>
                        </label>
                    </div>`;
                $("#applicant_preferences_list_2").append(choices);
                for(j=0; j< data.discipline_programs.length; j++){
                   $("#choice_2_1").append(" <option value="+data.discipline_programs[j].id+" > " + data.discipline_programs[j].name + "</option>");
                }
           } else if(data.discipline_programs != '' && $('#more_discipline').is(":checked")){
                $("#applicant_preferences_list_2").empty();
           } else {
               //$("#applicant_preferences_list").empty();
               $("#applicant_preferences_list_2").empty();
              // $("#more_discipline").prop("checked", false);
           }
        },
        error: function() {
            console.log('error');
        }
    });
}

function program_preference(program_id,discipline,choice){
    new_choice = choice + 1;
    var prev_prefer = $('#choice_'+discipline+'_'+choice).val();   // prev_pref is program
    var count_preference = document.getElementsByClassName('count_preference');

    for (k = 0; k <= count_preference.length - choice; k++) {
        if($('#choice_'+discipline+'_'+(choice+k+1)).length){
            $('#choice_'+discipline+'_'+(choice+k+1)+ ' option').remove();  // :not(:first)
        }
    }

    var length_ddl = document.querySelector("#choice_"+discipline+'_'+choice).length;  // remaining options
    if(length_ddl > 2){
        /*
        <div class="section colm colm4">
            <label for="choice_number">Choice<t t-esc="pref.preference"/>*</label>
            <label class="field select">
                <select t-attf-id="choice_{{pref.discipline_id.id}}_{{pref.preference}}"
                        name='choice_number'
                        t-attf-onchange="program_preference(program_id=this.value,{{pref.discipline_id.id}},{{pref.preference}})">
                    <option value="">None</option>
                    <option t-att-value="pref.program_id.id" selected="true">
                        <span t-esc="pref.program_id.name"/>
                    </option>
                </select>
                <i class="arrow double"/>
                <!--<input type="text" t-att-value="pref.program_id.name" readonly="true"/>-->
            </label>
        </div>
        */
        if(!($('#pref_'+discipline+'_'+new_choice).length)){
            var choices_list = "<div class='section colm colm4 count_preference' id='pref_"+discipline+'_'+new_choice+
                "'><label for='choice_number'>Program Preference"+new_choice+
                "*</label><label class='field select'><select id='choice_"+discipline+'_'+new_choice+
                "' name='choice_number' onchange='program_preference(program_id=this.value,"+discipline+","+new_choice+
                ")'></select><i class='arrow double'></i></label></div>";

            if(discipline == 1){
                $("#applicant_preferences_list").append(choices_list);
                $("#choice_"+discipline+"_"+new_choice).append($("#choice_"+discipline+"_"+choice).html());
                $("#choice_"+discipline+"_"+new_choice+" option[value="+prev_prefer+"]").remove();
            }
            else if(discipline == 2){
                $("#applicant_preferences_list_2").append(choices_list);
                $('#choice_'+discipline+'_'+new_choice).append($('#choice_'+discipline+'_'+choice).html());
                $("#choice_"+discipline+"_"+new_choice+" option[value="+prev_prefer+"]").remove();
           }
        } else{
            if(discipline == 1){
                $("#choice_"+discipline+"_"+new_choice).append($("#choice_"+discipline+"_"+choice).html());
                $("#choice_"+discipline+"_"+new_choice+" option[value="+prev_prefer+"]").remove();
            }
            else if(discipline == 2){
                $('#choice_'+discipline+'_'+new_choice).append($('#choice_'+discipline+'_'+choice).html());
                $("#choice_"+discipline+"_"+new_choice+" option[value="+prev_prefer+"]").remove();
           }
        }
    }

    var formData = new FormData();
    formData.append('program_id',program_id)
    formData.append('discipline_preference',discipline)
    formData.append('preference',choice)
    $.ajax({
         url: "/admission/discipline/preference/save",
         type: "POST",
         dataType: "json",
         data: formData,
         contentType: false,
         processData:false,
         success: function(data) {
         },
         error: function(){
            console.log('error');
         }
   });
}

// this para is removed from success
/* if (data.discipline_programs != '' && data.current_dis == 1)
               {    $("#applicant_preferences_list").empty();
               var choices = `<div class='section colm colm4'>
               <label for=''>Program Preference1*</label>
               <label class="field select">
                        <select name="choice_1_1" id="choice_1_1" onchange="program_preference(program_id= this.value,1,1)" required="True">
                            <option value="" selected="Selected">None</option>
                        </select>
                        <i class="arrow double"></i>
                    </label>
                </div>`;
               $("#applicant_preferences_list").append(choices);
                                for(j=0; j< data.discipline_programs.length; j++){
                       $("#choice_1_1").append(" <option value="+data.discipline_programs[j].id+" > " + data.discipline_programs[j].name + "</option>");
                        }
               }
               else if(data.discipline_programs != '' && data.current_dis == 2){
                 $("#applicant_preferences_list_2").empty();
                 var choices = `<div class='section colm colm4'>
               <label for=''>Program Preference1*</label>
               <label class="field select">
                        <select name="choice_2_1" id="choice_2_1" onchange="program_preference(program_id= this.value,2,1)" required="True">
                            <option value="" selected="Selected">None</option>
                        </select>
                        <i class="arrow double"></i>
                    </label>
                </div>`;
               $("#applicant_preferences_list_2").append(choices);
                                for(j=0; j< data.discipline_programs.length; j++){
                       $("#choice_2_1").append(" <option value="+data.discipline_programs[j].id+" > " + data.discipline_programs[j].name + "</option>");
                        }
               }
               else if(data.discipline_programs != '' && $('#more_discipline').is(":checked")){
               $("#applicant_preferences_list_2").empty();
               }
               else{
               //$("#applicant_preferences_list").empty();
               $("#applicant_preferences_list_2").empty();
              // $("#more_discipline").prop("checked", false);
               }*/

/*function test_center_save(id){
   var formData = new FormData();
        formData.append('test_center',id)
         formData.append('discipline_id',discipline)
         formData.append('preference',choice)
          $.ajax({
             url: "/admission/discipline/preference/save",
             type: "POST",
             dataType: "json",
             data: formData,
             contentType: false,
             processData:false,
             success: function(data)
              {

              *//* if (data.discipline_programs != '' && data.current_dis == 1)
               {    $("#applicant_preferences_list").empty();
               var choices = `<div class='section colm colm4'>
               <label for=''>Program Preference1*</label>
               <label class="field select">
                        <select name="choice_1_1" id="choice_1_1" onchange="program_preference(program_id= this.value,1,1)" required="True">
                            <option value="" selected="Selected">None</option>
                        </select>
                        <i class="arrow double"></i>
                    </label>
                </div>`;
               $("#applicant_preferences_list").append(choices);
                                for(j=0; j< data.discipline_programs.length; j++){
                       $("#choice_1_1").append(" <option value="+data.discipline_programs[j].id+" > " + data.discipline_programs[j].name + "</option>");
                        }
               }
               else if(data.discipline_programs != '' && data.current_dis == 2){
                 $("#applicant_preferences_list_2").empty();
                 var choices = `<div class='section colm colm4'>
               <label for=''>Program Preference1*</label>
               <label class="field select">
                        <select name="choice_2_1" id="choice_2_1" onchange="program_preference(program_id= this.value,2,1)" required="True">
                            <option value="" selected="Selected">None</option>
                        </select>
                        <i class="arrow double"></i>
                    </label>
                </div>`;
               $("#applicant_preferences_list_2").append(choices);
                                for(j=0; j< data.discipline_programs.length; j++){
                       $("#choice_2_1").append(" <option value="+data.discipline_programs[j].id+" > " + data.discipline_programs[j].name + "</option>");
                        }
               }
               else if(data.discipline_programs != '' && $('#more_discipline').is(":checked")){
               $("#applicant_preferences_list_2").empty();
               }
               else{
               //$("#applicant_preferences_list").empty();
               $("#applicant_preferences_list_2").empty();
              // $("#more_discipline").prop("checked", false);
               }*//*
            },
		  	error: function()
	    	{
	    	console.log('error');
	    	}
          });
}*/

