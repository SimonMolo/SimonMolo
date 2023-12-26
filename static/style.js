$(document).ready(function () {
    // Lorsque le champ de saisie change, déclenche une requête AJAX pour obtenir des suggestions
    $('#name').on('input', function () {
        var input = $(this).val();

        // Envoyer une requête au serveur pour obtenir des suggestions
        $.ajax({
            url: '/get_user_suggestions',
            method: 'GET',
            success: function (data) {
                // Filtrer les suggestions basées sur l'entrée utilisateur
                var filteredSuggestions = data.filter(function (suggestion) {
                    return suggestion.toLowerCase().includes(input.toLowerCase());
                });

                // Mettre à jour la liste de suggestions
                updateSuggestions(filteredSuggestions);
            }
        });
    });

    // Fonction pour mettre à jour la liste de suggestions
    function updateSuggestions(suggestions) {
        // Supprimer toutes les suggestions actuelles
        $('#suggestions').empty();

        // Ajouter les nouvelles suggestions à la liste
        suggestions.forEach(function (suggestion) {
            $('#suggestions').append('<option value="' + suggestion + '">');
        });
    }
});
$(document).ready(function () {
    // Fonction pour obtenir les suggestions du parrain en temps réel
    function getParrainSuggestions(input) {
      $.post('/get_parrain_suggestions', { input: input }, function (data) {
        // Mettez à jour les suggestions dans le champ de saisie du parrain
        $('#parrain_name').autocomplete({
          source: data,
        });
      });
    }

    // Déclenchez la fonction à chaque changement dans le champ de saisie du parrain
    $('#parrain_name').on('input', function () {
      var inputText = $(this).val();
      getParrainSuggestions(inputText);
    });
  });