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
            statusOthers.forEach(cb => cb.checked = false);
        } else {
            e.target.checked = true; 
        }
        updatePreview(); // Trigger update on change
    });

    statusOthers.forEach(cb => {
        cb.addEventListener('change', () => {
            const anyChecked = Array.from(statusOthers).some(c => c.checked);
            statusAll.checked = !anyChecked;
            updatePreview(); // Trigger update on change
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
        updatePreview(); // Trigger update on change
    });

    catOthers.forEach(cb => {
        cb.addEventListener('change', () => {
            const anyChecked = Array.from(catOthers).some(c => c.checked);
            catAll.checked = !anyChecked;
            updatePreview(); // Trigger update on change
        });
    });

    // --- 4. Logic for Date Inputs ---
    document.querySelectorAll('.date-input').forEach(input => {
        input.addEventListener('change', updatePreview);
    });

    // --- 5. Unified Filter Update Function ---
    const updatePreview = () => {
        // Collect Statuses
        const statusValues = Array.from(document.querySelectorAll('.status-cb:checked'))
            .filter(cb => cb.id !== 'status-all')
            .map(cb => cb.value);
        
        // Collect Categories
        const catValues = Array.from(document.querySelectorAll('.cat-cb:checked'))
            .filter(cb => cb.id !== 'cat-all')
            .map(cb => cb.value);

        // Collect Priorities (Assuming you have priority-cb class in HTML)
        const priorityValues = Array.from(document.querySelectorAll('.priority-cb:checked'))
            .map(cb => cb.value);

        // Construct Query Params
        const params = new URLSearchParams();
        statusValues.forEach(v => params.append('status', v));
        catValues.forEach(v => params.append('category', v));
        priorityValues.forEach(v => params.append('priority', v));
        
        params.append('start_date', document.getElementById('start-date').value);
        params.append('end_date', document.getElementById('end-date').value);

        // Reload page with new filters
        window.location.href = `/admin-export?${params.toString()}`;
    };

    // --- 6. Placeholder for Download Click ---
    document.getElementById('download-report-btn').addEventListener('click', () => {
        const format = btnExcel.classList.contains('active') ? 'Excel' : 'CSV';
        console.log(`Download triggered. Format: ${format}`);
    });

});