$(document).ready(function(){
	
	var ctx2 = document.getElementById('owner');
	$.ajax({
    url: "/populateCharts/owner/",
    method: "POST",
    success: function(data) {
	 d=JSON.parse(data);
     var chartlabel = [];
     var chartdata = [];
     for (var key in d) {
    var value = d[key]["created_by__first_name"];
    var ldata = d[key]["dcount"];
    chartlabel.push(value);
    chartdata.push(ldata);
	}
	
	var owner = new Chart(ctx2, {
    type: 'pie',
    data: {
        labels: chartlabel,
        datasets: [{
            data: chartdata
        }]
    },
	  options: {
		title: {
            display: true,
            text: 'Owner: Number of projects'
        },
		plugins: {
	      colorschemes: {
	        scheme: 'tableau.Tableau20'
	      }
        },
	    legend: {
	        display: false
	    },
	    'onClick' : function (evt) {
		   var activePoints = owner.getElementsAtEventForMode(evt, 'point', owner.options);
		    var firstPoint = activePoints[0];
        	var label = owner.data.labels[firstPoint._index];
       	    var value = owner.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];
            window.location = "/browseProject/"+label+"/" ;
                             
       		// alert(label + ": " + value);
		
	    }
	}
});
    },
    error: function(data) {
        console.log(data);
    }
});

/*##############*/
var ctx3 = document.getElementById('assay');
$.ajax({
    url: "/populateCharts/assay/",
    method: "POST",
    success: function(data) {
	 d=JSON.parse(data);
     var chartlabel = [];
     var chartdata = [];
     for (var key in d) {
    var value = d[key]["exp_project__json_type__name"];
    var ldata = d[key]["dcount"];
    chartlabel.push(value);
    chartdata.push(ldata);
	}
var assay = new Chart(ctx3, {
    type: 'pie',
    data: {
        labels: chartlabel,
        datasets: [{
            data: chartdata
        }]
    },
	  options: {
		title: {
            display: true,
            text: 'Assay: Number of experiments'
        },
		plugins: {
	      colorschemes: {
	        scheme: 'tableau.Tableau20'
	      }
        },
	    legend: {
	        display: false
	    },
	    'onClick' : function (evt) {
		   var activePoints = assay.getElementsAtEventForMode(evt, 'point', assay.options);
		    var firstPoint = activePoints[0];
        	var label = assay.data.labels[firstPoint._index];
       	    var value = assay.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];
       		window.location = "/browseProject/"+label+"/" ;
		
	    }
	}
});
},
    error: function(data) {
        console.log(data);
    }
});
/*##############*/
var ctx1 = document.getElementById('disease');
$.ajax({
    url: "/populateCharts/disease/",
    method: "POST",
    success: function(data) {
	 d=JSON.parse(data);
     var chartlabel = [];
     var chartdata = [];
     for (var key in d) {
    var value = d[key]["related__name"];
    var ldata = d[key]["dcount"];
    chartlabel.push(value);
    chartdata.push(ldata);
	}
var disease = new Chart(ctx1, {
    type: 'pie',
    data: {
        labels: chartlabel,
        datasets: [{
            data: chartdata
        }]
    },
	  options: {
		title: {
            display: true,
            text: 'Disease: Number of projects'
        },
		plugins: {
	      colorschemes: {
	        scheme: 'tableau.Tableau20'
	      }
        },
	    legend: {
	        display: false
	    },
	    'onClick' : function (evt) {
		   var activePoints = disease.getElementsAtEventForMode(evt, 'point', disease.options);
		    var firstPoint = activePoints[0];
        	var label = disease.data.labels[firstPoint._index];
       	    var value = disease.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];
       		 window.location = "/browseProject/"+label+"/" ;
		
	    }
	}
});
},
    error: function(data) {
        console.log(data);
    }
});
/*##############*/
var ctx4 = document.getElementById('projectlabel');
$.ajax({
    url: "/populateCharts/status/",
    method: "POST",
    success: function(data) {
	 d=JSON.parse(data);
     var chartlabel = [];
     var chartdata = [];
     for (var key in d) {
    var value = d[key]["status"];
    var ldata = d[key]["dcount"];
    chartlabel.push(value);
    chartdata.push(ldata);
	}
var projectlabel = new Chart(ctx4, {
    type: 'pie',
    data: {
        labels: chartlabel,
        datasets: [{
            data: chartdata
        }]
    },
	  options: {
		title: {
            display: true,
            text: 'Project status: Number of projects'
        },
		plugins: {
	      colorschemes: {
	        scheme: 'tableau.Tableau20'
	      }
        },
	    legend: {
	        display: false
	    },
	    'onClick' : function (evt) {
		   var activePoints = projectlabel.getElementsAtEventForMode(evt, 'point', projectlabel.options);
		    var firstPoint = activePoints[0];
        	var label = projectlabel.data.labels[firstPoint._index];
       	    var value = projectlabel.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];
       		 window.location = "/browseProject/"+label+"/" ;
		
	    }
	}
});
},
    error: function(data) {
        console.log(data);
    }
});

});

