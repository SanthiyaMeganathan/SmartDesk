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
    
    // Grab all filter dropdowns (Ensure your HTML selects have these IDs)
    const statusFilter = document.getElementById('status-filter');
    const categoryFilter = document.getElementById('category-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const dateFilter = document.getElementById('date-filter');

    function applyFilters() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
        
        // Handle dropdowns safely if they exist
        const sVal = statusFilter ? statusFilter.value : 'All';
        const cVal = categoryFilter ? categoryFilter.value : 'All';
        const pVal = priorityFilter ? priorityFilter.value : 'All';
        const dVal = dateFilter ? dateFilter.value : 'Date: All Time';

        // Date Boundaries
        const now = new Date();
        const dayOfWeek = now.getDay(); 
        const daysSinceMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1; 
        const startOfWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() - daysSinceMonday);
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
        const threeMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());

        filteredRows = allRows.filter(row => {
            // Search text
            const title = row.querySelector('.t-title') ? row.querySelector('.t-title').innerText.toLowerCase() : '';
            const email = row.querySelector('.t-email') ? row.querySelector('.t-email').innerText.toLowerCase() : '';
            const id = row.querySelector('.t-id') ? row.querySelector('.t-id').innerText.toLowerCase() : '';
            
            // Dropdown data
            const rStatus = row.getAttribute('data-status') || '';
            const rCat = row.getAttribute('data-category') || '';
            const rPri = row.getAttribute('data-priority') || '';
            const rDateStr = row.getAttribute('data-date');
            const rDate = rDateStr ? new Date(rDateStr) : new Date();

            // Match conditions
            let matchSearch = title.includes(searchTerm) || email.includes(searchTerm) || id.includes(searchTerm);
            let matchStatus = (sVal === 'All' || sVal === 'Status: All' || rStatus === sVal);
            let matchCat = (cVal === 'All' || cVal === 'Category: All' || rCat.toLowerCase() === cVal.toLowerCase());
            let matchPri = (pVal === 'All' || pVal === 'Priority: All' || rPri.toLowerCase() === pVal.toLowerCase());

            let matchDate = true;
            if (dVal !== 'All' && dVal !== 'Date: All Time' && rDateStr) {
                if (dVal === 'This week' && rDate < startOfWeek) matchDate = false;
                else if (dVal === 'This Month' && rDate < startOfMonth) matchDate = false;
                else if (dVal === 'Within 3 months' && rDate < threeMonthsAgo) matchDate = false;
            }

            return matchSearch && matchStatus && matchCat && matchPri && matchDate;
        });

        currentPage = 1; 
        renderTable();
    }

    // Attach listeners
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (statusFilter) statusFilter.addEventListener('change', applyFilters);
    if (categoryFilter) categoryFilter.addEventListener('change', applyFilters);
    if (priorityFilter) priorityFilter.addEventListener('change', applyFilters);
    if (dateFilter) dateFilter.addEventListener('change', applyFilters);

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
        
        const paginationInfo = document.getElementById('pagination-info');
        if (paginationInfo) paginationInfo.innerText = `Showing ${currentStart}–${currentEnd} of ${totalRows} tickets`;
        
        const currentPageBtn = document.getElementById('current-page-btn');
        if (currentPageBtn) currentPageBtn.innerText = currentPage;
        
        const prevBtn = document.getElementById('prev-btn');
        if (prevBtn) prevBtn.disabled = currentPage === 1;
        
        const nextBtn = document.getElementById('next-btn');
        if (nextBtn) nextBtn.disabled = currentPage === totalPages || totalPages === 0;
        
        window.totalPages = totalPages;
    }

    window.changePage = function(direction) {
        currentPage += direction;
        if (currentPage < 1) currentPage = 1;
        if (currentPage > window.totalPages) currentPage = window.totalPages;
        renderTable();
    };

    applyFilters();
});