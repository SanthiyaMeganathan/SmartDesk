document.addEventListener('DOMContentLoaded', () => {

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


    const statusAll = document.getElementById('status-all');

    const statusCheckboxes =
        document.querySelectorAll('.status-cb:not(#status-all)');

    statusAll.addEventListener('change', () => {

        if (statusAll.checked) {

            statusCheckboxes.forEach(cb => {
                cb.checked = false;
            });
        }

        updatePreview();
    });

    statusCheckboxes.forEach(cb => {

        cb.addEventListener('change', () => {

            const checkedCount =
                [...statusCheckboxes]
                .filter(c => c.checked).length;

            if (checkedCount > 0) {
                statusAll.checked = false;
            } else {
                statusAll.checked = true;
            }

            updatePreview();
        });

    });



    const catAll = document.getElementById('cat-all');

    const catCheckboxes =
        document.querySelectorAll('.cat-cb:not(#cat-all)');

    catAll.addEventListener('change', () => {

        if (catAll.checked) {

            catCheckboxes.forEach(cb => {
                cb.checked = false;
            });
        }

        updatePreview();
    });

    catCheckboxes.forEach(cb => {

        cb.addEventListener('change', () => {

            const checkedCount =
                [...catCheckboxes]
                .filter(c => c.checked).length;

            if (checkedCount > 0) {
                catAll.checked = false;
            } else {
                catAll.checked = true;
            }

            updatePreview();
        });

    });



    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');



    const today =
        new Date().toISOString().split('T')[0];

    startDate.max = today;
    endDate.max = today;

    startDate.addEventListener('change', updatePreview);
    endDate.addEventListener('change', updatePreview);



    function updatePreview() {

        const params = new URLSearchParams();



        const selectedStatuses =
            [...statusCheckboxes]
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        selectedStatuses.forEach(status => {
            params.append('status', status);
        });



        const selectedCategories =
            [...catCheckboxes]
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        selectedCategories.forEach(category => {
            params.append('category', category);
        });


        if (startDate.value > today) {

            alert(
                'Start date cannot be greater than today'
            );

            startDate.value = '';
            return;
        }


        if (endDate.value > today) {

            alert(
                'End date cannot be greater than todays date'
            );

            endDate.value = '';
            return;
        }

        if (
            startDate.value &&
            endDate.value &&
            endDate.value < startDate.value
        ) {

            alert(
                'End date cannot be lesser than start date'
            );

            endDate.value = '';
            return;
        }



        if (startDate.value) {
            params.append(
                'start_date',
                startDate.value
            );
        }

        if (endDate.value) {
            params.append(
                'end_date',
                endDate.value
            );
        }



        window.location.href =
            `/admin-export?${params.toString()}`;
    }

    document.getElementById('download-report-btn')
        .addEventListener('click', () => {

            const params = new URLSearchParams();
            const selectedStatuses =
                [...statusCheckboxes]
                .filter(cb => cb.checked)
                .map(cb => cb.value);

            selectedStatuses.forEach(status => {
                params.append('status', status);
            });


            const selectedCategories =
                [...catCheckboxes]
                .filter(cb => cb.checked)
                .map(cb => cb.value);

            selectedCategories.forEach(category => {
                params.append('category', category);
            });


            if (startDate.value) {
                params.append(
                    'start_date',
                    startDate.value
                );
            }

            if (endDate.value) {
                params.append(
                    'end_date',
                    endDate.value
                );
            }


            const format =
                btnExcel.classList.contains('active')
                    ? 'excel'
                    : 'csv';

            params.append('format', format);

            window.location.href =
                `/download-export?${params.toString()}`;
        });

});