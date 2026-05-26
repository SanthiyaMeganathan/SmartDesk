const rowsPerPage = 5;
let currentPage = 1;
let allRows = [];
let filteredRows = [];

document.addEventListener('DOMContentLoaded', () => {
    const rowElements = document.querySelectorAll('.ticket-row');
    allRows = Array.from(rowElements);
    filteredRows = [...allRows];


    const searchInput = document.querySelector('.search-bar input');
    const selectAllCheckbox = document.getElementById('selectAll');
    const ticketCheckboxes = document.querySelectorAll('.ticket-checkbox');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase().trim();
            currentPage = 1; 

            filteredRows = allRows.filter(row => {
                const title = row.querySelector('.t-title') ? row.querySelector('.t-title').innerText.toLowerCase() : '';
                const email = row.querySelector('.t-email') ? row.querySelector('.t-email').innerText.toLowerCase() : '';
                const id = row.querySelector('.t-id') ? row.querySelector('.t-id').innerText.toLowerCase() : '';

                return title.includes(searchTerm) || email.includes(searchTerm) || id.includes(searchTerm);
            });

            renderTable();
        });
    }
    // -------------------------------------

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            ticketCheckboxes.forEach(cb => {
                if(cb.closest('.ticket-row').style.display !== 'none') {
                    cb.checked = e.target.checked;
                }
            });
        });
    }

    function renderTable() {
        const totalRows = filteredRows.length;
        const totalPages = Math.ceil(totalRows / rowsPerPage) || 1;

        allRows.forEach(row => row.style.display = 'none');

        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;

        filteredRows.forEach((row, index) => {
            if (index >= startIndex && index < endIndex) {
                row.style.display = '';
            }
        });
        if(selectAllCheckbox) selectAllCheckbox.checked = false;

        const currentEnd = Math.min(endIndex, totalRows);
        const currentStart = totalRows === 0 ? 0 : startIndex + 1;
        document.getElementById('pagination-info').innerText = `Showing ${currentStart}–${currentEnd} of ${totalRows} tickets`;
        document.getElementById('current-page-btn').innerText = currentPage;
        document.getElementById('prev-btn').disabled = currentPage === 1;
        document.getElementById('next-btn').disabled = currentPage === totalPages;
    }

    window.changePage = function(direction) {
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage) || 1;
        currentPage += direction;
        
        if (currentPage < 1) currentPage = 1;
        if (currentPage > totalPages) currentPage = totalPages;
        
        renderTable();
    };

    renderTable();
});