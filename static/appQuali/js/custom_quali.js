
Chart.register(ChartDataLabels);

var ultimoregistro; // criada variavel global valorizada em data_ultimo_registro(url) para uso em outras partes

document.querySelectorAll('.btn-leia-mais').forEach((btn) => {
    const texto = btn.previousElementSibling;

    /* Se o texto NÃO ultrapassar 4 linhas, esconde o botão */
    if (texto.scrollHeight <= texto.clientHeight) {
        btn.style.display = 'none';
        return;
    }

    btn.addEventListener('click', () => {
        texto.classList.toggle('expandido');

        btn.textContent = texto.classList.contains('expandido')
            ? 'Ler menos'
            : 'Ler mais';
    });
});

function defeitosPorMes(url) {
        fetch(url, {
            method: 'get',
        }).then(function (result) {
            return result.json()
        }).then(function (data) {

            const ctx = document.getElementById('defeitosPorMes').getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.mesAno,
                    datasets: [{
                        label: "Reclamações",
                        data: data.tot,
                        borderWidth: 1,
                        backgroundColor: "rgba(255,30,150,0.20",
                        borderColor:"rgb(255,99,132",
                        fill: true,
                    }],
                },
                options: {
                    indexAxis: 'y',
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
                            offset: 15,       // 👈 distância da barra
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
                            max: 50,
                        },
                        y: {
                            display: true, 
                            ticks: {
                                beginAtZero: true,
                                min: 0,
                                max: 45,
                                font: {
                                    size: 20,
                                    weight: 'bold'   // 👈 rótulos do eixo
                                }
                            }
                        },
                    }
                }
            });
        })
}

function defeitosPorDiaHistorico30(url) {
    fetch(url, {
        method: 'get',
    }).then(function (result) {
        return result.json()
    }).then(function (data) {

        const ctx = document.getElementById('defeitosPorDiaHistorico30').getContext('2d');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dia_mes,
                datasets: [{
                    label: "Reclamações",
                    data: data.tot,
                    tension: 0.3, // Um valor entre 0 e 1. Quanto maior, mais suave/ondulada.
                    borderWidth: 1,
                    backgroundColor: "rgba(255,30,150,0.20",
                    borderColor: "rgb(255,99,132",
                    fill: true,
                }],
            },
            options: {
                //indexAxis: 'y',
                plugins: {
                    title: {
                        display: true,
                       // text: 'Reclamações por dia',
                        font: {
                           // weight: 'bold',
                            size: 25
                        },
                        // color: '#f0f',
                    },
                    datalabels: {
                        color: '#000',
                        anchor: 'end',
                        align: 'top',   // importante para barras horizontais
                        offset: 10,       // 👈 distância da barra
                        font: {
                            size: 15,
                            weight: 'bold'
                        }
                    },
                },
                scales: {
                    x: {
                        display: true,
                        ticks: {
                            font: {
                                size: 15   // 👈 rótulos do eixo
                            }
                        }
                    },
                    y: {
                        display: false,
                        ticks: {
                            font: {
                                size: 15   // 👈 rótulos do eixo
                            }
                        }
                    },
                }
            }
        });
    })
}

function defeitosPorTipoMaisFrequentes(url) {
    fetch(url, {
        method: 'get',
    }).then(function (result) {
        return result.json()
    }).then(function (data) {

        const ctx = document.getElementById('tiposMaisFrequentes').getContext('2d');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.tipo_recl,
                datasets: [{
                    label: "Reclamações",
                    data: data.tot,
                    borderWidth: 1,
                    backgroundColor: "rgba(255,30,150,0.20",
                    borderColor: "rgb(255,99,132",
                    fill: false,
                }],
            },
            options: {
                indexAxis: 'y',
                plugins: {
                    title: {
                        display: true,
                        // text: 'Reclamações por dia',
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
                        offset: 8,       // 👈 distância da barra
                        font: {
                            size: 15,
                            weight: 'bold'
                        }
                    },
                },
                scales: {
                    x: {
                        display: false,
                        ticks: {
                            font: {
                                size: 15   // 👈 rótulos do eixo
                            }
                        }
                    },
                    y: {
                        display: true,
                        ticks: {
                            font: {
                                size: 15, // 👈 rótulos do eixo
                                //weight: 'bold'  
                            }
                        }
                    },
                },
            }
        });
    })
}

function selecionaMesAno(url) {
    fetch(url, {
        method: 'get',
    }).then(function (result) {
        return result.json()
    }).then(function (data) {
        var num_rows = data.num_rows;
        var tbl = '';
        tbl += "<select class='form btn-sombra' id='selAnoMes' name = 'anoMes' onchange='anoMesEscolhido()'>";
        tbl += "<option>Escolha Mes/Ano</option>";
        for (var i = 0; i <= num_rows - 1; i++) {
            tbl += "<option value=" + data.yearMonth[i] + "> " + data.yearMonth[i] + " </option>";
        }
        tbl += "</select>";//alert(tbl);
        document.getElementById('selecionaMesAno').innerHTML = tbl
    })
}

function anoMesEscolhido(url) { 
    var anoMes = document.getElementById("selAnoMes").value; 
    
    $.ajax({
        type: 'GET',
        url: "/qualidade/defeitoMesEscolhido/",
        data: { anoMes: anoMes },
        success: function (resposta) { // recebe data_json = { 'chave_tipoId': chave_tipoId, 'qt_tipos': qt_tipos }
            var tbl = '';
            // tbl += "<div class='card_body bg'>";
            tbl += " Principais Tipos de Defeito em "+ anoMes + "  <canvas id='grf_defeitoMesEscolhido'></canvas>";
            // tbl += "</div>";
            document.getElementById('defeitoMesEscolhido').innerHTML = tbl;

            const ctx = document.getElementById('grf_defeitoMesEscolhido').getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: resposta.chave_tipoId,
                    datasets: [{
                        label: "",
                        data: resposta.qt_tipos,
                        borderWidth: 1,
                        backgroundColor: "rgba(255,30,150,0.20",
                        borderColor: "rgb(255,99,132",
                        fill: true
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                           // text: 'Principais Tipos de Defeito em ' + anoMes,
                            font: {
                                weight: 'bold',
                                size: 25,
                            },
                            color: '#F2480B',
                        }, 
                        datalabels: {
                            color: '#000',
                            anchor: 'center',
                            align: 'right',   // importante para barras horizontais
                            offset: 5,       // 👈 distância da barra
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        },

                    },
                    scales: {
                        x: {
                            display: false,
                            ticks: {
                                stepSize: 1
                            }
                        },
                        y: { // This targets the y-axis scale
                            ticks: {
                                font: {
                                    size: 14 // Set the desired font size in pixels
                                },
                            }
                        },
                    }
                }
            });
        },
        error: function (error) {
            // Código a ser executado em caso de erro
        }
    })
}


function defeitosPorMaisFrequentesMesAnterior(url) {
   
    $.ajax({
        type: 'GET',
        url: "/qualidade/defeitosPorMaisFrequentesMesAnterior",
       
        success: function (resposta) { // recebe data_json = { 'chave_tipoId': chave_tipoId, 'qt_tipos': qt_tipos }

            document.getElementById('defeitoMesEscolhido').innerHTML = "";
            var tbl = '';
            tbl += "<div class='card_body bg'>";
            tbl += "Principais Defeitos " +resposta.anoMes  + " - <u>mês anterior</u> " + "<canvas id='grf_defeitoMesEscolhido'></canvas>";
            tbl += "</div>";
            document.getElementById('defeitoMesEscolhido').innerHTML = tbl;

            const ctx = document.getElementById('grf_defeitoMesEscolhido').getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: resposta.labels,
                    datasets: [{
                        label: "",
                        data: resposta.quantidade,
                        borderWidth: 1,
                        backgroundColor: "rgba(255,30,150,0.20",
                        borderColor: "rgb(255,99,132",
                        fill: true
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            // text: 'Principais Tipos de Defeito em ' + anoMes,
                            font: {
                                weight: 'bold',
                                size: 25,
                            },
                            color: '#F2480B',
                        },
                        datalabels: {
                            color: '#000',
                            anchor: 'center',
                            align: 'right',   // importante para barras horizontais
                            offset: 5,       // 👈 distância da barra
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        },

                    },
                    scales: {
                        x: {
                            display: false,
                            ticks: {
                                stepSize: 1
                            }
                        },
                        y: { // This targets the y-axis scale
                            ticks: {
                                font: {
                                    size: 14 // Set the desired font size in pixels
                                },
                            }
                        },
                    }
                }
            });
        },
        error: function (error) {
        //     // Código a ser executado em caso de erro
        }
    })
}

function defeitosPorSemana(ursl){
    $.ajax({
        type: 'GET',
        url: "/qualidade/defeitosPorSemana/",

        success: function (resposta) { // recebe data_json = { 'chave_tipoId': chave_tipoId, 'qt_tipos': qt_tipos }

            document.getElementById('defeitosPorSemana').innerHTML = "";
            var tbl = '';
            tbl += "<div class='card_body bg'>";
            tbl += "Acumulado das Reclamações por Semana " + "<canvas id='grf_defeitosPorSemana'></canvas>";
            tbl += "</div>";
            document.getElementById('defeitosPorSemana').innerHTML = tbl;

            const ctx = document.getElementById('grf_defeitosPorSemana').getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: resposta.sem_Ano,
                    datasets: [{
                        label: "Semana",
                        data: resposta.quantidade,
                        tension: 0.3, // Um valor entre 0 e 1. Quanto maior, mais suave/ondulada.                    
                        borderWidth: 1,
                        backgroundColor: "rgba(255,30,150,0.20",
                        borderColor: "rgb(255,99,132",
                        fill: false
                    }]
                },
                options: {
                    //indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            // text: 'Principais Tipos de Defeito em ' + anoMes,
                            font: {
                               // weight: 'bold',
                                size: 25,
                            },
                            color: '#F2480B',
                        },
                        datalabels: {
                            color: '#000',
                            anchor: 'end',
                            align: 'top',   // importante para barras horizontais
                            offset: 8,       // 👈 distância da barra
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        },

                    },
                    scales: {
                        x: {
                            display: true,
                            ticks: {
                                stepSize: 1,
                                font: {
                                    size: 16, // Set the desired font size in pixels
                                    //weight: 'bold'
                                },
                            }
                        },
                        y: {// This targets the y-axis scale
                            display: false,
                            ticks: {
                                font: {
                                    size: 16 // Set the desired font size in pixels
                                },
                            }
                        },
                    }
                }
            });
        },
        error: function (error) {
            //     // Código a ser executado em caso de erro
        }
    })
}

function listaDefeitos(url) {
    fetch(url, {
        method: 'get',
    }).then(function (result) {
        return result.json()
    }).then(function (data) {
        var num_rows = data.num_rows;
        var tbl = '';
        tbl += "<select class='form btn-sombra' id='selTipoDefeito' name = 'selTipoDefeito' onchange='tiposDefeitosPorSemana()'>";
        tbl += "<option>Defeito ?</option>";
        for (var i = 0; i <= num_rows - 1; i++) {
            tbl += "<option value=" + data.num_Id[i] + "> " + data.tipoId[i] + " </option>";
        }
        tbl += "</select>";
        document.getElementById('listaDefeitos').innerHTML = tbl
    })
}

function tiposDefeitosPorSemana(url) {
    var defeito_escolhido = document.getElementById("selTipoDefeito").value ;

    $.ajax({
        type: 'GET',
        url: "/qualidade/tiposDefeitosPorSemana/",
        data: { defeito_escolhido: defeito_escolhido },
        success: function (resposta) {
            var tbl = '';
            tbl += "<div class='card_body bg'>";
            tbl +=  resposta.defeito + "<canvas id='grf_grafEscolhidoPorSemana'></canvas>";
            tbl += "</div>";
            document.getElementById('tiposDefeitosPorSemana').innerHTML = tbl;

            const ctx = document.getElementById('grf_grafEscolhidoPorSemana').getContext('2d');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: resposta.semAno,
                    datasets: [{
                        label: "Qt por defeito por semana_ano",
                        data: resposta.tot,
                        tension: 0.2, // Um valor entre 0 e 1. Quanto maior, mais suave/ondulada.                        
                        borderWidth: 1,
                        backgroundColor: "rgba(255,30,150,0.20",
                        borderColor: "rgb(255,99,132",
                        fill: true
                    }]
                },
                options: {
                   // indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            // text: 'Principais Tipos de Defeito em ' + anoMes,
                            font: {
                                //weight: 'bold',
                                size: 16,
                            },
                            color: '#F2480B',
                        },
                        datalabels: {
                            color: '#000',
                            anchor: 'center',
                            align: 'top',   // importante para barras horizontais
                            offset: 5,       // 👈 distância da barra
                            font: {
                                size: 18,
                                weight: 'bold'
                            }
                        },
                        tooltip: {
                            backgroundColor: '#212529',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            callbacks: {
                                title: (items) => `Semana ${items[0].label}`,
                                label: (ctx) => `Total: ${ctx.parsed.y}`,
                                footer: () => 'Clique para detalhes'
                            }
                        }
                        

                    },
                    scales: {
                        x: {
                            display: true,
                            ticks: {
                                stepSize: 1,
                                font: {
                                    size: 14, // Set the desired font size in pixels
                                    weight: 'bond'
                                },
                            }
                        },
                        y: {// This targets the y-axis scale
                            display: false, 
                            ticks: {
                                font: {
                                    size: 14 // Set the desired font size in pixels
                                },
                            }
                        },
                    }
                }
            });
        },
        error: function (error) {
            // Código a ser executado em caso de erro
        }
    })
}

// function data_primeiro_registro(url) { 
//     $.ajax({
//         type: 'GET',
//         url: '/qualidade/data_primeiro_registro/',
//         data: {},

//         success: function (resposta) {
            
//             document.getElementById('prim_reg').innerHTML = "Início: "+ resposta.prim_reg 
//         },
//         error: function (error) {
//             alert(' erro em data_primeiro_registro!!!')
//         }
//     })
// }

function data_ultimo_registro(url) { 
    $.ajax({
        type: 'GET',
        url: '/qualidade/data_ultimo_registro/',
        data: {},

        success: function (resposta) { 
            ultimoregistro = resposta.ult_reg
            document.getElementById('ult_reg').innerHTML = "Ult. atual.: " + ultimoregistro + '<p style="align-text:right">  vendedor(a): '+ resposta.vendedora+'</p>'
        },
        error: function (error) {
            alert('erro em data_ultimo_registro!!!')
        }
    })
}

$(function(){
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.classList.remove('show');
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 500);
        });
    }, 4000);
})

$(function () { // faz parte do conjto de acoes para deletar registros

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    $('.delete-btn').click(function (e) {
    e.preventDefault(); // Garante que o botão não faça nenhum comportamento nativo
    const id = $(this).data('id');

    // O JS cuida sozinho do Alerta de confirmação agora
    if (!confirm('Deseja excluir mesmo o registro id = ' + id + '?')) return;

    const btn = $(this); // Guarda o botão clicado para sumir com a linha depois

    $.ajax({
        // Certifique-se de que a rota começa com a barra inicial correta
        url: '/qualidade/reclamacao/excluir/' + id + '/', 
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function (response) {
            const html = `
            <div class="alert alert-danger alert-dismissible fade show">
                ${response.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`;

            // 1. Injeta a mensagem de sucesso na tela no elemento 'msg'
            const msgElement = document.getElementById('msg');
            if (msgElement) {
                msgElement.innerHTML = html;
            }

            // 2. Remove a linha da tabela na hora usando o ID único
            $('#linha-' + id).fadeOut(500, function() {
                $(this).remove();
            });
        },
        error: function (xhr) {
            console.error(xhr.responseText);
            alert('Erro ao excluir: Verifique o console do navegador.');
        }
    });
});

    


});


const table = $(document).ready(function () {
    $('#mytable').DataTable({
        dom: 'Bfrtip',      
            buttons: [
                'copyHtml5',
                'excelHtml5',
                'csvHtml5',
                {
                    extend: 'pdfHtml5',
                    text: 'PDF',
                    orientation: 'landscape', // 👈 PDF respeita
                    pageSize: 'A4'
                },
                'colvis'
            ],
            "fixedHeader": {
                header: true,
                footer: true
            },
            language: {
                url: '/static/datatables/pt-BR.json'
            },
            scrollX: true,
            scrollY: 450,
            columnDefs: [{ width: 400 }],
            scrollCollapse: true,
            fixedColumns: {
                left: 1,   // fixa duas primeiras
                right: 1   // fixa a última
            },

            // A função initComplete é executada quando a inicialização estiver completa
            initComplete: function () { // para colocar campos search em cada coluna...
                this.api()
                    .columns()
                this.api().columns([1, 2, 6, 8]).every(function () {
                    var column = this;
                    var select = $('<select><option value=""></option></select>')
                        .appendTo($(column.footer()).empty())
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex($(this).val());

                            column.search(val ? '^' + val + '$' : '', true, false).draw();
                        });

                    column
                        .data()
                        .unique()
                        .sort()
                        .each(function (d, j) {
                            select.append('<option value="' + d + '">' + d + '</option>');
                        });
                });
            }
    });
    table.columns.adjust().draw();
});


// tooltips a partir daqui


fetch('/qualidade/grafico_defeitos/')
    .then(r => r.json())
    .then(resp => {

        const labels = resp.labels;

        // 🔴 AQUI É O PONTO CRÍTICO
        const totais = resp.totais.map(v => Number(v));

        criarGrafico(labels, totais, resp.detalhes);
    });



function criarGrafico(labels, totais, detalhesPorSemana) {
    const partes = "Detalhamentos das Reclamações por Semana - (passe mouse sobre as barras)".split("-");

    new Chart(document.getElementById('grafico'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '',
                data: totais,
                borderWidth: 1,
                backgroundColor: "rgba(255,30,150,0.20",
                borderColor: "rgb(255,99,132",
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,

            scales: {
                x: {
                    display: true,
                    ticks: {
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0,
                        font: {
                            size: 20,
                            weight: 'bold'
                        }
                    }
                },
                y: {
                    display : false,
                    beginAtZero: true,
                    ticks: {
                        callback: v => v.toLocaleString('pt-BR')
                    },
                    min:0,
                    max: 20,
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: [
                        partes[0],
                        ""+ partes[1],
                    ],
                    font: {
                        weight: 'bold',
                        size: 25,
                    },
                    color: '#000',
                }, 
                datalabels: {
                    color: '#000',
                    anchor: 'center',
                    align: 'top',   // importante para barras horizontais
                    offset: 5,       // 👈 distância da barra
                    font: {
                        size: 20,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    padding: 12,

                    titleFont: {
                        size: 25,
                        weight: 'bold'
                    },

                    bodyFont: {
                        size: 20
                    },

                    footerFont: {
                        size: 28,
                        weight: 'bold'
                    },

                    callbacks: {
                        label: function (ctx) {

                            const semana = ctx.label;
                            const defeitos = (detalhesPorSemana[semana] || [])
                                // 🔽 ordena do maior para o menor
                                .sort((a, b) => {
                                    if (b.quantidade !== a.quantidade) {
                                        return b.quantidade - a.quantidade; // quantidade desc
                                    }
                                    return a.defeito.localeCompare(b.defeito); // alfabética asc
                                });


                            let total = 0;

                            const linhas = defeitos.map(d => {
                                total += d.quantidade;
                                return `${d.defeito}: ${d.quantidade}`;
                            });

                            // ➕ linha final com soma
                            linhas.push('----------------');
                            linhas.push(`Total: ${total}`);

                            return linhas;
                        }
                    }
                }
            }
        }
    });
}


function qt_reclamantes(url) { 
    $.ajax({
        type: 'GET',
        url: '/qualidade/qt_reclamantes/',
        data:{},

        success: function (resposta) {
            
            document.getElementById('qt_reclamantes').innerHTML = "Contatos feitos por " + "<strong>" + resposta.tot_cliente_reclam + "</strong>" +" clientes diferentes."
            // document.getElementById('qt_reclamantes').innerHTML = "Reclamaçoes feitas por " + "<strong>" + resposta.tot_cliente_reclam + "</strong>" 
        },
        error: function (error) {
            alert('erro!!!')
        }
    })
}

function maioresReclamantes(url) {
    $.ajax({
        type: 'GET',
        url: '/qualidade/maioresReclamantes/',
        data:{},

        success: function (resposta) { 
            document.getElementById('maiores_reclamantes_modal').innerHTML = "";
            var tbl = '';
            //tbl += "<div class='card_body bg'>";
            tbl += "<canvas id='grf_reclamantes'></canvas>";
            //tbl += "</div>";
            document.getElementById('maiores_reclamantes_modal').innerHTML = tbl;

            const ctx = document.getElementById('grf_reclamantes').getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: resposta.cliente,
                    datasets: [{
                        label: "",
                        data: resposta.tot_cliente,
                        tension: 0.3, // Um valor entre 0 e 1. Quanto maior, mais suave/ondulada.                    
                        borderWidth: 1,
                        backgroundColor: "rgba(255,30,150,0.20",
                        borderColor: "rgb(255,99,132",
                        fill: false
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        title: {
                            display: false,
                            // text: 'Principais Tipos de Defeito em ' + anoMes,
                            font: {
                                // weight: 'bold',
                                size: 25,
                            },
                            color: '#F2480B',
                        },
                        datalabels: {
                            color: '#000',
                            anchor: 'center',
                            align: 'center',   // importante para barras horizontais
                            offset: 8,       // 👈 distância da barra
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        },
                    },
                    scales: {
                        x: {
                            display: false,
                            ticks: {
                                stepSize: 1,
                                font: {
                                    size: 16, // Set the desired font size in pixels
                                    //weight: 'bold'
                                },
                            }
                        },
                        y: {// This targets the y-axis scale
                            display: true,
                            ticks: {
                                font: {
                                    size: 16 // Set the desired font size in pixels
                                },
                            }
                        },
                    }
                }
            });
        },
        error: function (error) {
            //     // Código a ser executado em caso de erro
        }
    })
}


$(function () {
    $("#abre_modal_reclamantes").click(function () {
        $("#modal_reclamantes").modal('show');
    });
});


$(function () {
    $("#abre_modal_semanAno").click(function () {
        $("#modal_semanAno").modal('show');
    });
});


$(document).on('submit', '#form-semana-ano', function (e) {
    e.preventDefault(); // 🚫 impede submit normal

    const form = $(this);

    $.ajax({
        type: 'POST',
        url: form.attr('action') || '/week_modal/',
        data: form.serialize(),
        success: function (resposta) {
            console.log('SUCCESS AJAX');
            console.log(resposta.form);
            $('#recebe_semanAno_modelForm').html(resposta);
        },
        error: function (xhr) {
            console.error('ERRO AJAX', xhr.responseText);
            alert('Erro ao salvar');
        }
    });
});

function week_modal() {
    $.ajax({
        type: 'GET',
        url: '/qualidade/week_modal/',
        success: function (resposta) {
            $('#recebe_semanAno_modelForm').html(resposta);
            $('#modalSemanaAno').modal('show');
        },
        error: function () {
            alert('Tentando conectar na rota nova...')
        }
    });
}

$(function () {
    $("#acesso_navBar").click(function () {
        $(".navbar").css("display", "block");
    });
});