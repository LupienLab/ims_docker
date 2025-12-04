let chartOwner;
let barChart;

function loadDropdown(url, selector, defaultOption) {
  $.ajax({
    url: url,
    method: 'GET',
    success: function (data) {
      const select = $(selector);
      select.empty();
      select.append(new Option(defaultOption, ''));
      data.forEach(item => {
        if(item.id) {
          select.append(new Option(item.name, item.id));
        } else {
          select.append(new Option(item, item));
        }
      });
    }
  });
}

function loadFilteredData() {
  const owner = $('#ownerFilter').val();
  const status = $('#statusFilter').val();
  const disease = $('#diseaseFilter').val();

  $.ajax({
    url: "/api/charts/owner/",
    method: "GET",
    data: { owner, status, disease },
    success: function (data) {
      const labels = data.owners.map(owner => owner.name);
      const ownerIdMap = data.owners.reduce((acc, owner) => {
        acc[owner.name] = owner.id;
        return acc;
      }, {});
      const diseases = data.diseases;
      const counts = data.counts;


      const datasets = diseases.map((disease, i) => ({
        label: disease,
        data: counts[disease]
      }));

      if (chartOwner) {
        chartOwner.data.labels = labels;
        chartOwner.data.datasets = datasets;
        chartOwner.update();
      } else {
        const ctx = document.getElementById('chartOwner').getContext('2d');
        chartOwner = new Chart(ctx, {
          type: 'bar',
          data: { labels, datasets },
          options: {
            responsive: true,
            scales: {
              x: { stacked: true },
              y: {
                stacked: true, beginAtZero: true,
                ticks: {
                  stepSize: 1,    // increments of 1 for whole numbers only
                  // Optional: You can also use a callback to further force rounding if needed
                  // callback: function(value) {
                  //   return Math.round(value);
                  // }
                }
              }
            },
            plugins: {
              title: { display: true, text: 'Projects by Owner and Disease Site' },
              legend: { position: 'top' },
              autocolors: {
                enabled: true,
                mode: 'dataset',
                offset: 1
              },
            },
            onClick: (evt) => {
              const activePoints = chartOwner.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, false);
              if (!activePoints.length) return;
              const firstPoint = activePoints[0];
              const datasetIndex = firstPoint.datasetIndex;
              const dataIndex = firstPoint.index;
              // Get the disease site (dataset label)
              const diseaseSite = chartOwner.data.datasets[datasetIndex].label;

              // Get owner label (x-axis label)
              const owner = chartOwner.data.labels[dataIndex];
              window.location.href = `/browseProject/${encodeURIComponent(diseaseSite)}/`;
            }
          }
        });
      }
    },
    error: function (err) {
      console.error('Error loading data', err);
    }
  });
}

function loadHorizontalBarChart() {
  $.ajax({
    url: '/api/charts/assay/',
    method: 'GET',
    success: function (data) {
      const labels = data.map(item => item.assay_type);
      const counts = data.map(item => item.dcount);

      const ctx = document.getElementById('horizontalBarChart').getContext('2d');

      if (barChart) {
        barChart.data.labels = labels;
        barChart.data.datasets[0].data = counts;
        barChart.update();
      } else {
        barChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Number of Experiments',
              data: counts,
              borderColor: 'white',
              borderWidth: 1
              // Do NOT set backgroundColor here for autocolors to work
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
              autocolors: { enabled: true, mode: 'data', offset: 1 },
              legend: { display: false },
              title: { display: true, text: 'Number of Experiments by Assay Type' }
            },
            scales: {
              x: {
                beginAtZero: true,
                ticks: { stepSize: 1 }
              },
              y: { beginAtZero: true }
            },
            onClick: (evt) => {
              const activePoints = barChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, false);
              if (!activePoints.length) return;
              const firstPoint = activePoints[0];
              const dataIndex = firstPoint.index;

              // Get owner label (x-axis label)
              const assayType = barChart.data.labels[dataIndex];
              window.location.href = `/browseProject/${encodeURIComponent(assayType)}/`;
            }
          }
        });
      }
    },
    error: function (err) {
      console.error('Failed to load assay chart data', err);
    }
  });
}

// Load initial data on page load
$(document).ready(function () {
  const autocolors = window['chartjs-plugin-autocolors'];
  Chart.register(autocolors);
  loadDropdown('/api/owners/', '#ownerFilter', 'All Owners');
  loadDropdown('/api/statuses/', '#statusFilter', 'All Statuses');
  loadDropdown('/api/diseases/', '#diseaseFilter', 'All Disease sites');
  loadFilteredData();
  loadHorizontalBarChart();

  // You may want to bind filter change event to reload data dynamically
  $('#ownerFilter, #statusFilter, #diseaseFilter').change(loadFilteredData);
});
