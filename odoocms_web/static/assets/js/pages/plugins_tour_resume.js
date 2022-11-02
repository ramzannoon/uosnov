$(function() {
  

    $('#restartTour').click(function() {
        altair_tour.init();
    })

});

altair_tour = {
    init: function() {
    
        // This tour guide is based on EnjoyHint plugin
        // for more info/documentation please check https://github.com/xbsoftware/enjoyhint

        // initialize instance
        var enjoyhint_instance = new EnjoyHint({});

        // config
        var enjoyhint_script_steps = [
            {
                "next #new_picture": 'Hi and welcome to Qalaam\'s Resume Builder. In this short tour guide we will show you<br>' +
                'some features regarding the Resume Builder Application<br>' +
                'For starters you can click on this button to upload your resume picture.<br>' +
                'Click "Next" to proceed.'
            },
            {
                "next #personal_information" : "Here you can see your personal information extracted from our Database.",
                shape : 'rectangle',
                radius: 30,
                showSkip: true
            },
            {
                "next #personal_edit_save" : "If you think the data is incorrect you can modify it from here.",
                shape : 'circle',
                radius: 25,
                showSkip: true
            },
            {
                "next #objectives_display" : "<div style='width:1000px; '><p class='grayout' style='font-size:17px;font-weight: bold;'>Guidelines</p><p></p><ul><li class='grayout'>Start with a strong trait, add 2 - 3 skills, describe your career goals, and say what you hope to do for the company.</li><li class='grayout'>State the position to which you're applying and use the name of the company.</li><li class='grayout'>Keep it short.</li></ul><p></p><p class='grayout' style='font-weight: bold;'>Sample: Secure a responsible career opportunity to fully utilize my training and skills, while making a significant contribution to the success of the company.</p></div>",
                showSkip: true
            },
            {
                "next #objectives_edit" : "Want to update or add your objectives? Click here",
                shape : 'circle',
                radius: 30,
                showSkip: false
            },
            {
                "next #professional_exp_display": "<div style='width:1000px; '><p class='grayout' style='font-size:17px;font-weight: bold;'>Guidelines:</p><p class='grayout'></p><ul><li class='grayout'>Please write 2-4 bullet points that list your responsibilities and achievements during the internship.</li><li class='grayout'>Focus on responsibilities that relate to the job you are applying for. For example, if you are applying for a writing job, mention how you wrote and published five articles during your internship. You don’t need to include your less relevant tasks, such as answering phones or photocopying.</li><p></p></ul></div>",                showSkip: false
            },
            { "next #professional_exp_add" : "Add your Internship experience here",
                shape : 'circle',
                radius: 30,
                showSkip: false

            },
                 { "next #education_display" : "<div style='width:1040px; '><p class='grayout' style='font-size:17px;font-weight: bold;'>Guidelines:</p><p class='grayout'>Please mention your FsC / A levels and Bachelors Degree details  below</p><p></p></div>",
               
                showSkip: false

            },

            { "key #professional_display" : "<div style='width:1040px; '><p class='grayout' style='font-size:17px;font-weight: bold;'>Guidelines:</p><p class='grayout'>Please mention your FYPs, semester projects , patents drafted / approved, publications below. </p></div>",               
                showSkip: true,
                "skipButton" : {text: "Finish"}

            }
        ];

        // set script config
        enjoyhint_instance.set(enjoyhint_script_steps);

        // run Enjoyhint script
        enjoyhint_instance.run();

        $('#restartTour').click(function() {
            console.log(enjoyhint_instance);
            // run Enjoyhint script
            enjoyhint_instance.run();
        })


    }
};