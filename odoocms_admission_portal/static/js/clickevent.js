// this is out of window.onload because it is applied on html with onchange attribute of form
function quota_change(id,code,name,application,check){
    var formData = new FormData();
    formData.append('qouta_id',id)
    formData.append('name',name)
    formData.append('code',code)
    formData.append('application_id',application)
    formData.append('check',check)
    $.ajax({
         url: "/admissiononline/quota/save",
         type: "POST",
         dataType: "json",
         data: formData,
         contentType: false,
         processData:false,
         success: function(data) {
         console.log('qouta saved');
         },
         error: function(){
            console.log('error');
         }
   });
}
function confirm_test_center(){
var formData = new FormData();
$.ajax({
        	url: "/confirm/test/center",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-voucher").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			$("#test_center").prop('disabled', 'disabled');
			$('input[name=test_timing]').attr("disabled",true);
			$('#test_center_lock').attr("disabled",true);
			},
		  	error: function(){
	    	}
	   });
}

function inter_pass_year_check(year){
var m = $("#matric_pass_year").val();

if(parseInt(m) >= year){
 alert('Matric passing year must be less then Inter passing year.')
}
}
function downloadVoucher(state) {
    $("#voucher_div_title").css("display", "block");
    $("#voucher_div").css("display", "block");
    if(state== 'no' || state == 'download'){
        $("#step_text_msg").html('Not Uploaded Yet');
    }
    else if(state== 'upload0'){
        $("#step_text_msg").html('Fee Submitted');
    }
    else if(state== 'upload'){
        $("#step_text_msg").html('Not Verified Yet');
    }
    else if(state== 'verify'){
        $("#step_text_msg").html('Already Verified');
    }
    else if(state== 'unverify'){
        $("#step_text_msg").html('Unverified');
    }
}

function showProfile_imagePreview(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
			$("#profile_image_target_layer").html('<img src="'+e.target.result+'" width="200px" height="200px" class="upload-preview" />');
			$("#profile_image_target_layer").css('opacity','0.8');
			$("#profile_image_target_layer2").html('<img src="'+e.target.result+'" width="200px" height="200px" class="upload-preview" />');
			$("#profile_image_target_layer2").css("display", "none");
			$(".icon-choose-image").css('opacity','0');
        }
		fileReader.readAsDataURL(objFileInput.files[0]);
		var formData = new FormData()
		formData.append('profile_image',objFileInput.files[0])
		$.ajax({
        	url: "/admissiononline/profileimage/save",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-voucher").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
		        var step_number = document.getElementById("step_number").value = data.step_number;
		        $("#profile_image_target_layer2").css("display", "block");
				$("#profile_image_target_layer").css("display", "none");
				$("#uploaded_profile_image").css("display", "none");
				$(".icon-choose-image").css('opacity','0.5');
			    setInterval(function() {$("#profile_photo_loading").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}

function showVoucherPreview(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("voucher_image_preview").src = e.target.result;
			$("#voucher_image_preview").css('opacity','0.8');
			document.getElementById("voucher_modal_image_preview").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData()
		formData.append('voucher_image',objFileInput.files[0])
		$.ajax({
                url: "/save/voucher",
                type: "POST",
                dataType: "json",
                data: formData,
                beforeSend: function(){$("#body-overlay-voucher").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    $("#step_text_msg").html('Image Uploaded');
			    $("#fee_voucher_state").html(data.fee_voucher_state);
			    setInterval(function() {$("#body-overlay-voucher").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}

function show_pre_matric(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("matric_scaned_copy").src = e.target.result;
			$("#matric_scaned_copy").css('opacity','0.8');
			document.getElementById("matric_scaned_copy_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('matric_scaned_copy',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_inter(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("inter_scaned_copy").src = e.target.result;
			$("#inter_scaned_copy").css('opacity','0.8');
			document.getElementById("inter_scaned_copy_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('inter_scaned_copy',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_domicile(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("domicile_scaned_copy").src = e.target.result;
			$("#domicile_scaned_copy").css('opacity','0.8');
			document.getElementById("domicile_scaned_copy_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('domicile_scaned_copy',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_salary_slip(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("salary_slip_scaned_copy").src = e.target.result;
			$("#salary_slip_scaned_copy").css('opacity','0.8');
			document.getElementById("salary_slip_scaned_copy_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('salary_slip_scaned_copy',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_test(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("test_certificate").src = e.target.result;
			$("#test_certificate").css('opacity','0.8');
			document.getElementById("test_certificate_copy_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('test_certificate',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_cnic(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("cnic_scanned_copy").src = e.target.result;
			$("#cnic_scanned_copy").css('opacity','0.8');
			document.getElementById("cnic_scanned_copy_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('cnic_scanned_copy',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_cnic_back(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("cnic_back_scanned_copy").src = e.target.result;
			$("#cnic_back_scanned_copy").css('opacity','0.8');
			document.getElementById("cnic_back_scanned_copy_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('cnic_back_scanned_copy',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_dae_first_year(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("dae_first_year").src = e.target.result;
			$("#dae_first_year").css('opacity','0.8');
			document.getElementById("dae_first_year_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('dae_first_year',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_dae_second_year(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("dae_second_year").src = e.target.result;
			$("#dae_second_year").css('opacity','0.8');
			document.getElementById("dae_second_year_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('dae_second_year',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_dae_third_year(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("dae_third_year").src = e.target.result;
			$("#dae_third_year").css('opacity','0.8');
			document.getElementById("dae_third_year_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('dae_third_year',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}
function show_pre_hope_certificate(objFileInput) {
    if (objFileInput.files[0]) {
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            $('#blah').attr('src', e.target.result);
            document.getElementById("hope_certificate_scanned_copy").src = e.target.result;
			$("#hope_certificate_scanned_copy").css('opacity','0.8');
			document.getElementById("hope_certificate_scanned_copy_modal_image").src = e.target.result;
        }
		fileReader.readAsDataURL(objFileInput.files[0]);

		var formData = new FormData();
		formData.append('hope_certificate_scanned_copy',objFileInput.files[0]);
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			dataType: "json",
			data: formData,
			beforeSend: function(){
			    $("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data){
			    setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function(){
	    	}
	   });
    }
}

function save_voucher_details() {
    voucher_number =document.getElementById('voucher_number').value
    voucher_date =document.getElementById('voucher_date').value
    fee_voucher_state = $("#fee_voucher_state").html()
    if (!(fee_voucher_state == 'upload0' || fee_voucher_state == 'upload')){
        alert('Please upload Invoice First!');
    }
    else if (voucher_number == ''){
        alert('Add Voucher number First!');
    }
    else if (voucher_date == ''){
        alert('Add Date First!');
    }
    else{
	   odoo.define('odoocms_admission_portal.voucher_details', function (require) {
			"use strict";
			var ajax = require('web.ajax');
			var core = require('web.core');
			var session = require('web.session');
			var base = require('web_editor.base');
			var _t = core._t;
			base.url_translations = '/website/translations';
			var _t = core._t;
            $.ajax({
                url: "/save/voucher/details",
                method: "POST",
                dataType: "json",
                data: {voucher_number:voucher_number,voucher_date:voucher_date},
                beforeSend: function(){$("#body-overlay-voucher").show();
			    },
                success: function (data) {
                    if (data.msg == 'not_uploaded'){
                        document.getElementById("step_text_msg").innerHTML = 'Please upload invoice picture first!';
                    }
                    else if (data.msg == 'no_info'){
                        document.getElementById("step_text_msg").innerHTML = 'Please enter Invoice detail first!';
                    }
                    else if (data.msg == 'success'){
                        document.getElementById("step_text_msg").innerHTML = 'Invoice details Submitted. You will be informed by email for next Step.';
                        //alert('Invoice details Submitted. You will be informed by email for next step.');
                        $("#voucher_div_title").css("display", "none");
                        $("#voucher_div").css("display", "none");
                    }
                    setInterval(function() {$("#body-overlay-voucher").hide(); },100);
                },
                error: function (error) {
                    alert('error: ' + error);
                }
            });
		});
    }
}

function on_change_dualNationality() {
    if ($('#is_dual_nationality').is(":checked"))
        {
         $("#passport_div").css("display", "block");
         $("#div_dual_nationality_country").css("display", "block");

        /* document.getElementById('test_type').value = 'SAT';
         document.getElementById('test_type').readOnly = true;*/
        }
    else{
        $("#passport_div").css("display", "none");
        $("#div_dual_nationality_country").css("display", "none");
       /* document.getElementById('test_type').readOnly = false;*/
    }

}

function on_change_is_any_disability() {
    if ($('#is_any_disability').is(":checked"))
        {
         $("#disability_div").css("display", "block");
        }
    else{
        $("#disability_div").css("display", "none");
    }

}

function on_change_is_any_disease() {
    if ($('#is_any_disease').is(":checked"))
        {
        $("#disease_div").css("display", "block");
        }
    else{
        $("#disease_div").css("display", "none");
    }

}

function on_change_is_forces_quota() {
    if ($('#is_forces_quota').is(":checked"))
        {
         $("#forces_quota_div").css("display", "block");
        }
    else{
        $("#forces_quota_div").css("display", "none");
    }

}

function on_change_is_is_rural_quota() {
    if ($('#is_rural_quota').is(":checked"))
        {
        $("#rural_quota_div").css("display", "block");
        }
    else{
        $("#rural_quota_div").css("display", "none");
    }

}


/*function student_province_change() {
    if (document.getElementById('province').value == 'Other')
        {
         $("#province_id2_div").css("display", "block");
        }
    else{
        $("#province_id2_div").css("display", "none");
    }

}*/
function change_present_country(){
 if (document.getElementById('present_country_id').value == '177')
        {
         document.getElementById('present_province_select_div').style.display = 'block';
         document.getElementById('present_province_id2_div').style.display = 'none';
        }
    else{
        //document.getElementById('domicile_div').style.display = 'none';
        document.getElementById('present_province_select_div').style.display = 'none';
        document.getElementById('present_province_id2_div').style.display = 'none';
    }
}
function onchange_per_country(){
 if (document.getElementById('per_country').value == '177')
        {
         document.getElementById('country_province').style.display = 'block';
         document.getElementById('country_province').style.display = 'block';
         document.getElementById('per_province_id2_div').style.display = 'none';
        }
    else{
        //document.getElementById('domicile_div').style.display = 'none';
        document.getElementById('country_province').style.display = 'none';
        document.getElementById('per_province_id2_div').style.display = 'none';
    }
}
function onchange_nationality() {
    if (document.getElementById('nationality').value == '177')
        {
         document.getElementById('domicile_div').style.display = 'block';
         document.getElementById('province_div').style.display = 'block';
         document.getElementById('province_div_2').style.display = 'none';
        }
    else{
        document.getElementById('domicile_div').style.display = 'none';
        document.getElementById('province_div').style.display = 'none';
        document.getElementById('province_div_2').style.display = 'block';
    }
}


function student_per_province_change() {
    if (document.getElementById('per_province').value == 'Other')
        {
         $("#per_province_id2_div").css("display", "block");
        }
    else{
        $("#per_province_id2_div").css("display", "none");
    }
}

function student_present_province_change() {
    if (document.getElementById('present_province').value == 'Other')
        {
         $("#present_province_id2_div").css("display", "block");
        }
    else{
        $("#present_province_id2_div").css("display", "none");
    }
}

function father_status_change() {
    if (document.getElementById('father_status').value == 'Deceased')
        {
         $("#guardian_div").css("display", "block");
        }
    else{
        $("#guardian_div").css("display", "none");
    }
}


$(document).ready(function (e) {
	$("#document_upload_form").on('submit',(function(e) {
		e.preventDefault();
		var formData = new FormData(this)
		$.ajax({
        	url: "/save/application/documents",
			type: "POST",
			data: formData,
			beforeSend: function(){$("#body-overlay-documents").show();
			},
			contentType: false,
    	    processData:false,
			success: function(data)
		    {
			setInterval(function() {$("#body-overlay-documents").hide(); },100);
			},
		  	error: function()
	    	{
	    	}
	   });
	}));
});

//verify ETA Data
function verifyETEAData(){
	var test_date = document.getElementById("test_date").value;
		var applicantID = document.getElementById("applicantID").value;
		var test_score = document.getElementById("test_score").value;
		var applicant_name = document.getElementById("applicant_name").value;
		if (test_date != "" && applicantID != "" && test_score != "" && applicant_name != "") {
			odoo.define('odoocms_admission_portal.clickevent', function (require) {
				"use strict";
				var ajax = require('web.ajax');
				var core = require('web.core');
				var session = require('web.session');
				var base = require('web_editor.base');
				var _t = core._t;
				base.url_translations = '/website/translations';
				var _t = core._t;

				// $(function () {
					$.ajax({
						url: "/entrytest/verfication",
						method: "POST",
						dataType: "json",
						data: {
							test_date: test_date, applicantID: applicantID, test_score: test_score
							, applicant_name: applicant_name
						},
						success: function (data) {
							if (data.status_is == "verified") {
								alert('verified!');
								document.getElementById("verify_entrytest").value = "Verified";
							} else {
								alert("Wrong details provided! please verify it again!");
							}
						},
						error: function (error) {
							alert('error: ' + error);
						}
					});
				// });
			});
		} else {
			alert('Please fill the details first!');
		}
}


//Final confirmation on checkBoxes
function finalConfirmation(){
	var final_confirmation = document.getElementById('final_confirmation');
	var final_agreement = document.getElementById('final_agreement');
	var final_terms_agreement = document.getElementById('final_terms_agreement');

	if (final_agreement.checked == true && final_terms_agreement.checked == true) {
		odoo.define('odoocms_admission_portal.clickevent', function (require) {
			"use strict";
			var ajax = require('web.ajax');
			var core = require('web.core');
			var session = require('web.session');
			var base = require('web_editor.base');
			var _t = core._t;
			base.url_translations = '/website/translations';
			var _t = core._t;

			// $(function () {
				$.ajax({
					url: "/application/change/state",
					method: "POST",
					dataType: "json",
					data: {},
					success: function (data) {
						if (data.state == "submit") {
							alert('submit!');
							window.location.href = "/admission/registration";
							//document.getElementById("verify_eta").value= "Verified";
						} else {
							alert("Somthing went wrong!");
						}
					},
					error: function (error) {
						alert('error: ' + error);
					}
				});
			// });
		});
	} else {
		alert("Please accept the conditions first!");
	}
}

function isSameAddressHide(){
    var checkBox_is_same_address = document.getElementById("is_same_address");

    if (checkBox_is_same_address.checked){
        document.getElementById('permanent_address_check').style.display='none';
    }
    else{
        document.getElementById('permanent_address_check').style.display='block';

    }
}

function isSameAddress(){
	var present_address = document.getElementById("present_address");
//	var street2 = document.getElementById("street2");
	var present_city = document.getElementById("present_city");
	var present_country_id = document.getElementById("country_id");
	var present_province = document.getElementById("present_province_id");
//	var present_province2 = document.getElementById("present_province2");

	var checkBox_is_same_address = document.getElementById("is_same_address");

	if(checkBox_is_same_address.checked){
			permanent_address.value = document.getElementById("present_address").value;
////			street2.value = document.getElementById("per_street2").value;
			city_permanent.value = document.getElementById("present_city").value;
		    console.log(123456, present_country_id.value = document.getElementById("country_id"))
//			permanent_country_id.value = document.getElementById("country_id").value;
//			permanent_province_id.value = document.getElementById("present_province_id").value;
//			present_province2.value = document.getElementById("per_province2").value;
//	        console.log(66666666666666666, document.getElementById("present_province_id"))
//	        console.log(66666666666666666, document.getElementById("present_province_id").value)
//
//			permanent_address.readOnly = true;
////			street2.readOnly = true;
//			city.readOnly = true;
//			present_country_id.readOnly = true;
//			present_province.readOnly = true;
//			present_province2.readOnly = true;
//            change_present_country();
		}
		else{
			console.log(666666666666666666)
			permanent_address.value = "";
//			street2.value = "";
			city_permanent.value = "";
//			permanent_country_id.value = "";
//			permanent_province_id.value = "";
//			present_province2.value = "";

//			permanent_address.readOnly = false;
//			street2.readOnly = false;
//			city_permanent.readOnly = false;
//			permanent_country_id.readOnly = false;
//			permanent_province_id.readOnly = false;
//			present_province2.readOnly = false;
		}
}

function closeFinalModal(){
	var final_modal = document.getElementById('final_data_id');
	final_modal.style.display = "none";

}

//Matric Percentage
function onchange_matric_marks() {
    var matrictotalmarks = document.getElementById('matrictotalmarks').value;
    var matricobtainedmarks = document.getElementById('matricobtainedmarks').value;
    if (matrictotalmarks != '' && matricobtainedmarks != '')
        {
         document.getElementById('matricpercentage').value = (matricobtainedmarks/matrictotalmarks*100).toFixed(2);
        }
}

//Olevel Percentage
function onchange_olevel_marks() {
    var oleveltotalmarks = document.getElementById('o-level-totalmarks').value;
    var olevelobtainedmarks = document.getElementById('o-level-obtainedmarks').value;
    if (oleveltotalmarks != '' && olevelobtainedmarks != '')
        {
        document.getElementById('o-level-percentage').value = (olevelobtainedmarks/oleveltotalmarks*100).toFixed(2);
        }
}

//Alevel Percentage
function onchange_alevel_marks() {
    var aleveltotalmarks = document.getElementById('a-level-totalmarks').value;
    var alevelobtainedmarks = document.getElementById('a-level-obtainedmarks').value;
    if (aleveltotalmarks != '' && alevelobtainedmarks != '')
        {
        document.getElementById('a-level-percentage').value = (alevelobtainedmarks/aleveltotalmarks*100).toFixed(2);
        }
}

//UG Percentage
function onchange_ug_cgpa() {
    var ug_total_cgpa = document.getElementById('ug_total_cgpa').value;
    var ug_obtained_cgpa = document.getElementById('ug_obtained_cgpa').value;
    if (ug_total_cgpa != '' && ug_obtained_cgpa != '')
        {
         document.getElementById('ug_cgpa_percentage').value = (ug_obtained_cgpa/ug_total_cgpa*100).toFixed(2);
        }
}

function compute_grades_total(){


    var grade_aa_marks = 90;
    var grade_a_marks = 85;
    var grade_b_marks = 80;
    var grade_c_marks = 75;
    var grade_d_marks = 70;
    var grade_e_marks = 65;
    var grade_f_marks = 60;
    var grade_g_marks = 55;

    var grade_aa = document.getElementById('grade_aa').value;
    var grade_a = document.getElementById('grade_a').value;
    var grade_b = document.getElementById('grade_b').value;
    var grade_c = document.getElementById('grade_c').value;
    var grade_d = document.getElementById('grade_d').value;
    var grade_e = document.getElementById('grade_e').value;
    var grade_f = document.getElementById('grade_f').value;
    var grade_g = document.getElementById('grade_g').value;

    var total_cal = (grade_aa * 100)+(grade_a * 100)+(grade_b * 100)+(grade_c * 100)+(grade_d * 100)+(grade_e * 100)+(grade_f * 100)+(grade_g * 100);
    var obtained_cal = (grade_aa * grade_aa_marks)+(grade_a * grade_a_marks)+(grade_b * grade_b_marks)+(grade_c * grade_c_marks)+(grade_d * grade_d_marks)+(grade_e * grade_e_marks)+(grade_f * grade_f_marks)+(grade_g * grade_g_marks);
    document.getElementById('o-level-total_cal').value = total_cal;
    document.getElementById('o-level-obtained_cal').value = obtained_cal;
    var total = 900;
    var obtained = (obtained_cal * total)/800;
    document.getElementById('o-level-totalmarks').value = total;
    document.getElementById('o-level-obtainedmarks').value = obtained;
    if (total>0){
        document.getElementById('o-level-percentage').value = (obtained/total*100).toFixed(2);
    }
    else{
        document.getElementById('o-level-percentage').value = 0.00;
    }

}


//For intermediate

function onchange_inter_result_status_complete(){

    var inter_result_status_complete = document.getElementById("inter_result_status_complete");

	if(inter_result_status_complete.checked){

	    var min_value = 50;
//	    $("#math_marks_per").attr({"min" : min_value});
//	    $("#physics_marks_per").attr({"min" : min_value});
//	    $("#add_math_marks_per").attr({"min" : min_value});
//	    $("#chemistry_marks_per").attr({"min" : min_value});
//	    $("#computer_marks_per").attr({"min" : min_value});
	    $("#interpercentage").attr({"min" : min_value});

//	    $("#a_level_physics_percentage").attr({"min" : min_value});
//	    $("#a_level_com_percentage").attr({"min" : min_value});
//	    $("#a_level_che_percentage").attr({"min" : min_value});
//	    $("#a_level_math_percentage").attr({"min" : min_value});
//	    $("#a_level_percentage").attr({"min" : min_value});

        req_fields2 = document.getElementsByClassName('fields_req');
        if(req_fields2){
         for (i = 0; i < req_fields2.length; i++) {
            req_fields2[i].setAttribute('aria-required',true);
            req_fields2[i].setAttribute('required',true);
        }
        }
	}
	else {
	    var min_value = 0;
//	    $("#math_marks_per").attr({"min" : min_value});
//	    $("#physics_marks_per").attr({"min" : min_value});
//	    $("#add_math_marks_per").attr({"min" : min_value});
//	    $("#chemistry_marks_per").attr({"min" : min_value});
//	    $("#computer_marks_per").attr({"min" : min_value});
	    $("#interpercentage").attr({"min" : min_value});

//	    $("#a_level_physics_percentage").attr({"min" : min_value});
//	    $("#a_level_com_percentage").attr({"min" : min_value});
//	    $("#a_level_che_percentage").attr({"min" : min_value});
//	    $("#a_level_math_percentage").attr({"min" : min_value});
//	    $("#a_level_percentage").attr({"min" : min_value});

	    req_fields = document.getElementsByClassName('fields_req');
        if(req_fields){
         for (i = 0; i < req_fields.length; i++) {
            req_fields[i].removeAttribute('aria-required');
            req_fields[i].removeAttribute('required');
        }
        }
	}

}
function onchange_inter_result_status_waiting(){

    var inter_result_status_waiting = document.getElementById("inter_result_status_waiting");

	if(inter_result_status_waiting.checked){

	    var min_value = 0;
//	    $("#math_marks_per").attr({"min" : min_value});
//	    $("#physics_marks_per").attr({"min" : min_value});
//	    $("#add_math_marks_per").attr({"min" : min_value});
//	    $("#chemistry_marks_per").attr({"min" : min_value});
//	    $("#computer_marks_per").attr({"min" : min_value});
	    $("#interpercentage").attr({"min" : min_value});

//	    $("#a_level_physics_percentage").attr({"min" : min_value});
//	    $("#a_level_com_percentage").attr({"min" : min_value});
//	    $("#a_level_che_percentage").attr({"min" : min_value});
//	    $("#a_level_math_percentage").attr({"min" : min_value});
//	    $("#a_level_percentage").attr({"min" : min_value});

        req_fields = document.getElementsByClassName('fields_req');
         if(req_fields){
         for (i = 0; i < req_fields.length; i++) {
            req_fields[i].removeAttribute('aria-required');
            req_fields[i].removeAttribute('required');
        }
        }
	}
	else {
	    var min_value = 50;
//	    $("#math_marks_per").attr({"min" : min_value});
//	    $("#physics_marks_per").attr({"min" : min_value});
//	    $("#add_math_marks_per").attr({"min" : min_value});
//	    $("#chemistry_marks_per").attr({"min" : min_value});
//	    $("#computer_marks_per").attr({"min" : min_value});
	    $("#interpercentage").attr({"min" : min_value});

//	    $("#a_level_physics_percentage").attr({"min" : min_value});
//	    $("#a_level_com_percentage").attr({"min" : min_value});
//	    $("#a_level_che_percentage").attr({"min" : min_value});
//	    $("#a_level_math_percentage").attr({"min" : min_value});
//	    $("#a_level_percentage").attr({"min" : min_value});
	     req_fields = document.getElementsByClassName('fields_req');
         if(req_fields){
         for (i = 0; i < req_fields.length; i++) {
            req_fields[i].setAttribute('aria-required',true);
            req_fields[i].setAttribute('required',true);
        }
        }
	}

}
function onchange_inter_marks() {
    var intertotalmarks = document.getElementById('intertotalmarks').value;
    var interbtainedmarks = document.getElementById('interbtainedmarks').value;
    if (matrictotalmarks != '' && matricobtainedmarks != '')
        {
         document.getElementById('interpercentage').value = (interbtainedmarks/intertotalmarks*100).toFixed(2);
        }
}

function compute_grades_inter_total(){
    console.log(111111111)
    var grade_aa_marks = 90;
    var grade_a_marks = 85;
    var grade_b_marks = 80;
    var grade_c_marks = 75;
    var grade_d_marks = 70;
    var grade_e_marks = 65;
    var grade_f_marks = 60;
    var grade_g_marks = 55;

    var grade_aa = document.getElementById('a_level_grade_aa').value;
    var grade_a = document.getElementById('a_level_grade_a').value;
    var grade_b = document.getElementById('a_level_grade_b').value;
    var grade_c = document.getElementById('a_level_grade_c').value;
    var grade_d = document.getElementById('a_level_grade_d').value;
    var grade_e = document.getElementById('a_level_grade_e').value;
    var grade_f = document.getElementById('a_level_grade_f').value;
    var grade_g = document.getElementById('a_level_grade_g').value;

    var total_cal = (grade_aa * 100)+(grade_a * 100)+(grade_b * 100)+(grade_c * 100)+(grade_d * 100)+(grade_e * 100)+(grade_f * 100)+(grade_g * 100);
    var obtained_cal = (grade_aa * grade_aa_marks)+(grade_a * grade_a_marks)+(grade_b * grade_b_marks)+(grade_c * grade_c_marks)+(grade_d * grade_d_marks)+(grade_e * grade_e_marks)+(grade_f * grade_f_marks)+(grade_g * grade_g_marks);
//    var total = parseInt(total_cal) + parseInt(document.getElementById('o-level-total_cal').value);
    var total = parseInt(total_cal);
//    var obtained = parseInt(obtained_cal) + parseInt(document.getElementById('o-level-obtained_cal').value);
    var obtained = parseInt(obtained_cal);

    document.getElementById('a_level_total').value = 1100;
    document.getElementById('a_level_obtained').value = (obtained * total)/1100;

    if (total>0){
        document.getElementById('a_level_percentage').value = (obtained/total*100).toFixed(2);
    }
    else{
        document.getElementById('a_level_percentage').value = 0.00;
    }
}

//function onchange_dae_inter(){
//    if (document.getElementById('inter_radio').checked == true){
//        document.getElementById('intermdiate_a_level_div').style.display='block';
//		document.getElementById('dae_div').style.display='none';
////		document.getElementById('inter_dae_degree').value='';
//    }
//    else{
//        document.getElementById('intermdiate_a_level_div').style.display='none';
//	    document.getElementById('dae_div').style.display='block';
////	    document.getElementById('inter_degree').value='';
//    }
//}

//function onchange_dae_inter2(){
//    if (document.getElementById('dae_radio').checked == true){
//        document.getElementById('intermdiate_a_level_div').style.display='none';
////		document.getElementById('dae_div').style.display='block';
////		document.getElementById('inter_degree').value='';
//    }
//    else{
//        document.getElementById('intermdiate_a_level_div').style.display='block';
////	    document.getElementById('dae_div').style.display='none';
////	    document.getElementById('inter_dae_degree').value='';
//    }
//}

function onchange_matric_o_level(){
    if (document.getElementById('matric_degree').value == 'O-Level'){
        document.getElementById('o-level_div').style.display = 'block';
        document.getElementById('matric_div').style.display = 'none';
    } else if (document.getElementById('matric_degree').value == 'Matric') {
        document.getElementById('matric_div').style.display = 'block';
        document.getElementById('o-level_div').style.display = 'none';
    }
}

function ugChecked(){
    if($('.check_ug').is(":checked")){
       $(".ug_education").show();
    } else
        $(".ug_education").hide();
  }

function onchange_inter_a_level(){
    if (document.getElementById('inter_degree').value == 'A-Level'){
        document.getElementById('intermediate_div').style.display = 'none';
		document.getElementById('a_level_div').style.display = 'block';
    } else if (document.getElementById('inter_degree').value == 'Intermediate') {
        document.getElementById('intermediate_div').style.display = 'block';
		document.getElementById('a_level_div').style.display = 'none';
    }
    onchange_inter_subjects();
}

function onchange_inter_subjects(){
    if (document.getElementById('inter_subject').value == 'Pre-Engineering'){
        document.getElementById('inter_comp_div').style.display = 'none';
        document.getElementById('inter_chem_div').style.display = 'block';
        document.getElementById('inter_math_div').style.display = 'block';
        document.getElementById('inter_add_math_div').style.display = 'none';
    } else if (document.getElementById('inter_subject').value == 'Pre-Medical') {
        document.getElementById('inter_comp_div').style.display = 'none';
        document.getElementById('inter_chem_div').style.display = 'block';
        document.getElementById('inter_math_div').style.display = 'none';
        document.getElementById('inter_add_math_div').style.display = 'block';
    } else if (document.getElementById('inter_subject').value == 'ICS') {
        document.getElementById('inter_chem_div').style.display = 'none';
        document.getElementById('inter_comp_div').style.display = 'block';
        document.getElementById('inter_math_div').style.display = 'block';
        document.getElementById('inter_add_math_div').style.display = 'none';
    }
}

//function math_grade_per(){
//    var grade_list = ['','A*','A','B','C','D','E','F','G'];
//    var per_list = [0,90,85,75,65,55,45,40,35];
//
//    var a_level = document.getElementById('a_level_math').value;
//    var ind = grade_list.indexOf(a_level);
//    document.getElementById('a_level_math_percentage').value = per_list[ind];
//}

function che_grade_per(){
    var grade_list = ['','A*','A','B','C','D','E','F','G'];
    var per_list = [0,90,85,75,65,55,45,40,35];

    var a_level = document.getElementById('a_level_che').value;
    var ind = grade_list.indexOf(a_level);
    document.getElementById('a_level_che_percentage').value = per_list[ind];

    if (a_level != ''){
        document.getElementById('test_total_marks').value = 2400;
        var obtained = document.getElementById('test_obtained_marks').value;
        if (obtained != '')
            {
             document.getElementById('test_percentage').value = (obtained/2400*100).toFixed(2);
            }
        else{
            document.getElementById('test_percentage').value = 0;
        }
         /*a_level = document.getElementById('a_level_com').value = '';
         document.getElementById('a_level_com_percentage').value = 0;*/
    }

    else if (a_level == ''){
        document.getElementById('test_total_marks').value = 1600;
        var obtained = document.getElementById('test_obtained_marks').value;
        if (obtained != '')
            {
             document.getElementById('test_percentage').value = (obtained/1600*100).toFixed(2);
            }
        else{
            document.getElementById('test_percentage').value = 0;
        }
        /*a_level = document.getElementById('a_level_com').value = 'G';
        document.getElementById('a_level_com_percentage').value = 35;*/
    }


}

//function com_grade_per(){
//    var grade_list = ['','A*','A','B','C','D','E','F','G'];
//    var per_list = [0,90,85,75,65,55,45,40,35];
//
//    var a_level = document.getElementById('a_level_com').value;
//    var ind = grade_list.indexOf(a_level);
//    document.getElementById('a_level_com_percentage').value = per_list[ind];
//
//    if (a_level != ''){
//
//        /*document.getElementById('a_level_che').value = '';
//        document.getElementById('a_level_che_percentage').value = 0;*/
//
//        document.getElementById('test_total_marks').value = 1600;
//        var obtained = document.getElementById('test_obtained_marks').value;
//        if (obtained != '')
//            {
//             document.getElementById('test_percentage').value = (obtained/1600*100).toFixed(2);
//            }
//        else{
//            document.getElementById('test_percentage').value = 0;
//        }
//    }
//
//    else if (a_level == ''){
//        document.getElementById('test_total_marks').value = 2400;
//        var obtained = document.getElementById('test_obtained_marks').value;
//        if (obtained != '')
//            {
//             document.getElementById('test_percentage').value = (obtained/2400*100).toFixed(2);
//            }
//        else{
//            document.getElementById('test_percentage').value = 0;
//        }
//
//        /*document.getElementById('a_level_che').value = 'G';
//        getElementById('a_level_che_percentage').value = 35;*/
//    }
//}

//function physics_grade_per(){
//    var grade_list = ['','A*','A','B','C','D','E','F','G'];
//    var per_list = [0,90,85,75,65,55,45,40,35];
//
//    var a_level_physics = document.getElementById('a_level_physics').value;
//    var ind = grade_list.indexOf(a_level_physics);
//    document.getElementById('a_level_physics_percentage').value = per_list[ind];
//}

//function compute_inter_ph_per() {
//    var total = document.getElementById('physics_total_marks').value;
//    var obtained = document.getElementById('physics_marks').value;
//    if (total != '' && obtained != '')
//        {
//         document.getElementById('physics_marks_per').value = (obtained/total*100).toFixed(2);
//        }
//}
//
//function compute_inter_math_per() {
//    var total = document.getElementById('math_total_marks').value;
//    var obtained = document.getElementById('math_marks').value;
//    if (total != '' && obtained != '')
//        {
//         document.getElementById('math_marks_per').value = (obtained/total*100).toFixed(2);
//        }
//}
//
//function compute_inter_add_math_per() {
//    var total = document.getElementById('add_math_total_marks').value;
//    var obtained = document.getElementById('add_math_marks').value;
//    if (total != '' && obtained != '')
//        {
//         document.getElementById('add_math_marks_per').value = (obtained/total*100).toFixed(2);
//        }
//}
//
//function compute_inter_che_per() {
//    var total = document.getElementById('chemistry_total_marks').value;
//    var obtained = document.getElementById('chemistry_marks').value;
//    if (total != '' && obtained != ''){
//        document.getElementById('chemistry_marks_per').value = (obtained/total*100).toFixed(2);
//    }
//}

//function compute_inter_com_per() {
//    var total = document.getElementById('computer_total_marks').value;
//    var obtained = document.getElementById('computer_marks').value;
//    if (total != '' && obtained != ''){
//        document.getElementById('computer_marks_per').value = (obtained/total*100).toFixed(2);
//    }
//}

//function dae_compute_inter_ph_per() {
//    var total = document.getElementById('dae_physics_total_marks').value;
//    var obtained = document.getElementById('dae_physics_marks').value;
//    if (total != '' && obtained != ''){
//        document.getElementById('dae_physics_marks_per').value = (obtained/total*100).toFixed(2);
//    }
//}
//
//function dae_compute_inter_math_per() {
//    var total = document.getElementById('dae_math_total_marks').value;
//    var obtained = document.getElementById('dae_math_marks').value;
//    if (total != '' && obtained != ''){
//        document.getElementById('dae_math_marks_per').value = (obtained/total*100).toFixed(2);
//    }
//}
//
//function dae_compute_inter_che_per() {
//    var total = document.getElementById('dae_chemistry_total_marks').value;
//    var obtained = document.getElementById('dae_chemistry_marks').value;
//    if (total != '' && obtained != ''){
//        document.getElementById('dae_chemistry_marks_per').value = (obtained/total*100).toFixed(2);
//    }
//}
//
//function compute_dae_percentage() {
//    var total = document.getElementById('dae_totalmarks').value;
//    var obtained = document.getElementById('dae_obtainedmarks').value;
//    if (total != '' && obtained != ''){
//        document.getElementById('dae_percentage').value = (obtained/total*100).toFixed(2);
//    }
//}

function compute_fy_percentage() {
    var total = document.getElementById('fy_totalmarks').value;
    var obtained = document.getElementById('fy_obtainedmarks').value;
    if (total != '' && obtained != ''){
        document.getElementById('fy_percentage').value = (obtained/total*100).toFixed(2);
    }
}
function compute_sd_y_percentage() {
    var total = document.getElementById('sd_y_totalmarks').value;
    var obtained = document.getElementById('sd_y_obtainedmarks').value;
    if (total != '' && obtained != ''){
        document.getElementById('sd_y_percentage').value = (obtained/total*100).toFixed(2);
    }
}
function compute_td_y_percentage() {
    var total = document.getElementById('td_y_totalmarks').value;
    var obtained = document.getElementById('td_y_obtainedmarks').value;
    if (total != '' && obtained != ''){
        document.getElementById('td_y_percentage').value = (obtained/total*100).toFixed(2);
    }
}

function onchange_test_marks(){
    var total = document.getElementById('test_total_marks').value;
    var obtained = document.getElementById('test_obtained_marks').value;
    if (obtained != ''){
        document.getElementById('test_percentage').value = (obtained/total*100).toFixed(2);
    }
    else{
        document.getElementById('test_percentage').value = 0;
    }
}

function onchange_gat_sat(test_tab){
    var test_type = document.getElementById('test_type').value;
    if(test_type){
    if (test_type == 'UET'){
        document.getElementById('sat_outer_div').style.display = 'none';
        document.getElementById('uet_message_div').style.display = 'block';
        if(test_tab !=''){
        test_tab = document.getElementById(test_tab)
        if(test_tab)
        test_tab.style.display = 'block';
        }
    } else{
        document.getElementById('sat_outer_div').style.display = 'block';
        document.getElementById('uet_message_div').style.display = 'none';
        if(test_tab){
         if(test_tab)
        test_tab.style.display = 'none';
        }
    }
    }
}

function confirm_application_form(){
   $.ajax({
        url: "/admission/online/confirm",
        type: "POST",
        dataType: "json",
        data: {},
        beforeSend: function(){
            $("#body-overlay-confirm").show();
        },
        contentType: false,
        processData:false,
        success: function(data){
            setInterval(function() {$("#body-overlay-confirm").hide(); },100);
            window.location.reload();
//			    window.location.href = "/admission/registration";
        },
        error: function(){
        }
    });
}

