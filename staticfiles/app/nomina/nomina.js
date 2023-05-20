$(function () {
 // Configurar el botón de "Eliminar"
    $('.descargar_excel').on('click', function () {
        var asistencia_id = $(this).closest('tr[data-asistencia-id]').attr('data-asistencia-id');
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

    });

});