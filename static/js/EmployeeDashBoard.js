const rowsPerPage = 5;
let currentPage = 1;
let filteredRows = [];

document.addEventListener('DOMContentLoaded', () => {
    // Grab all rows and convert to an array for easy filtering
    const allRows = Array.from(document.querySelectorAll('.ticket-row'));
    
    // Grab all filter dropdowns
    const statusFilter = document.getElementById('status-filter');
    const categoryFilter = document.getElementById('category-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const dateFilter = document.getElementById('date-filter');

    // Function to apply filters and update the filteredRows array
    function applyFilters() {
        const sVal = statusFilter.value;
        const cVal = categoryFilter.value;
        const pVal = priorityFilter.value;
        const dVal = dateFilter.value;

        // Get current date boundaries
        const now = new Date();
        
        // 1. Calculate Start of This Week (Assuming Monday is the first day of the week)
        const dayOfWeek = now.getDay(); 
        const daysSinceMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // 0 is Sunday
        const startOfWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() - daysSinceMonday);
        
        // 2. Calculate Start of This Month
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

        // 3. Calculate 3 Months Ago (Exact calendar date 3 months back)
        const threeMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());

        filteredRows = allRows.filter(row => {
            const rStatus = row.getAttribute('data-status');
            const rCat = row.getAttribute('data-category');
            const rPri = row.getAttribute('data-priority');
            const rDateStr = row.getAttribute('data-date');
            
            const rDate = rDateStr ? new Date(rDateStr) : new Date();

            let matchStatus = (sVal === 'All' || rStatus === sVal);
            let matchCat = (cVal === 'All' || rCat.toLowerCase() === cVal.toLowerCase());
            let matchPri = (pVal === 'All' || rPri.toLowerCase() === pVal.toLowerCase());

            // Calendar-based Date Filtering
            let matchDate = true;
            if (dVal !== 'All' && rDateStr) {
                if (dVal === 'This week' && rDate < startOfWeek) {
                    matchDate = false;
                } else if (dVal === 'This Month' && rDate < startOfMonth) {
                    matchDate = false;
                } else if (dVal === 'Within 3 months' && rDate < threeMonthsAgo) {
                    matchDate = false;
                }
            }

            return matchStatus && matchCat && matchPri && matchDate;
        });

        currentPage = 1; // Always reset to page 1 when a new filter is applied
        renderTable();
    }

    function renderTable() {
        // Hide everything first
        allRows.forEach(row => row.style.display = 'none');

        const totalRows = filteredRows.length;
        const totalPages = Math.ceil(totalRows / rowsPerPage) || 1;

        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;

        // Show only the rows that match the filter for the current page
        filteredRows.forEach((row, index) => {
            if (index >= startIndex && index < endIndex) {
                row.style.display = '';
            }
        });

        const currentEnd = Math.min(endIndex, totalRows);
        const currentStart = totalRows === 0 ? 0 : startIndex + 1;
        
        document.getElementById('pagination-info').innerText = `Showing ${currentStart}–${currentEnd} of ${totalRows} tickets`;
        document.getElementById('current-page-btn').innerText = currentPage;
        document.getElementById('prev-btn').disabled = currentPage === 1;
        document.getElementById('next-btn').disabled = currentPage === totalPages || totalPages === 0;

        window.totalPages = totalPages;
    }

    window.changePage = function(direction) {
        currentPage += direction;
        if (currentPage < 1) currentPage = 1;
        if (currentPage > window.totalPages) currentPage = window.totalPages;
        renderTable();
    };

    // Attach event listeners so the table updates whenever a dropdown is changed
    statusFilter.addEventListener('change', applyFilters);
    categoryFilter.addEventListener('change', applyFilters);
    priorityFilter.addEventListener('change', applyFilters);
    dateFilter.addEventListener('change', applyFilters);

    // Run once on load to show initial table
    applyFilters();
});