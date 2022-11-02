

function selected_test_center(id) {
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