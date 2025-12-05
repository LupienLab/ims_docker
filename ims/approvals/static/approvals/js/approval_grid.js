document.addEventListener('DOMContentLoaded', function () {
  // Modal handlers (your existing code)
  const commentModal = document.getElementById('commentModal');
  const submitButton = document.getElementById('submitButton');
  const commentForm = document.getElementById('commentForm');
  const approvalIdInput = document.getElementById('approvalId');

  commentModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const approvalId = button.getAttribute('data-id');
    const approvalTitle = button.getAttribute('data-title');
    approvalIdInput.value = approvalId;
    const formAction = `/approvals/disapprove/${approvalId}/`;
    commentForm.setAttribute('action', formAction);
  });

  submitButton.addEventListener('click', function () {
    commentForm.submit();
  });

  // Parse approvals data
  const allApprovalsDataElement = document.getElementById('all-approvals-data');
  if (!allApprovalsDataElement) return;

  const allApprovals = JSON.parse(allApprovalsDataElement.textContent);

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

  new gridjs.Grid({
    columns: [
      "Title",
      "User",
      "Lab",
      {
        name: "Project",
        formatter: htmlFormatter
      },
      {
        name: "Experiments",
        formatter: numberedListFormatter
      },
      { name: "Document", formatter: htmlFormatter },
      "Created At",
      "Status",
      { name: "Actions", formatter: htmlFormatter }
    ],
    data: pendingData,
    search: true,
    sort: true,
    pagination: { limit: 5 },
    className: {
      table: 'table table-bordered table-hover table-sm  table-striped',
      thead: 'table-dark'
    }
  }).render(document.getElementById("pendingGrid"));

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
           <a href="${approval.complete_url}" class="btn btn-outline-success btn-sm">Complete</a>
         </div>` : ''
    ]);

  new gridjs.Grid({
    columns: [
      { name: "Title" },
      { name: "User" },
      { name: "Lab"},
      {
        name: "Project",
        formatter: htmlFormatter
      },
      {
        name: "Experiments",
        formatter: numberedListFormatter,
      },
      { name: "Document", formatter: htmlFormatter },
      { name: "Created At"  },
      { name: "Status"  },
      { name: "Approved/Disapproved By"  },
      { name: "Approved/Disapproved At" },
      { name: "Comment"},
      { name: "Actions", formatter: htmlFormatter }
    ],
    data: processedData,
    search: true,
    sort: true,
    pagination: { limit: 5 },
    className: {
      table: 'table table-bordered table-hover table-sm',
      thead: 'table-dark'
    }
  }).render(document.getElementById("processedGrid"));

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
    ]);

  new gridjs.Grid({
    columns: [
      "Title",
      "User",
      "Lab",
      {
        name: "Project",
        formatter: htmlFormatter
      },
      {
        name: "Experiments",
        formatter: numberedListFormatter
      },
      { name: "Document", formatter: htmlFormatter },
      "Created At",
      "Status",
      "Approved/Disapproved By",
      "Approved/Disapproved At",
    ],
    data: completedData,
    search: true,
    sort: true,
    pagination: { limit: 5 },
    className: {
      table: 'table table-bordered table-hover table-sm table-success table-striped',
    }
  }).render(document.getElementById("completedGrid"));
});
