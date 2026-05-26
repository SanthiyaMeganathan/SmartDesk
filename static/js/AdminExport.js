document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Toggle Format Buttons (Excel vs CSV) ---
    const btnExcel = document.getElementById('btn-excel');
    const btnCsv = document.getElementById('btn-csv');

    btnExcel.addEventListener('click', () => {
        btnExcel.classList.add('active');
        btnCsv.classList.remove('active');
    });

    btnCsv.addEventListener('click', () => {
        btnCsv.classList.add('active');
        btnExcel.classList.remove('active');
    });

    // --- 2. Logic for 'Status' Checkboxes ---
    const statusAll = document.getElementById('status-all');
    const statusOthers = document.querySelectorAll('.status-cb:not(#status-all)');

    statusAll.addEventListener('change', (e) => {
        if (e.target.checked) {
            // Uncheck all specific statuses
            statusOthers.forEach(cb => cb.checked = false);
        } else {
            // Force it to stay checked if user tries to uncheck it manually while nothing else is checked
            e.target.checked = true; 
        }
    });

    statusOthers.forEach(cb => {
        cb.addEventListener('change', () => {
            const anyChecked = Array.from(statusOthers).some(c => c.checked);
            if (anyChecked) {
                statusAll.checked = false; // Uncheck "All"
            } else {
                statusAll.checked = true;  // Fallback to "All" if everything is unchecked
            }
        });
    });

    // --- 3. Logic for 'Category' Checkboxes ---
    const catAll = document.getElementById('cat-all');
    const catOthers = document.querySelectorAll('.cat-cb:not(#cat-all)');

    catAll.addEventListener('change', (e) => {
        if (e.target.checked) {
            catOthers.forEach(cb => cb.checked = false);
        } else {
            e.target.checked = true;
        }
    });

    catOthers.forEach(cb => {
        cb.addEventListener('change', () => {
            const anyChecked = Array.from(catOthers).some(c => c.checked);
            if (anyChecked) {
                catAll.checked = false;
            } else {
                catAll.checked = true; 
            }
        });
    });

    // --- 4. Placeholder for Download Click ---
    document.getElementById('download-report-btn').addEventListener('click', () => {
        const format = btnExcel.classList.contains('active') ? 'Excel' : 'CSV';
        console.log(`Download triggered. Format: ${format}`);
        // Backend logic will go here
    });

});