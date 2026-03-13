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
                this.api().columns([2, 4, 8]).every(function () {
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


$('#myTable').on('click', 'button[name=orcam_id]', function (e) {
    e.preventDefault();
    var id = $(this).closest('tr').find('#getId').html(); //alert('id para editar nivel '+id);

    $.ajax({ 
        type: 'GET',
        url: `/orcamento/${id}/` ,
        data: {},
        success: function (response) {
            // Abre nova janela com o conteúdo do PDF/HTML
            var novaJanela = window.open('', '_blank');
            if (novaJanela) {
                novaJanela.document.write(response);
                novaJanela.document.close();
            } else {
                alert("Por favor, habilite pop-ups para este site.");
            }
        },
        error: function (xhr, status, error) {
            // MELHORADO: Mostra o erro técnico no console
            console.error("Erro AJAX:", status, error);
            alert("Ocorreu um erro...ao tentar abrir orcamento");
        }
    });
});    