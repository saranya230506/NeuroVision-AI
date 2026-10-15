/**
 * NeuroVision AI - Scan History & Record Management Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('history-search-input');
  const tableRows = document.querySelectorAll('.history-row');
  const clearHistoryBtn = document.getElementById('clear-history-btn');

  // Client-side quick filter
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      tableRows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
      });
    });
  }

  // Delete Individual Record
  document.querySelectorAll('.delete-record-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const recordId = btn.getAttribute('data-id');
      const patientName = btn.getAttribute('data-patient') || `#${recordId}`;

      if (!confirm(`Are you sure you want to delete diagnostic record for ${patientName}?`)) {
        return;
      }

      try {
        const res = await fetch(`/api/history/${recordId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
          const row = document.getElementById(`row-${recordId}`);
          if (row) {
            row.style.opacity = '0';
            setTimeout(() => row.remove(), 250);
          }
          window.showToast(`Record #${recordId} deleted successfully.`, 'success');
        } else {
          window.showToast(data.error || 'Failed to delete record.', 'error');
        }
      } catch (err) {
        console.error(err);
        window.showToast('Network error while attempting to delete record.', 'error');
      }
    });
  });

  // Clear All Records
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', async () => {
      if (!confirm('CAUTION: This will permanently delete all patient diagnostic records from the local SQLite database. Proceed?')) {
        return;
      }

      try {
        const res = await fetch('/api/history/clear', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          window.showToast('History purged successfully.', 'success');
          setTimeout(() => window.location.reload(), 1000);
        } else {
          window.showToast(data.error || 'Failed to purge history.', 'error');
        }
      } catch (err) {
        console.error(err);
        window.showToast('Network error while purging records.', 'error');
      }
    });
  }

});
