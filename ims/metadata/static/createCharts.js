$(document).ready(function () {
  const autocolors = window['chartjs-plugin-autocolors'];
  Chart.register(autocolors);

  // Reusable function to create a pie chart with AJAX-fetched data
  function createPieChart(ctxId, ajaxUrl, labelKey, chartTitle, clickRedirectBase) {
    const ctx = document.getElementById(ctxId);
    if (!ctx) return;

    $.ajax({
      url: ajaxUrl,
      method: "POST",
      dataType: "json",
      success: function (data) {
        // Defensive: ensure data is an array
        if (!Array.isArray(data)) {
          data = JSON.parse(data);
        }

        const labels = data.map(item => item[labelKey] || "N/A");
        const values = data.map(item => item.dcount || 0);

        const chartInstance = new Chart(ctx, {
          type: 'pie',
          data: {
            labels: labels,
            datasets: [{
              data: values
            }]
          },
          options: {
            plugins: {
              title: {
                display: true,
                text: chartTitle
              },
              autocolors: {
                enabled: true,
                mode: 'data',
                offset: 10
              },
              legend: {
                position: "right"
              }
            },
            onClick: function (evt) {
              const activePoints = chartInstance.getElementsAtEventForMode(evt, 'point', chartInstance.options);
              if (!activePoints.length) return;
              const label = chartInstance.data.labels[activePoints[0].index];
              window.location = clickRedirectBase + label + "/";
            }
          }
        });
      },
      error: function (err) {
        console.error("Error loading chart data:", err);
      }
    });
  }

  // Call the reusable function for each chart
  // createPieChart('owner', '/populateCharts/owner/', 'created_by__first_name', 'Number of projects by Owner', '/browseProject/');
  // createPieChart('assay', '/populateCharts/assay/', 'exp_project__json_type__name', 'Number of experiments by Assay', '/browseProject/');
  // createPieChart('disease', '/populateCharts/disease/', 'disease_site__name', 'Number of projects by Disease', '/browseProject/');
  // createPieChart('projectlabel', '/populateCharts/status/', 'status', 'Number of projects by Status', '/browseProject/');
  //createPieChart('experimenttags', `/populateCharts/tags_${$("#project_id").val()}/`, 'name', 'Tags chart', '/detailExperimentTag/');


  const EXPERIMENT_COLUMNS = ['Disease-site', 'ATAC-seq', 'Hi-C', 'ChIP-seq', 'RNA-seq', 'scATAC', 'scATAC-RNAseq-multiome', 'BS-seq', 'Cut-Run', 'WGS', 'WES'];

  new gridjs.Grid({
    search: true,
    columns: EXPERIMENT_COLUMNS,
    sort: {
      multiColumn: false,
      server: {
        url: (prev, columns) => {
          if (!columns.length) return prev;
          const col = columns[0];
          const dir = col.direction === 1 ? 'True' : 'False';
          let colName = EXPERIMENT_COLUMNS[col.index];
          return `${prev}+${colName}+${dir}`;
        }
      }
    },
    server: {
      method: 'POST',
      url: '/populateCharts/grid',
      then: data => data.map((row) => {
        return Object.keys(row).map(key => {
          if (key === 'Disease-site') {
            return gridjs.html(`${row['Disease-site']}`);
          }
          return gridjs.html(`<a href='/browseExperimentGrid/${row['Disease-site']}/${key}'>${row[key]}</a>`);
        });
      }),
      handle: (res) => {
        if (res.status === 404) return { data: [] };
        if (res.ok) return res.json();
        throw Error('Grid data loading failed.');
      }
    },
    style: {
      container: {
        width: '100%',
        height: '100%'
      },
      table: {
        'min-width': '100%' // allows table to expand horizontally
      }
    },
    fixedHeader: true,   // keeps header visible on scroll
    autoWidth: true      // lets Grid.js calculate column widths dynamically
  }).render(document.getElementById("matrixDataGrid"));

  fetch('/api/active-projects/')
    .then(response => response.json())
    .then(data => {
      new gridjs.Grid({
        columns: [
          { name: 'url', hidden: true},
          {
            id: "name",
            name: 'Project Name',
            selector: row => row,
            formatter: (_, row) => gridjs.html(`<a href="${row.cells[0].data}">${row.cells[1].data}</a>`)
          }
        ],
        data: data,
        search: true,
        sort: true,
        pagination: { enabled: true, limit: 10 },
      }).render(document.getElementById('gridjs-active-projects'));
    });
});
