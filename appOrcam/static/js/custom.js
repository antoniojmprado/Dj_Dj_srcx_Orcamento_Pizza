/* =========================
   DATATABLES
========================== */
$(document).ready(function () {
    if ($('#myTable').length) {
        const table = $('#myTable').DataTable({
            dom: 'Bfrtip',
            buttons: [
                'copyHtml5', 'excelHtml5', 'csvHtml5',
                { extend: 'pdfHtml5', orientation: 'landscape', pageSize: 'A4' },
                'colvis'
            ],
            fixedHeader: true,
            scrollX: true,
            scrollY: 450,
            scrollCollapse: true,
            scrollX: true, // Necessário para colunas fixas
            fixedColumns: {
                left: 3, // Fixa a primeira coluna à esquerda
                right: 2 // Fixa a última coluna à direita
            },
            language: { url: "/static/datatables/pt-BR.json" },
            initComplete: function () {
                this.api().columns([ 4, 8]).every(function () {
                    const column = this;
                    const select = $('<select><option value=""></option></select>')
                        .appendTo($(column.footer()).empty())
                        .on('change', function () {
                            const val = $.fn.dataTable.util.escapeRegex($(this).val());
                            column.search(val ? '^' + val + '$' : '', true, false).draw();
                        });
                    column.data().unique().sort().each(function (d) { select.append(`<option value="${d}">${d}</option>`); });
                });
            }
        });
        if ($.fn.DataTable.isDataTable('#myTable')) table.columns.adjust().draw();
    }
});