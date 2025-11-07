function loadGrid() {
  // Get the current path from the browser
  const pathParts = window.location.pathname.split('/').filter(p => p);

  // Assuming the structure: /browseExperimentGrid/<disease>/<assay>/
  const diseaseSlug = encodeURIComponent(pathParts[1] || '');
  const assaySlug = encodeURIComponent(pathParts[2] || '');

  // Construct the API URL
  const apiUrl = `/api/experiments/${diseaseSlug}/${assaySlug}/`;

  fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      new gridjs.Grid({
        columns: [
          {
            // Empty column for detail control
            id: 'details',
            name: '',
            formatter: () => gridjs.html('<span class="details-control"></span>'),
            width: '5%',
          },
          {
            id: "project_name",
            name: "Project Name",
            formatter: (cell, row) => gridjs.html(
              `<a href="${row.cells[2].data}">${row.cells[1].data}</a>`
            )
          },
          { name: 'project_url', hidden: true },
          {
            id: "experiment_name",
            name: "Experiment Name",
            formatter: (cell, row) => gridjs.html(
              `<a href="${row.cells[4].data}">${row.cells[3].data}</a>`
            )
          },
          { name: 'experiment_url', hidden: true },
          {
            name: "tissue_type",
            formatter: cell => gridjs.html(cell.tissue_type?.replace(/\n/g, '<br/>'))
          },
          {
            name: "Disease-site",
            data: 'disease_site'
          },
          {
            name: "Assay",
            data: 'assay'
          },
          // Conditionally add Target column only if assay is ChIP-seq
          {
            name: "Target",
            data: 'target',
            hidden: true,  // You can toggle visibility dynamically depending on data
            formatter: cell => cell || ''
          },
          {
            name: "owner",
            data: 'owner'
          }
        ],
        data: data,
        search: true,
        sort: true,
        pagination: { enabled: true, limit: 10 }
      }).render(document.getElementById('gridjs-experiments'));
    });
}


// Load initial data on page load
$(document).ready(function () {

  loadGrid();
});
