$(function () {

    // Configurar el botón de "Eliminar"
    $('.eliminar-btn').on('click', function () {

        var gasto_id = $(this).closest('tr[data-id]').attr('data-id');


        if (confirm('¿Está seguro de que desea eliminar esta gasto?')) {
            // Obtener el token CSRF del cookie
            var csrftoken = getCookie('csrftoken');

            // Incluir el token CSRF en los encabezados de la solicitud AJAX
            $.ajaxSetup({
                headers: {
                    'X-CSRFToken': csrftoken,
                }
            });

            $.ajax({
                type: 'POST',
                url: '/eliminar_gasto/',
                data: {
                    'id': gasto_id,
                },
                success: function (response) {
                    console.log('Eliminación de gasto exitosa:', response);
                    window.location.reload();
                },
                error: function (error) {
                    console.error('Error al eliminar gasto:', error);
                }
            });
        }
    });
    // Función para obtener el valor de una cookie por su nombre
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }


});