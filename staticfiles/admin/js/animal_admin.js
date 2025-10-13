// Garante que o código só rode quando o jQuery do admin do Django estiver pronto
if (typeof django !== 'undefined' && typeof django.jQuery !== 'undefined') {
    (function($) {
        $(document).ready(function() {
            // Seleciona os campos pelos IDs que o Django cria para os formulários
            var sexoField = $('#id_sexo');
            var statusReprodutivoField = $('.form-row.field-status_reprodutivo');
            var isReprodutorField = $('.form-row.field-is_reprodutor');

            function toggleFields() {
                var selectedSexo = sexoField.val();
                if (selectedSexo === 'F') { // Se for Fêmea
                    statusReprodutivoField.show(); // Mostra o status reprodutivo
                    isReprodutorField.hide();      // Esconde a opção de ser reprodutor
                } else if (selectedSexo === 'M') { // Se for Macho
                    statusReprodutivoField.hide();      // Esconde o status reprodutivo
                    isReprodutorField.show();         // Mostra a opção de ser reprodutor
                } else { // Se nenhum sexo for selecionado
                    statusReprodutivoField.hide();
                    isReprodutorField.hide();
                }
            }

            // Executa a função assim que a página carrega, para o estado inicial
            toggleFields();

            // Executa a função toda vez que o campo 'sexo' for alterado pelo usuário
            sexoField.change(function() {
                toggleFields();
            });
        });
    })(django.jQuery);
}