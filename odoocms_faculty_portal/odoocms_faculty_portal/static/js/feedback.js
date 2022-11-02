$(document).ready(function (e) {

   $('.highcharts-description').ready(function(e) {
     $.ajax({
         url: "/faculty/dashboard/feedback/self",
         type: "GET",
         dataType: "json",

         //beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
         processData:false,
         success: function(data)
          {
           console.log(data);
            var drillme = data.dr
             // var $this = document.getElementById('create_assessment_button');
            // showNotify('Created Successfully','success','top-right');
            Highcharts.chart('container', {
            chart: {
                type: 'column',
                events:{
             drilldown: function(e){
             var chart=this;
             var myValue = e;
             $('#faculty_comment_table > tbody').empty();
          for(var i=0; i< data.comments_fac_feed.length;i++){
               {
               /*
                   console.log(data.comments_fac_feed[i].id);
                   console.log(data.comments_fac_feed[i].title);
                   console.log(myValue.seriesOptions.title);
               */
              if (myValue.seriesOptions.id === data.comments_fac_feed[i].id){
              faculty_feedback_comments(data.comments_fac_feed[i]);
                }
                }
                    }
          for(var i=0; i< data.summary.length;i++){
          {
           console.log(data.summary[i].id);
          if (myValue.seriesOptions.id === data.summary[i].id){
           chart.setTitle(null,{
           text: "Score:" +data.summary[i].weightage + "," + "Rating:" + data.summary[i].rating + "," + "Registered:" + data.summary[i].total_registered + "," + "Responses:" + data.summary[i].answeres
           });}
            }
         }
      }
     }
    }
    ,
    title: {
        text: 'Teacher Evaluation'
    },
     subtitle: {
       // text: "Score:" +data.summary[0].weightage + "," + "Rating:" + data.summary[0].rating
    },

    accessibility: {
        announceNewData: {
            enabled: true
        }
    },
    xAxis: {
        type: 'category'
    },
    yAxis: {
        title: {
            text: 'Score'
        }
    },
    legend: {
        enabled: false
    },
    credits: {
    enabled: false
  },
    plotOptions: {
        series: {
            borderWidth: 0,
            dataLabels: {
                enabled: true,
                format: '{point.y:.1f}%'
            }
        }
    },
    tooltip: {
        headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b><br/>'
    },
    series:
       data.series
    ,
    drilldown:{ series:drillme }
});
//         setInterval(function() {$("#body-overlay-documents").hide(); },100);
         },
         error: function()
          {
//            showNotify('Something went wrong!','danger','top-right');
          }
         })
         })



    $('.highcharts-description').ready(function(e) {
      $.ajax({
         url: "/faculty/dashboard/feedback/course",
         type: "GET",
         dataType: "json",

// beforeSend: function(){ showNotify('Please wait !','warning','top-right');},
         contentType: false,
           processData:false,
         success: function(data)
          {
           console.log(data)
            var drillme = data.dr
//            showNotify('Created Successfully','success','top-right');
            Highcharts.chart('course', {
    chart: {
        type: 'column',
        events:{
     drilldown: function(e){
     var chart=this;
     var myValue = e;
    $('#course_comment_table > tbody').empty();
      console.log(myValue.seriesOptions.id);
          for(var i=0; i< data.comments_fac_course.length;i++){
      {
      /* console.log(data.comments_fac_course[i].id);

       console.log(data.comments_fac_course[i].title);

       console.log(myValue.seriesOptions.title);*/
      if (myValue.seriesOptions.id === data.comments_fac_course[i].id){
      course_feedback_comments(data.comments_fac_course[i]);
    }
    }
}
      for(var i=0; i< data.summary.length;i++){
      {
       console.log(data.summary[i].id);
      if (myValue.seriesOptions.id === data.summary[i].id){
       chart.setTitle(null,{
       text: "Score:" +data.summary[i].weightage + "," + "Rating:" + data.summary[i].rating + "," + "Registered:" + data.summary[i].total_registered + "," + "Responses:" + data.summary[i].answeres

       //feedback_comments(data);
       });
    }
    }
}
      }
     }
    }
    ,
    title: {
        text: 'Course Evaluation'
    },
     subtitle: {
       // text: "Score:" +data.summary[0].weightage + "," + "Rating:" + data.summary[0].rating
    },

    accessibility: {
        announceNewData: {
            enabled: true
        }
    },
    xAxis: {
        type: 'category'
    },
    yAxis: {
        title: {
            text: 'Score'
        }
    },
    legend: {
        enabled: false
    },
    credits: {
    enabled: false
  },
    plotOptions: {
        series: {
            borderWidth: 0,
            dataLabels: {
                enabled: true,
                format: '{point.y:.1f}%'
            }
        }
    },
    tooltip: {
        headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b><br/>'
    },
    series:
       data.series
    ,
    drilldown:{ series:drillme }

});
//         setInterval(function() {$("#body-overlay-documents").hide(); },100);
         },
         error: function()
          {
//            showNotify('Something went wrong!','danger','top-right');
          }
         })
         })

      //   UIkit.modal.alert('<h4 class="heading_b">Heading</h4><div>  Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusantium architecto corporis deleniti, eaque et excepturi facere, in ipsa modi nemo obcaecati pariatur, quas quibusdam repudiandae rerum. Aspernatur cumque id odit.</div>');
 });

function course_feedback_comments(comm) {
        console.log("feedback course comments");
        /*console.log(comm.comments);*/
        var comments_table = document.getElementById('course_comment_table');
        if(comm.comments != false){
        $("#course_comment_table > tbody").append("<tr><td>"+comm.comments+"</td></tr>");
        }
}
function faculty_feedback_comments(comm) {
        console.log("feedback fac comments");
        /*console.log(comm.comments);*/
        var faculty_comment_table = document.getElementById('faculty_comment_table');
        if(comm.comments != false){
        $("#faculty_comment_table > tbody").append("<tr><td>"+comm.comments+"</td></tr>");
        }
}