$(function () {
    // Configurar el botón de "Eliminar"
    $('.eliminar-asistencia-btn').on('click', function () {
        var asistencia_id = $(this).closest('tr[data-asistencia-id]').attr('data-asistencia-id');

        if (confirm('¿Está seguro de que desea eliminar esta asistencia?')) {
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
                url: '/eliminar_asistencia/',
                data: {
                    'id': asistencia_id,
                },
                success: function (response) {
                    console.log('Eliminación de venta exitosa:', response);
                    window.location.reload();
                },
                error: function (error) {
                    console.error('Error al eliminar venta:', error);
                }
            });
        }
    });

    //flastPicker


    var hoy = new Date(); // Obtiene la fecha actual
    // var tresDiasDespues = new Date(hoy.getTime() + (3 * 24 * 60 * 60 * 1000)); // Calcula la fecha tres días después
    var fecha_entrega;
    flatpickr('#id_fecha', {
        inline: true,
        static: true,
        height: "50px",
        width: "50px",
    });

});

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
