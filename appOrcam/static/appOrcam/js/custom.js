/* =========================
   DATATABLES
========================== */
$(document).ready(function () {
        if ($('#myTable').length) {

        // Alvo da correção: Se a tabela já foi inicializada anteriormente, destrói para remontar sem erros
        if ($.fn.dataTable.isDataTable('#myTable')) {
            $('#myTable').DataTable().destroy();
            // Opcional: Garante que os selects do footer antigos sejam limpos antes da recriação
            $('#myTable tfoot select').remove();
        }

        const table = $('#myTable').DataTable({
            "order": [[0, "desc"]],
            dom: 'Bfrtip',
            buttons: [
                'copyHtml5', 'excelHtml5', 'csvHtml5',
                { extend: 'pdfHtml5', orientation: 'landscape', pageSize: 'A4' },
                'colvis'
            ],
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
        // if ($.fn.DataTable.isDataTable('#myTable')) table.columns.adjust().draw();
        table.columns.adjust().draw();
    }


    // 1. MÁSCARAS VISUAIS (Com trava de segurança contra travamentos)
    if (typeof $.fn.mask === "function") {
        // Para inteiros (Ex: 1.500)
        $('.mask-inteiro').mask('#.##0', { reverse: true });

        // Para decimais/moeda (Ex: 1.250,50)
        $('.mask-decimal, .mask-money').mask('#.##0,00', { reverse: true });
    } else {
        console.warn("Plugin jquery.mask não encontrado nesta página. Pulando máscaras.");
    }

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
        var chapaId = $(this).val(); // Verificação rápida do valor selecionado

        if (chapaId) {
            $.ajax({
                // Use a URL que funcionou no navegador (ex: /get_chapa_detalhes/ ou /orcam/get_chapa_detalhes/)
                url: '/orcam/get_chapa_detalhes/' + chapaId + '/',
                type: 'GET',
                success: function (data) {
                    // 1. Preenche o Nome (id_produto_nome)
                    $('#id_produto_nome').val(data.nome);

                    // 2. Preenche o Rendimento (id_unidades_chapa)
                    // Dica: Use .trigger('change') para garantir que o Django/JS perceba a mudança
                    $('#id_unidades_chapa').val(data.unidades_chapa).trigger('change');

                    // 3. O PONTO CRÍTICO: chapa_projeto e chapa_utilizada
                    // Como são ForeignKeys, o Django gera os IDs como #id_chapa_projeto e #id_chapa_utilizada
                    $('#id_chapa_projeto').val(chapaId).trigger('change');
                    $('#id_chapa_utilizada').val(chapaId).trigger('change');

                    console.log("Campos preenchidos para a chapa ID: " + chapaId);
                },
                error: function () {
                    console.error("Erro ao buscar detalhes da chapa. Verifique a URL.");
                }
            });
        }
    });

});

// Captura o elemento primeiro
let elementoCep = document.getElementById('cep');

// Só executa a máscara se o elemento existir na página atual
if (elementoCep) {
    let cep = elementoCep.innerText;
    // Aplica a máscara 00000-000
    elementoCep.innerText = cep.replace(/(\d{5})(\d{3})/, "$1-$2");
}

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
        // CORREÇÃO CRUCIAL: Em vez de varrer todas as classes '.alert' da tela (que quebrava o simulador),
        // buscamos apenas pelos alertas de mensagens do Django (ex: com a classe '.messages' ou '.alert-dismissible')
        const alerts = document.querySelectorAll('.messages .alert, .alert-dismissible');
        
        if (alerts.length > 0) {
            // Cria o contexto de áudio
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);

            // Configuração do "Bip" discreto
            oscillator.type = 'sine'; 
            oscillator.frequency.setValueAtTime(1900, audioCtx.currentTime); 

            // Controle de volume
            gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);

            // Duração curta (200ms) com um "fade out" acústico para não estalar
            oscillator.start();
            gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.2);
            oscillator.stop(audioCtx.currentTime + 0.2);
            
            // ⚠️ SE HOUVER UM FADE VISUAL LOGO ABAIXO DAQUI NO SEU CUSTOM.JS, 
            // ele agora só vai afetar as mensagens reais, deixando o simulador intacto!
        }
});

// $(document).ready(function() {
//     // Gatilho para abrir o modal de Maiores Reclamantes de qualquer tela
//     $('#abre_modal_reclamantes').on('click', function(e) {
//         e.preventDefault(); // Evita que a página dê um salto para o topo
        
//         // Pega o modal e força o Bootstrap 5 a exibi-lo
//         // NOTA: Troque '#modalMaioresReclamantes' pelo ID REAL que está no seu HTML recortado!
//         var meuModal = new bootstrap.Modal(document.getElementById('modalMaioresReclamantes'));
//         meuModal.show();
//     });
// });
// ==========================================
// CONTROLE DOS MODAIS GLOBAIS (NAVBAR)
// ==========================================

$(function () {
    // 1. Clique no botão de Maiores Reclamantes
    $("#abre_modal_reclamantes").click(function (e) {
        e.preventDefault(); // Evita saltos na página pelo '#'
        
        // Abre o modal na tela
        $("#modal_reclamantes").modal('show');
        
        // CHAMA A FUNÇÃO QUE DESENHA O GRÁFICO (Crucial!)
        maioresReclamantes();
    });

    // 2. Clique no botão de Semana/Ano (Se mantiver o mesmo padrão)
    $("#abre_modal_semanAno").click(function (e) {
        e.preventDefault();
        $("#modal_semanAno").modal('show');
    });
});

// ==========================================
// FUNÇÃO AJAX QUE BUSCA E RENDERIZA O GRÁFICO
// ==========================================
function maioresReclamantes() {
    $.ajax({
        type: 'GET',
        url: '/qualidade/maioresReclamantes/',
        data: {},
        success: function (resposta) { 
            // Garante a limpeza do container antes de reinjetar o canvas
            if (document.getElementById('maiores_reclamantes_modal')) {
                document.getElementById('maiores_reclamantes_modal').innerHTML = "";
                var tbl = "<canvas id='grf_reclamantes'></canvas>";
                document.getElementById('maiores_reclamantes_modal').innerHTML = tbl;

                const ctx = document.getElementById('grf_reclamantes').getContext('2d');

                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: resposta.cliente,
                        datasets: [{
                            label: "Total de Reclamações",
                            data: resposta.tot_cliente,
                            tension: 0.3,
                            borderWidth: 1,
                            backgroundColor: "rgba(255,30,150,0.20)",
                            borderColor: "rgb(255,99,132)",
                            fill: false
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        plugins: {
                            title: { display: false },
                            datalabels: {
                                color: '#000',
                                anchor: 'center',
                                align: 'center',
                                offset: 8,
                                font: { size: 16, weight: 'bold' }
                            },
                        },
                        scales: {
                            x: { display: false },
                            y: {
                                display: true,
                                ticks: { font: { size: 16 } }
                            }
                        }
                    }
                });
            }
        },
        error: function (error) {
            console.log("Erro na requisição dos reclamantes:", error);
        }
    });
}