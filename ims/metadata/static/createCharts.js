$(document).ready(function(){

var ctx2 = document.getElementById('owner');
if(ctx2){
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
}
/*##############*/
var ctx3 = document.getElementById('assay');
if(ctx3){
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
}
/*##############*/
var ctx1 = document.getElementById('disease');
if(ctx1){
$.ajax({
    url: "/populateCharts/disease/",
    method: "POST",
    success: function(data) {
	 d=JSON.parse(data);
     var chartlabel = [];
     var chartdata = [];
     for (var key in d) {
    var value = d[key]["disease_site__name"];
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
}
/*##############*/
var ctx4 = document.getElementById('projectlabel');
if(ctx4){
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
}
/*##############*/
var ctx5 = document.getElementById('experimenttags');
if(ctx5){
var project_id= $("#project_id").val();
$.ajax({
    url: "/populateCharts/tags_"+project_id+"/",
    method: "POST",
    success: function(data) {
	 d=JSON.parse(data);
     var chartlabel = [];
     var chartdata = [];
     for (var key in d) {
    var value = d[key]["name"];
    var ldata = d[key]["dcount"];
    chartlabel.push(value);
    chartdata.push(ldata);
	}
var experimenttags = new Chart(ctx5, {
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
            text: 'Tags chart'
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
		   var activePoints = experimenttags.getElementsAtEventForMode(evt, 'point', experimenttags.options);
		    var firstPoint = activePoints[0];
        	var label = experimenttags.data.labels[firstPoint._index];
       	    var value = experimenttags.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];
       		 window.location = "/detailExperimentTag/"+label+"/" ;

	    }
	}
});
},
    error: function(data) {
        console.log(data);
    }
});
}
/*##############*/
new gridjs.Grid({
  search: true,
  columns: ['Disease-site','ATAC-seq', 'Hi-C', 'ChIP-seq', 'RNA-seq', 'scATAC', 'scATAC-RNAseq-multiome', 'BS-seq','Cut-Run', 'WGS', 'WES'],
  sort: {
    multiColumn: false,
    server: {
      url: (prev, columns) => {
       if (!columns.length) return prev;

       const col = columns[0];
       const dir = col.direction === 1 ? 'True' : 'False';
       let colName = ['Disease-site','ATAC-seq', 'Hi-C', 'ChIP-seq', 'RNA-seq', 'scATAC', 'scATAC-RNAseq-multiome', 'BS-seq','Cut-Run','WGS', 'WES'][col.index];

       return `${prev}+${colName}+${dir}`;
     }
    }
  },
  server: {
	  method: 'POST',
    url: '/populateCharts/grid',
    then: data => data.map((card) => {

      console.log("card:", card)

      return card.map((value, index) => {
        console.log(value)
        if(index === 0) {
          return gridjs.html(`${value}`)
        } else {
          return gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${value['assay']}'>${value['value']}</a>`)
        }
      })

      // return [ gridjs.html(`${card[0]}`),
      //   gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${card[1]['assay]']}'>${card[1]}</a>`),
      //   gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${card[2]['assay]']}'>${card[2]}</a>`),
      //   gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${card[3]['assay]']}'>${card[3]}</a>`),
      //   gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${card[4]['assay]']}'>${card[4]}</a>`),
      //   gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${card[5]['assay]']}'>${card[5]}</a>`),
      //   gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${card[6]['assay]']}'>${card[6]}</a>`),
      //   gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${card[7]['assay]']}'>${card[7]}</a>`),
      //   gridjs.html(`<a href='/browseExperimentGrid/${card[0]}/${card[8]['assay]']}'>${card[8]}</a>`),
      // ]

    }
    ),
    handle: (res) => {
      // no matching records found
      if (res.status === 404) return {data: []};
      if (res.ok) return res.json();

      throw Error('oh no :(');
    },
  }
}).render(document.getElementById("matrixDataGrid"));

/*##############*/
});
