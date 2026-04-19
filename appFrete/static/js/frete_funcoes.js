var controleCampo = 1;
window.adicionarCampo = function () { // Adicione 'window.' aqui    
    controleCampo++;
    // alert('entrei')
    console.log(controleCampo);

    document.getElementById('dimensoes').insertAdjacentHTML('beforeend', '<div class="form-group row" id="campo' + controleCampo + '"><div   class="col" style="text-align: center;">' + controleCampo + '</div><div class="col dimens_red"><input type="text" name="comprimento" id="comprimento" oninput="check_dim(this)" pattern="\\d{1,3}" placeholder="comprimento" required></div><div class="col dimens_red"><input type="text" name="largura" id="largura" oninput="check_dim(this)" pattern="\\d{1,3}"  placeholder="largura" required></div><div class="col dimens_red"><input type="text" name="altura" id="altura" oninput="check_dim(this)" pattern="\\d{1,3}"  placeholder="altura" required></div><div class="col dimens_cyan"><input type="text" name="volume" id="volume" oninput="check_dim(this)" pattern="\\d{1,4}"  placeholder="volume" required></div><div class="col dimens_black"><input type="text" name="unidades" id="unidades" oninput="check_dim(this)" pattern="\\d{1,4}"  placeholder="unidades" required></div><div class="col larg_botao"><button type="button" id="' + controleCampo + '" class = "campo_neg" onclick="removerCampo(' + controleCampo + ')"> - </button></div></div>');

}

window.removerCampo = function (idCampo) { // E aqui também
    //console.log("Campo remover: " + idCampo);
    document.getElementById('campo' + idCampo).remove();
}

window.removerCampo = function (idCampo) { // E aqui também
    //console.log("Campo remover: " + idCampo);
    document.getElementById('campo' + idCampo).remove();
}

window.check = function (input) {
    if (!/^\d{1,}$/g.test(input.value)) {
        input.reportValidity()
    }
}

window.check_dim = function (input) {
    if (!/^\d{1,3}$/g.test(input.value)) {
        input.reportValidity()
    }
}

window.check_vol = function (input) {
    if (!/^\d{1,4}$/g.test(input.value)) {
        input.reportValidity()
    }
}

window.check_cep = function (input) {
    if (!/^([0-9]{5})\-?([0-9]{1})([0-9]{1})([0-9]{1})$/g.test(input.value)) {
        input.reportValidity()
    }
}

window.myFunction = function() {
    if (document.getElementById('botao').innerHTML == 'Mostrar Produtos') { ;
        document.getElementById('myDIV').style.display = "block";
        document.getElementById('botao').innerHTML = 'Ocultar Produtos';
        document.getElementById('botao').style.background = '#d10';

        btn = document.getElementById("botao");
        btn.style.color = 'white';

    } else {
        document.getElementById('botao').innerHTML = 'Mostrar Produtos';
        // document.getElementById('botao').style.background = "#40E0D0";
        document.getElementById('botao').style.background = "#000";

        btn = document.getElementById("botao");
        btn.style.color = 'white';

        document.getElementById('myDIV').style.display = "none";

    }
}

$(document).ready(function () {
    // 1. MÁSCARAS VISUAIS
    // Para inteiros (Ex: 1.500)
    $('.mask-inteiro').mask('#.##0', { reverse: true });

    // Para decimais/moeda (Ex: 1.250,50)
    $('#valor_total, .mask-money').mask('#.##0,00', { reverse: true });

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
    
})


