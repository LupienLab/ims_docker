function format(value) {
      return '<div>Description: ' + value + '</div>';
  }


$(document).ready(function () {

    var table = $('.data_table').DataTable({
    	 "order": [],
    });

    // Add event listener for opening and closing details
    $('.data_table').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        } else {
            // Open this row
            row.child(format(tr.data('child-value'))).show();
            tr.addClass('shown');
        }
    });

    if($('#id_json_type').val()){
    	callAjax();
    }

    $('#id_json_type').on('change',callAjax);

    function callAjax() {
    	var json_type_pk = $('#id_json_type').val();
		if(json_type_pk.length>0){
    	$.ajax({
		    url: "/addFields/",
		    type: "POST",
		    data: {
                'json_type_pk': json_type_pk,
            },
		    cache:false,
		    success: function(obj){
		    	$('#json_form_display').empty();
		    	$('#json_form_display').html(obj);
		    	addCalender();
		    	if($( "#json-data" ).length){
		    		var json_data = JSON.parse(document.getElementById('json-data').textContent);
		    		populate(json_data);
		    	}
		    	},
		    	error : function(xhr,errmsg,err) {
		    		$('#json_form_display').empty();
		            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
		                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
		            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		        }
    });
	}
	else{
		$('#json_form_display').empty();
	}
    }

    function populate(data) {
		  $.each(data, function(key, value){
		    $('[name='+key+']').val(value);
		  });
		}


	 if($('#id_choose_existing').val()){
    	existingCheck();
    }
	if(document.getElementById("id_choose_existing")){
	document.getElementById("id_choose_existing").onchange = function() {existingCheck()};
    }
    function existingCheck() {
    	var prevRequired = []
    	$('label.requiredField').each(function(){
    		prevRequired.push($(this).parent('div').attr('id'))
    	})
    	      if($("#id_choose_existing").val() !=""){
    	    	  $('#id_json_type').val("");
    	    	  callAjax();
    	    	  $("input").removeAttr("required" );
    	    	  $("input[name!='csrfmiddlewaretoken']").prop('disabled',true);
				          $(".select2-search__field").prop('disabled',false);
    	    	  $("select").removeAttr("required" );
    	    	  $("select:not(#id_choose_existing)").prop('disabled',true);
    	    	  $("textarea").prop('disabled',true);
    	    	  $(".asteriskField").remove();

            	  $("#id_choose_existing").prop('required',true);
            	  $("#div_id_choose_existing label").append( "<span class=\"asteriskField\">*</span>" );

    	      }
    	      else{
    	    	  $("#id_choose_existing").removeAttr("required" );
    	    	  $("#div_id_choose_existing .asteriskField").remove();
    	    	  $('input').prop('disabled',false);
    	    	  $('select').prop('disabled',false);
    	    	  $("textarea").prop('disabled',false);
    	    	  $.each( prevRequired, function( index, prev ){
    	    		    $("#" + prev +' input').prop('required',true);
    	    		    $("#" + prev +' select').prop('required',true);
    	    		    if ($("#" + prev +' label').children('span .asteriskField').length == 0) {
    	    		    	$("#" + prev +' label').append( "<span class=\"asteriskField\">*</span>" );
    	    		    }
    	    		});
    	      }
    	 }

    $( "<h5>Or Add New</h5>" ).insertAfter( "#div_id_choose_existing" );

    $('.jsontable').hide();
    $('.hide-show').click(function() {
       $('.jsontable').toggle();
    });
    addCalender();
    function addCalender() {
    $( ".dateinput" ).datepicker({
    	dateFormat:'yy-mm-dd',
    	changeMonth: true,
        changeYear: true
    });
    }

});
