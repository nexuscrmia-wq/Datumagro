// Local: static/js/main.js

/**
 * Este evento garante que todo o código JavaScript dentro dele só será executado
 * depois que a página HTML estiver completamente carregada e pronta.
 * É uma boa prática fundamental para evitar erros.
 */
document.addEventListener('DOMContentLoaded', () => {

    // 1. Mensagem de verificação
    // Imprime uma mensagem no console do navegador para confirmar que o arquivo foi carregado.
    console.log('DatumAgro JS Carregado com Sucesso!');

    // 2. Lógica Futura
    // Aqui é onde vamos adicionar a lógica de interatividade do DatumAgro, como:
    //  - Funções para buscar dados da nossa API e desenhar os gráficos do dashboard.
    //  - Lógica para menus interativos.
    //  - Validações de formulários antes de serem enviados.

    // Exemplo de uma função simples
    function exemploFuncao() {
        console.log('Uma função de exemplo foi chamada.');
    }

    // Chamando a função para teste
    exemploFuncao();

});