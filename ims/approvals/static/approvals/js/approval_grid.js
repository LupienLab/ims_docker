document.addEventListener('DOMContentLoaded', function () {
  // Modal handlers (your existing code)
  const commentModal = document.getElementById('commentModal');
  const submitButton = document.getElementById('submitButton');
  const commentForm = document.getElementById('commentForm');
  const approvalIdInput = document.getElementById('approvalId');

  commentModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const approvalId = button.getAttribute('data-id');
    approvalIdInput.value = approvalId;
    const formAction = `/approvals/disapprove/${approvalId}/`;
    commentForm.setAttribute('action', formAction);
  });

  submitButton.addEventListener('click', function () {
    commentForm.submit();
  });

  const completeModal = document.getElementById('completeModal');
  const submitCompleteButton = document.getElementById('submitCompleteButton');
  const completeForm = document.getElementById('completeForm');
  const approvalCompleteId = document.getElementById('approvalCompleteId');

  completeModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const approvalId = button.getAttribute('data-id');
    approvalCompleteId.value = approvalId;
    const formAction = `/approvals/complete/${approvalId}/`;
    completeForm.setAttribute('action', formAction);
  });

  submitCompleteButton.addEventListener('click', function () {
    completeForm.submit();
  });

  const checkboxesContainer = document.getElementById('columnCheckboxes');
  if (checkboxesContainer) {

    // Common column names from your grids
    const allColumns = [
      'Title', 'User', 'Lab', 'Project', 'Experiments',
      'Document', 'Created At', 'Status', 'Actions',
      'Approved/Disapproved By', 'Approved/Disapproved At', 'Comment',
      'Completed By', 'Completed At', 'Completion Files'
    ];

    checkboxesContainer.innerHTML = allColumns.map(col => `
      <div class="form-check">
        <input class="form-check-input col-toggle" type="checkbox" id="col-${col}" data-col="${col}" checked>
        <label class="form-check-label" for="col-${col}">${col}</label>
      </div>
    `).join('');
  }

  // Parse approvals data
  const allApprovalsDataElement = document.getElementById('all-approvals-data');
  if (!allApprovalsDataElement) return;

  const allApprovals = JSON.parse(allApprovalsDataElement.textContent);
  window.grids = {}; // Store grid instances

  // Helper for HTML columns
  const htmlFormatter = (cell) => gridjs.html(cell || '');

  const numberedListFormatter = (cell) => {
    if (!cell) return '';
    // cell is expected to be a comma-separated string of HTML links
    const items = cell.split(',').map(item => item.trim());
    let html = '<ol>';
    for (const item of items) {
      html += `<li>${item}</li>`;
    }
    html += '</ol>';
    return gridjs.html(html);
  };

  const statusFormatter = (cell) => {
    if (!cell) return '';

    let html = ''
    switch (cell) {
      case 'Pending':
        html = `<span class="badge rounded-pill bg-warning">${cell}</span>`
        break;
      case 'Approved':
        html = `<span class="badge rounded-pill bg-success">${cell}</span>`
        break;
      case 'Disapproved':
        html = `<span class="badge rounded-pill bg-danger">${cell}</span>`
        break;
      case 'Completed':
        html = `<span class="badge rounded-pill bg-primary">${cell}</span>`
        break;
      default:
        html = `<span class="badge rounded-pill bg-info">${cell}</span>`
        break;
    }

    return gridjs.html(html)

  }

  function colorizeLabCells(tableId) {
    const labCells = document.querySelectorAll(`#${tableId} td[data-lab]`);
    const labMap = new Map();
    const labColors = [
      '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
      '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43',
      '#00b894', '#e17055', '#00cec9', '#fdcb6e', '#6c5ce7'
    ];

    // Assign unique colors to each lab
    labCells.forEach(td => {
      const lab = td.dataset.lab;
      if (!labMap.has(lab)) {
        labMap.set(lab, labMap.size % labColors.length);
      }
    });

    // Apply color to Lab cell only
    labCells.forEach(td => {
      const lab = td.dataset.lab;
      const color = labColors[labMap.get(lab)];
      td.style.backgroundColor = color;
      td.style.fontWeight = 'bold';
      td.style.borderRadius = '4px';
    });
  }

  // Column visibility helper
  function getVisibleColumns(gridColumns) {
    // On initial load, checkboxes don't exist yet - show ALL columns
    const checkboxes = document.querySelectorAll('.col-toggle:checked');
    if (checkboxes.length === 0) {
      // No checkboxes = initial load, return ALL column names as visible
      return new Set(gridColumns.map(col => typeof col === 'string' ? col : (col.name || col)));
    }

    // Checkboxes exist, use normal logic
    const visible = new Set();
    checkboxes.forEach(cb => visible.add(cb.dataset.col));
    return visible;
  }

  // Create grid with column visibility
  function createGrid(gridId, data, columns, tableClass = '') {
    const visibleColumns = getVisibleColumns(columns);

    const columnsWithVisibility = columns.map(col => {
      if (typeof col === 'string') {
        return { name: col, hidden: !visibleColumns.has(col), formatter: htmlFormatter };
      }
      col.hidden = !visibleColumns.has(col.name || col);
      return col;
    });

    window.grids[gridId] = new gridjs.Grid({
      columns: columnsWithVisibility,
      data: data,
      search: true,
      sort: true,
      pagination: { limit: 5 },
      className: {
        table: `table table-bordered table-hover table-sm ${tableClass}`,
      },
    });

    window.grids[gridId].render(document.getElementById(gridId));
    setTimeout(() => colorizeLabCells(gridId), 200);
  }

  // PENDING COLUMNS
  const pendingColumns = [
    "Title", "User",
    { name: "Lab", formatter: numberedListFormatter, attributes: (cell) => ({ 'data-lab': cell }) },
    { name: "Project", formatter: htmlFormatter },
    { name: "Experiments", formatter: numberedListFormatter },
    { name: "Document", formatter: htmlFormatter },
    "Created At",
    { name: "Status", formatter: statusFormatter },
    { name: "Actions", formatter: htmlFormatter }
  ];

  // Pending Grid (status === 'pending')
  const pendingData = allApprovals
    .filter(a => a.status === 'pending')
    .map(approval => [
      approval.title,
      approval.created_by_full_name,
      approval.lab,
      `<a href="${approval.project_url}">${approval.project_name}</a>`,
      approval.experiments_html,
      `<a href="${approval.document_url}" target="_blank">Download</a>`,
      approval.created_at,
      approval.status_display,
      approval.is_action_allowed ?
        `<div class="d-grid gap-2">
           <a href="${approval.approve_url}" class="btn btn-outline-success btn-sm">Approve</a>
           <button class="btn btn-outline-danger btn-sm" data-bs-toggle="modal" data-bs-target="#commentModal" data-id="${approval.id}">Disapprove</button>
         </div>` : ''
    ]);
  createGrid("pendingGrid", pendingData, pendingColumns);

  // const pendingGrid = new gridjs.Grid({
  //   columns: [
  //     "Title",
  //     "User",
  //     {
  //       name: "Lab",
  //       formatter: numberedListFormatter,
  //       attributes: (cell) => {
  //         if (cell) {
  //           return {
  //             'data-lab': cell
  //           }
  //         }
  //       }
  //     },
  //     {
  //       name: "Project",
  //       formatter: htmlFormatter
  //     },
  //     {
  //       name: "Experiments",
  //       formatter: numberedListFormatter
  //     },
  //     { name: "Document", formatter: htmlFormatter },
  //     "Created At",
  //     { name: "Status", formatter: statusFormatter },
  //     { name: "Actions", formatter: htmlFormatter }
  //   ],
  //   data: pendingData,
  //   search: true,
  //   sort: true,
  //   pagination: { limit: 5 },
  //   className: {
  //     table: 'table table-bordered table-hover table-sm',
  //   },
  // })

  // pendingGrid.render(document.getElementById("pendingGrid"));
  // setTimeout(() => colorizeLabCells('pendingGrid'), 200);

  // PROCESSED COLUMNS
  const processedColumns = [
    { name: "Title" }, { name: "User" },
    { name: "Lab", attributes: (cell) => ({ 'data-lab': cell }) },
    { name: "Project", formatter: htmlFormatter },
    { name: "Experiments", formatter: numberedListFormatter },
    { name: "Document", formatter: htmlFormatter },
    { name: "Created At" },
    { name: "Status", formatter: statusFormatter, attributes: (cell) => ({ 'data-status': cell }) },
    { name: "Approved/Disapproved By" }, { name: "Approved/Disapproved At" },
    { name: "Comment" }, { name: "Actions", formatter: htmlFormatter }
  ];

  // Processed Grid (status !== 'pending')
  const processedData = allApprovals
    .filter(a => a.status !== 'pending' && a.status !== 'completed')
    .map(approval => [
      approval.title,
      approval.created_by_full_name,
      approval.lab,
      `<a href="${approval.project_url}">${approval.project_name}</a>`,
      approval.experiments_html,
      `<a href="${approval.document_url}" target="_blank">Download</a>`,
      approval.created_at,
      approval.status_display,
      approval.approved_by_full_name,
      approval.approved_at,
      approval.comments,
      approval.is_complete_action_allowed ?
        `<div class="d-grid gap-2">
           <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#completeModal" data-id="${approval.id}">Complete</button>
         </div>` : ''
    ]);
  createGrid("processedGrid", processedData, processedColumns);

  // processedGrid = new gridjs.Grid({
  //   columns: [
  //     { name: "Title" },
  //     { name: "User" },
  //     { name: "Lab",
  //       attributes: (cell) => {
  //         if (cell) {
  //           return {
  //             'data-lab': cell
  //           }
  //         }
  //       }
  //     },
  //     {
  //       name: "Project",
  //       formatter: htmlFormatter
  //     },
  //     {
  //       name: "Experiments",
  //       formatter: numberedListFormatter,
  //     },
  //     { name: "Document", formatter: htmlFormatter },
  //     { name: "Created At"  },
  //     { name: "Status",
  //       formatter: statusFormatter,
  //       attributes: (cell) => {
  //         if(cell) {
  //           return {
  //             'data-status': cell
  //           }
  //         }
  //       }
  //     },
  //     { name: "Approved/Disapproved By"  },
  //     { name: "Approved/Disapproved At" },
  //     { name: "Comment"},
  //     { name: "Actions", formatter: htmlFormatter }
  //   ],
  //   data: processedData,
  //   search: true,
  //   sort: true,
  //   pagination: { limit: 5 },
  //   className: {
  //     table: 'table table-bordered table-hover table-sm',
  //     thead: 'table-dark'
  //   },
  // })

  // processedGrid.render(document.getElementById("processedGrid"));
  // setTimeout(() => colorizeLabCells('processedGrid'), 200);

  // COMPLETED COLUMNS
  const completedColumns = [
    "Title", "User",
    { name: "Lab", attributes: (cell) => ({ 'data-lab': cell }) },
    { name: "Project", formatter: htmlFormatter },
    { name: "Experiments", formatter: numberedListFormatter },
    { name: "Document", formatter: htmlFormatter },
    "Created At",
    { name: "Status", formatter: statusFormatter },
    "Approved/Disapproved By",
    "Approved/Disapproved At",
    "Completed By",
    "Completed At",
    "Completion Files"
  ];

  // Completed Grid (status == 'completed')
  const completedData = allApprovals
    .filter(a => a.status == 'completed')
    .map(approval => [
      approval.title,
      approval.created_by_full_name,
      approval.lab,
      `<a href="${approval.project_url}">${approval.project_name}</a>`,
      approval.experiments_html,
      `<a href="${approval.document_url}" target="_blank">Download</a>`,
      approval.created_at,
      approval.status_display,
      approval.approved_by_full_name,
      approval.approved_at,
      approval.completed_by_full_name,
      approval.completed_at,
      approval.completion_files_count > 0
        ? `<details><summary>${approval.completion_files_count} file${approval.completion_files_count > 1 ? 's' : ''}</summary>` +
        approval.completion_files.map(f =>
          `<div><a href="${f.file}" target="_blank">${f.filename}</a> ` +
          `<small>(${f.uploaded_at} by ${f.uploaded_by})</small></div>`
        ).join('') +
        `</details>`
        : 'None'
    ]);
  createGrid("completedGrid", completedData, completedColumns, 'table-striped');

  // COLUMN FILTER EVENT LISTENER
  document.getElementById('columnCheckboxes')?.addEventListener('change', function (e) {
    if (e.target.matches('.col-toggle')) {
      const gridId = document.querySelector('.tab-pane.active [id$="Grid"]').id;
      const grid = window.grids[gridId];
      if (grid) {
        const visibleColumns = getVisibleColumns(grid.config.columns);
        const updatedColumns = grid.config.columns.map(col => {
          if (typeof col === 'string') col = { name: col };
          col.hidden = !visibleColumns.has(col.name || col);
          return col;
        });
        grid.updateConfig({ columns: updatedColumns }).forceRender();
        setTimeout(() => colorizeLabCells(gridId), 200);
      }
    }
  });

  // Tab change handler
  document.getElementById('nav-tab')?.addEventListener('shown.bs.tab', function () {
    const activeGridId = document.querySelector('.tab-pane.active [id$="Grid"]').id;
    if (window.grids[activeGridId]) {
      const grid = window.grids[activeGridId];

      // Reapply column visibility based on current checkbox state
      const visibleColumns = getVisibleColumns(grid.config.columns);
      const updatedColumns = grid.config.columns.map(col => {
        if (typeof col === 'string') col = { name: col };
        col.hidden = !visibleColumns.has(col.name || col);
        return col;
      });

      grid.updateConfig({ columns: updatedColumns }).forceRender();
      setTimeout(() => colorizeLabCells(activeGridId), 200);
    }
  });
  // completedGrid = new gridjs.Grid({
  //   columns: [
  //     "Title",
  //     "User",
  //     {
  //       name: "Lab",
  //       attributes: (cell) => {
  //         if (cell) {
  //           return {
  //             'data-lab': cell
  //           }
  //         }
  //       }
  //     },
  //     {
  //       name: "Project",
  //       formatter: htmlFormatter
  //     },
  //     {
  //       name: "Experiments",
  //       formatter: numberedListFormatter
  //     },
  //     { name: "Document", formatter: htmlFormatter },
  //     "Created At",
  //     { name: "Status", formatter: statusFormatter },
  //     "Approved/Disapproved By",
  //     "Approved/Disapproved At",
  //   ],
  //   data: completedData,
  //   search: true,
  //   sort: true,
  //   pagination: { limit: 5 },
  //   className: {
  //     table: 'table table-bordered table-hover table-sm table-striped',
  //   }
  // })

  // completedGrid.render(document.getElementById("completedGrid"));
  // setTimeout(() => colorizeLabCells('completedGrid'), 200);
});
