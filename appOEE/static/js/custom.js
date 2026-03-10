/* =========================
   VARIÁVEIS GLOBAIS
========================== */
let chartOEE = null;
let oeeParqueGlobal = null;
let chartRanking = null;
let chartParadas = null; 
let chartParadasDia = null;
let chartParadasMaquina = null;
let chartTipos_paradas = null;
let chartMot_paradas = null;
let chartOEE_paradas = null;
let chartcustos_maquina = null;
let chartpreju_maquina = null;
let dias_estudo = null;
let total_horasParadas = null;


/* =========================
   REGISTROS CHART.JS
========================== */
Chart.register(ChartDataLabels);


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
            language: { url: "/static/datatables/pt-BR.json" },
            initComplete: function () {
                this.api().columns([1, 4, 5, 6]).every(function () {
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


/*===================================
   Dias de acompanhamento
===================================*/
async function total_dias_horasParadas() {
    fetch('/total_dias_horasParadas/') // O método padrão já é 'GET', não precisa declarar
        .then(response => {
            if (!response.ok) throw new Error('Erro na rede');
            return response.json();
        })
        .then(data => {
            dias_estudo = data.tot_dias; // Usando constante local
            total_horasParadas = data.total_parado; // Armazenando o total de horas paradas

            const nav_bar_dias = document.getElementById('nav_bar_dias');
            if (!nav_bar_dias) {
                // Se não achou o elemento, sai sem reclamar
                return;
            }
            nav_bar_dias.innerHTML = '<p>OEE: dados de "chão de fábrica" transformados em decisões objetivas -Período: '+ dias_estudo + ' dias - Total de Horas Paradas: '+ total_horasParadas +'</p>';

            const elemTitulo = document.getElementById('titulo_grafico_paradas');
            if (elemTitulo) {
                elemTitulo.innerHTML = '<h3>Total de Horas Paradas por dia - Período: ' + dias_estudo + ' dias - Acumulado de Horas Paradas: ' + total_horasParadas + '</h3>';
            }

        })
}


/* ===========================================
   Disp/Qual/Perf acumulados para Painel ROCE
=========================================== */
function oee_global_duponthtml(url) { // valores Disp., Perf. e Quali. acumulado geral
    fetch('/oee_global_duponthtml/', {
        method: 'get',
    }).then(function (result) {
        return result.json()
    }).then(function (data) {
        oeeParqueGlobal = data.oee;

        const alvo = document.getElementById('oee_global_dupont');

        if (!alvo) {
            // Se não achou o elemento, sai sem reclamar
            return;
        }

        alvo.innerHTML = 'Resultados Globais: Qual.: ' + data.qualidade + '% - Perf.: ' + data.performance +
            '% - Disp.: ' + data.disponibilidade + '% ';

    });

}


/* ================================
   CONFIGURAÇÃO PADRÃO GRÁFICOS
================================ */
function configGraficoPercentual() { // configuracao de grafico tipo "Percentual"
    return {
        responsive: true,
        plugins: {
            datalabels: {
                anchor: 'end',
                align: 'top',
                font: { size: 15, weight: 'bold' }
            }
        },
        scales: {
            x: { ticks: { font: { size: 15, weight: 'bold' } } },
            y: {
                beginAtZero: true,
                //max: 100,
                ticks: { stepSize: 10, font: { size: 20, weight: 'bold' } },
                title: { display: true, text: '%', font: { size: 30, weight: 'bold' } }
            }
        }
    };
}


function configGraficoParadas() { // configuracao de grafico tipo "Paradas"
    return {
        type: 'bar',
        options: {
            indexAxis: 'y',// <--- ESSA É A CHAVE PARA HORIZONTAL // <--- ESSA É A CHAVE PARA HORIZONTAL

            responsive: true,
            plugins: {
                title: {
                    display: true,
                    //text: 'Reclamações por mês',
                    font: {
                        weight: 'bold',
                        size: 25
                    },
                    // color: '#f0f',
                },
                datalabels: {
                    color: '#000',
                    anchor: 'center',
                    align: 'right',   // importante para barras horizontais
                    offset: 20,       // 👈 distância da barra
                    font: {
                        size: 20,
                        weight: 'bold'
                    }
                },
            },
            scales: {
                x: {
                    display: false,
                    fontsize: 40,
                    beginAtZero: true,
                    min: 0,
                    //max: 50,
                    font: {
                        size: 20,
                        weight: 'bold'   // 👈 rótulos do eixo
                    }
                },
                y: {
                    display: true,
                    ticks: {
                        beginAtZero: true,
                        min: 0,
                        //max: 45,
                        font: {
                            size: 20,
                            weight: 'bold'   // 👈 rótulos do eixo
                        }
                    }
                },
            }
        }
    };
}


function configGraficoPrejuizo() { // configuracao de grafico tipo "Prejuizo"
    return {
        type: 'bar',
        indexAxis: 'y',
        plugins: {
            title: {
                display: true,
                text: '',
                font: {
                    size: 25,
                    weight: 'bold'
                }
            },
            datalabels: {
                color: '#000',
                anchor: 'center',
                align: 'right',
                offset: 5,
                font: {
                    size: 15,
                    weight: 'bold'
                },
                formatter: function (value) {
                    return 'R$ ' + (value).toLocaleString('pt-BR', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    }) + ' /min';
                }
            }
        },
        scales: {
            x: {
                display: false,
                min: -1500000,
                max: 1500000,
                ticks: {
                    font: {
                        size: 25
                    },
                    callback: v => 'R$ ' + v.toLocaleString('pt-BR')
                }
            },
            y: {
                ticks: {
                    font: {
                        size: 20,
                        weight: 'bold'
                    }
                }
            }
        }
    };
}


/* ==================================================
   CARREGAR OEE DIARIO PARQUE DE MAQUINAS
   carrega o grafico geral ao clicar Listar no Listar
===================================================== */
async function carregarOeeDiarioParqueMaquinas() { // grafico OEE por maquina
    const canvas = document.getElementById('oeeChart');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/oee_parque_diario/')).json();
        if (chartOEE) chartOEE.destroy();

        chartOEE = new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: resp.dia,
                datasets: [
                    { label: 'dia', data: resp.dia },
                    { label: 'Qualidade', data: resp.qualidade },
                    { label: 'Performance', data: resp.performance },
                    { label: 'Disponibilidade', data: resp.disponibilidade },
                    { label: 'oee', data: resp.oee },
                ]
            },
            options: configGraficoPercentual()
        });
        //-----------------------------------------------------
        // Declara valor global para variavel oeeParqueGlobl
        //-----------------------------------------------------
       //oeeParqueGlobal = resp.oee
        // const elem = document.getElementById('oee_parque_acumulado');
        // if (elem) elem.innerHTML = `<h3>OEE Acumulado - Parque: ${Math.round(oeeParqueGlobal)}%</h3>`;

    } catch (err) {
        console.error("Erro ao carregar OEE diário:", err);
    }
}


/* =================================================
   CARREGAR OEE ACUMULADO GLOBAL PARQUE DE MAQUINAS
==================================================== */
async function carregarOeeDiarioParqueGlobal() { // calcula o OEE acumulado, disp., perf., qual. toda a planta

    const canvas = document.getElementById('oeeChart');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/oee_parque_acumulado/')).json();

        const elem = document.getElementById('oee_parque_acumulado');
        if (elem) elem.innerHTML = `<h3>OEE Acumulado - Parque: ${oeeParqueGlobal}%</h3>`;


    } catch (err) {
        console.error("Erro ao carregar OEE diário:", err);
    };
}


/* =========================
   CARREGAR OEE POR MÁQUINA
========================== */
async function carregarOeePorMaquina(maquinaId) { //  OEE com escolha de maquina
    const canvas = document.getElementById('oeeChart');
    if (!canvas) return;

    try {
        const resp = await (await fetch(`/oee_por_maquina/?maquina=${maquinaId}`)).json();
        if (chartOEE) chartOEE.destroy();

        chartOEE = new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: resp.dia,
                datasets: [
                    { label: 'OEE', data: resp.oee },
                    { label: 'Disponibilidade', data: resp.disponibilidade },
                    { label: 'Performance', data: resp.performance },
                    { label: 'Qualidade', data: resp.qualidade }
                ]
            },
            options: configGraficoPercentual()
        });

        // Comparação OEE
        if (oeeParqueGlobal !== null) {
            const elem = document.getElementById('comparacao_oee'); //
            if (!elem) return;

            const desc = oeeParqueGlobal > resp.oee_acum
                ? `<span style="color:red">▼</span>`
                : `<span style="color:white">▲</span>`;//Math.abs(val).toFixed(2)

            elem.innerHTML = `OEE - Parque de Máquinas: ${Math.round(oeeParqueGlobal).toFixed(0)}% / OEE ${resp.maquina}: ${Math.round(resp.oee_acum).toFixed(0)}% ${desc}`;
        }

    } catch (err) {
        console.error("Erro ao carregar OEE por máquina:", err);
    }
}


/*========================
#   CARREGAR RANKING OEE
========================== */
async function carregarRankingOEE() { // ranking OEE
    const canvas = document.getElementById('rankingChart');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/ranking_oee/')).json();
        if (chartRanking) chartRanking.destroy();

        chartRanking = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: { labels: resp.labels, datasets: [{ label: 'OEE (%)', data: resp.data }] },
            options: configGlobal('', 'x', 'percentual')
        });

    } catch (err) {
        console.error("Erro ao carregar ranking OEE:", err);
    }
}


/* ===================================
   GRAFICOS MAQUINAS POR PARALISACOES
====================================== */
async function paradas_maquina() { // horas paradas acumuladas por maquina
    const canvas = document.getElementById('Chartmaq_paradas');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/paradas_maquina/')).json();
        if (chartParadas) chartParadas.destroy();

        chartParadas = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: { labels: resp.maquina, datasets: [{ label: '', data: resp.tempo }] },

            options: configGlobal('', 'x', 'numero')
        });

    } catch (err) {
        console.error("Erro ao carregar mot_paradasChart:", err);
    }
}


async function tipo_parada() {// tipos de paradas produtivas, improdutivas ou programadas
    const canvas = document.getElementById('chartTipos_paradas');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/tipo_parada/')).json();
        if (chartTipos_paradas) chartTipos_paradas.destroy();

        chartTipos_paradas = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: resp.tipo,
                datasets: [{
                    label: '',
                    data: resp.tempo,
                }]
            },
            options: configGlobal('', 'x', 'numero')
        });

    } catch (err) {
        console.error("Erro ao carregar Charttipos_paradas:", err);
    }
}


async function motivo_parada() { // Grafico motivos de paradas por maquina em horas
    const canvas = document.getElementById('chartMot_paradas');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/motivo_parada/')).json();
        if (chartMot_paradas) chartMot_paradas.destroy();

        chartTipos_paradas = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: { labels: resp.motivo, datasets: [{ label: '', data: resp.tempo }] },
            options: configGlobal('', 'y', 'numero')
        });

    } catch (err) {
        console.error("Erro ao carregar Charttipos_paradas:", err);
    }
}


async function oee_maquina() { // Grafico  OEE  por maquina em %
    const canvas = document.getElementById('ChartOEE_maquina');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/oee_maquina/')).json();
        if (chartOEE_paradas) chartOEE_paradas.destroy();

        chartOEE_paradas = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: { labels: resp.maquina, datasets: [{ label: '', data: resp.oee }] },
            options: configGlobal('', 'x', 'percentual')
        });

    } catch (err) {
        console.error("Erro ao carregar oee_maquinaChart:", err);
    }
}


async function prejuizos_financeiros() { // tabela prejuizos financeiros na dupont.html
    try {
        const resp = await (await fetch('/prejuizos_financeiros/')).json();

        const elParalis = document.getElementById('dist_paralis');

        // Se o elemento não existir nesta página, saímos da função silenciosamente
        if (!elParalis) return;

        elParalis.innerHTML = `<h3>Distribuições das  ${resp.total_prejuizo[0]} em paralisações - Custo da Ineficiência Operacional  ${resp.total_prejuizo[4]}</h3>`

    } catch (err) {
        console.error("Erro ao carregar prejuizos_financeiros:", err);
    }
}


async function prejuizos_custos_maquina() { // custo_minuto individual por máquina
    const canvas = document.getElementById('Chartmaq_custo');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/prejuizos_custos_maquina/')).json();
        if (chartcustos_maquina) chartcustos_maquina.destroy();

        chartcustos_maquina = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: { labels: resp.maq_nome, datasets: [{ label: '', data: resp.custo_minuto }] },
            options: configGlobal('', 'y', 'custo_minuto')
        });

    } catch (err) {
        console.error("Erro ao carregar prejuizos_custos_maquina:", err);
    }
}


async function prejuizos_maquina() { // prejuizo indicividaul por maquina em R$
    const canvas = document.getElementById('Chartmaq_prejuizo');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/prejuizos_maquina/')).json();
        if (chartpreju_maquina) chartpreju_maquina.destroy();

        chartpreju_maquina = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: { labels: resp.maq_nome, datasets: [{ label: '', data: resp.preju_maq }] },
            options: configGlobal('', 'y', 'moeda')

        });

    } catch (err) {
        console.error("Erro ao carregar prejuizos_maquina:", err);
    }
}


/* ==================================================
    CARREGAR PARADO DIARIO PARQUE DE MAQUINAS
    carrega o grafico geral ao clicar Listar no Listar
===================================================== */
async function carregarParadasDiarioParqueMaquinas() { // grafico Paradas por dia

    const canvas = document.getElementById('chart_paradaspordia');
    if (!canvas) return;

    try {
        const resp = await (await fetch('/paradas_parque_diario/')).json(); 
        if (chartParadasDia) chartParadasDia.destroy(); 

        chartParadasDia = new Chart(canvas.getContext('2d'), {
            type: 'line',
                data: {
                    labels: resp.dia, 
                    datasets: [
                        { label: 'horas',
                         data: resp.horas_paradas, 
                            fill: {
                                target: 'origin', // 'origin' is the x-axis (y=0)
                                above: 'rgba(255, 0, 0, 0.08)', // Color above the origin (red)
                                below: 'rgb(255, 0, 0)'  // Color below the origin (blue) with transparency
                            } 
                        }
                    ] 
                },
            options: configGraficoParadasDiarias('', 'x', 'numero')
        });

    } catch (err) {
        console.error("Erro ao carregar total_dias_horasParadas:", err);
    }
}


/*==================================================
#  CONFIGURACOES DOS GRAFICOS COM GEMINI AJUDANDO
==================================================*/
function configGlobal(titulo, orientacao = 'x', formato = 'numero') { // configuracao generica para vários graficos bar 

    // Definindo a cor com 0.35 de transparência
    const corComTransparencia = 'rgba(220, 53, 69, 0.35)';
    const corSolida = 'rgba(220, 53, 70, 0.72)';

    return {
        indexAxis: orientacao, // 'x' para vertical, 'y' para horizontal
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: titulo,
                font: { size: 22, weight: 'bold' }
            },
            legend: { display: false },
            // Garanta que os datalabels apareçam para compensar a falta do eixo
            datalabels: {

                formatter: function (value) {
                    // Se for Waterfall, value é um array [início, fim]
                    // Precisamos calcular a diferença (o tamanho da barra)
                    let val;

                    if (Array.isArray(value)) {
                        // Para as perdas (que descem), queremos a diferença absoluta
                        // Para o faturamento inicial e final, pegamos o topo
                        val = (value[0] === 0) ? value[1] : (value[1] - value[0]);
                    } else {
                        val = value;
                    }

                    // Agora formatamos o 'val' que é um número garantido
                    if (formato === 'moeda') {
                        return 'R$ ' + (Math.abs(val) / 1000).toFixed(0) + ' mil';
                    } else if (formato === 'percentual') {
                        return value.toFixed(0) + ' %';
                    } else if (formato === 'custo_minuto') {
                        return 'R$ ' + Math.abs(val).toFixed(2) + ' /min';
                    } else {
                        
                        return Math.abs(val).toFixed(0);
                    }

                },
                font: { weight: 'bold', size: 20 },
                color: '#000',
                anchor: 'center',
                align: 'center',   // importante para barras horizontais
                offset: 25,       // 👈 distância da barra
                font: {
                    size: 15,
                    weight: 'bold'
                },
            }
        },
        scales: {
            x: {
                display: (orientacao === 'x'),
                grid: { display: false },
                border: { display: false },
                ticks: { font: { size: 18, weight: 'bold' } }
            },
            y: {
                display: (orientacao === 'y'),
                grid: { display: false },
                border: { display: false },
                ticks: { font: { size: 20, weight: 'bold' } }
            }
        },

        elements: {
            bar: {
                backgroundColor: corComTransparencia,
                borderColor: corSolida,
                borderWidth: 1
            },
        }
    };
}


function configGraficoParadasDiarias(titulo, orientacao = 'x', formato = 'numero') { // configuracao de grafico tipo "ParadasDiarias"
    return {
        indexAxis: orientacao, // 'x' para vertical, 'y' para horizontal
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: titulo,
                font: { size: 22, weight: 'bold' }
            },
            legend: { display: false },
            // Garanta que os datalabels apareçam para compensar a falta do eixo
            datalabels: {
                formatter: function (value) {
                    // Se for Waterfall, value é um array [início, fim]
                    // Precisamos calcular a diferença (o tamanho da barra)
                    let val;

                    if (Array.isArray(value)) {
                        // Para as perdas (que descem), queremos a diferença absoluta
                        // Para o faturamento inicial e final, pegamos o topo
                        val = (value[0] === 0) ? value[1] : (value[1] - value[0]);
                    } else {
                        val = value;
                    }

                    // Agora formatamos o 'val' que é um número garantido
                    if (formato === 'moeda') {
                        return 'R$ ' + (Math.abs(val) / 1000).toFixed(0) + ' mil';
                    } else if (formato === 'percentual') {
                        return value.toFixed(0) + ' %';
                    } else if (formato === 'custo_minuto') {
                        return 'R$ ' + Math.abs(val).toFixed(2) + ' /min';
                    } else {
                        return Math.abs(val).toFixed(0);
                    }
                },
                color: '#000',
                anchor: 'center',
                align: 'top',   // importante para barras horizontais
                offset: 5,       // 👈 distância da barra
                font: {
                    size: 15,
                    weight: 'bold'
                },
            }
        },
        scales: {
            x: {
                display: (orientacao === 'x'),
                grid: { display: false },
                border: { display: false },
                ticks: { font: { size: 15, weight: 'bold' } }
            },
            y: {
                display: true,
                title: { display: true, text: 'horas', font: { size: 20, weight: 'bold' } },
                grid: { display: true },
                border: { display: false },
                ticks: { beginAtZero: true, font: { size: 20, weight: 'bold' } }              
            }
        },
    };
}

fetch('/paradas_por_dia_maquina/')
    .then(response => response.json())
    .then(data => {
        const canvas = document.getElementById('chart_paradasporDiaMaquina');
        if (!canvas) return;

        if (chartParadasMaquina) chartParadasMaquina.destroy();

        chartParadasMaquina = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: data.labels, // As datas vindas do Python
                datasets: data.datasets // A lista de máquinas vinda do Python
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        stacked: true, // Empilha as máquinas no eixo X
                        ticks: { font: { size: 15, weight: 'bold' } } 
                    },
                    y: {
                        display:true, 
                        stacked: true, // Empilha os valores no eixo Y para somar o total
                        beginAtZero: true,
                        title: { display: true, text: 'horas paradas',
                            font: { size: 20, weight: 'bold' }
                         },
                        ticks: { font: { size: 20, weight: 'bold' }, stepSize: 1 } 
                    }
                },
                plugins: {
                    legend: {
                        position: 'top', // Mostra a legenda das máquinas no topo
                    },
                    datalabels: {
                        formatter: function (value, context) {
                            return value > 0 ? value : ''; // Se for 0, retorna vazio
                        },
                        color: '#000', // Cor do texto da etiqueta
                        anchor: 'center',
                        align: 'center',     // 👈 distância da barra
                        font: {
                            size: 15,
                            weight: 'bold'
                        }
                    }
                }
            }
        });
    });


/* ==================================================
#  AUTOLOAD AO ABRIR PÁGINA
====================================================*/
document.addEventListener('DOMContentLoaded', function () {
    total_dias_horasParadas();
    carregarOeeDiarioParqueMaquinas();
    carregarOeeDiarioParqueGlobal();
    carregarRankingOEE();
    oee_global_duponthtml();
    carregarParadasDiarioParqueMaquinas();
    paradas_maquina();
    tipo_parada();
    motivo_parada();
    oee_maquina();
    prejuizos_financeiros();
    prejuizos_custos_maquina();
    prejuizos_maquina();
});