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

    // 1. MÁSCARAS VISUAIS
    // Para inteiros (Ex: 1.500)
    $('.mask-inteiro').mask('#.##0', { reverse: true });

    // Para decimais/moeda (Ex: 1.250,50)
    $('.mask-decimal, .mask-money').mask('#.##0,00', { reverse: true });

    // 2. LIMPEZA ANTES DO ENVIO (Crucial para o Django não dar erro)
    $('form').submit(function () {
        // Limpar inteiros (remover todos os pontos)
        $('.mask-inteiro').each(function () {
            var val = $(this).val().replace(/\./g, '');
            $(this).val(val);
        });

        // Limpar decimais (remover pontos e trocar vírgula por ponto)
        $('.mask-decimal, .mask-money').each(function () {
            var val = $(this).val().replace(/\./g, '').replace(',', '.');
            $(this).val(val);
        });
    });
            // Escuta a mudança no campo de seleção de produto/chapa
        $('#id_selecionar_produto_padrao').change(function () {
            var chapaId = $(this).val();

            if (chapaId) {
                $.ajax({
                    url: '/get-chapa-detalhes/' + chapaId + '/',
                    type: 'GET',
                    success: function (data) {
                        // 1. Preenche o Nome do Produto (descrição para o orçamento)
                        $('#id_produto_nome').val(data.nome);

                        // 2. Preenche as Unidades por Chapa (Rendimento)
                        $('#id_unidades_chapa').val(data.unidades_chapa).trigger('input');

                        // 3. Seleciona a chapa automaticamente nos campos de FK
                        // Isso garante que o cálculo use os custos da chapa correta
                        $('#id_chapa_projeto').val(chapaId);
                        $('#id_chapa_utilizada').val(chapaId);

                        console.log("Configurações da chapa aplicadas!");
                    },
                    error: function () {
                        console.error("Erro ao buscar detalhes da chapa.");
                    }
                });
            }
        });

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

// Aguarda 3 segundos (3000 milissegundos)
setTimeout(function () {
    // Seleciona as mensagens do Django (assumindo classe .alert)
    var messages = document.querySelectorAll('.alert');

    messages.forEach(function (message) {
        // Aplica a transição CSS de fade
        message.style.transition = 'opacity 0.5s ease';
        message.style.opacity = '0';

        // Remove o elemento após a transição
        setTimeout(function () {
            message.remove();
        }, 500); // tempo da transição
    });
}, 3000);

document.addEventListener("DOMContentLoaded", function() {
        // Verifica se existe algum alerta na página
        const alerts = document.querySelectorAll('.alert');
        
        if (alerts.length > 0) {
            // Cria o contexto de áudio
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);

            // Configuração do "Bip" discreto
            oscillator.type = 'sine'; // Som suave
            oscillator.frequency.setValueAtTime(1900, audioCtx.currentTime); // Nota Lá (A5)

            // Controle de volume (muito baixo para não sustar)
            gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);

            // Duração curta (150ms) com um "fade out" para não estalar
            oscillator.start();
            gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.2);
            oscillator.stop(audioCtx.currentTime + 0.2);
        }
        
});