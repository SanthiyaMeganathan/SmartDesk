const rowsPerPage = 5;
let currentPage = 1;

document.addEventListener('DOMContentLoaded', () => {
    const rows = document.querySelectorAll('.ticket-row');
    const totalRows = rows.length;
    const totalPages = Math.ceil(totalRows / rowsPerPage) || 1;

    function renderTable() {
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        rows.forEach((row, index) => {
            if (index >= startIndex && index < endIndex) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });

        const currentEnd = Math.min(endIndex, totalRows);
        const currentStart = totalRows === 0 ? 0 : startIndex + 1;
        document.getElementById('pagination-info').innerText = `Showing ${currentStart}–${currentEnd} of ${totalRows} tickets`;
        document.getElementById('current-page-btn').innerText = currentPage;
        document.getElementById('prev-btn').disabled = currentPage === 1;
        document.getElementById('next-btn').disabled = currentPage === totalPages;
    }


    window.changePage = function(direction) {
        currentPage += direction;
        // Safety checks
        if (currentPage < 1) currentPage = 1;
        if (currentPage > totalPages) currentPage = totalPages;
        renderTable();
    };

    renderTable();
});