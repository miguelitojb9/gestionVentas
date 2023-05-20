$(function () {

    // Configurar el botón de "Eliminar"
    $('.eliminar-btn').on('click', function () {
        var trabajador_id = $(this).closest('tr[data-trabajador-id]').attr('data-trabajador-id');

        if (confirm('¿Está seguro de que desea eliminar este trabajador?')) {
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
                url: '/eliminar_trabajador/',
                data: {
                    'id': trabajador_id,
                },
                success: function (response) {
                    console.log('Eliminación de trabajador exitosa:', response);
                    window.location.reload();
                },
                error: function (error) {
                    console.error('Error al eliminar trabajador:', error);
                }
            });
        }
    });


    $('.editar-btn').on('click', function () {
        var ventaId = $(this).closest('tr[data-trabajador-id]').attr('data-trabajador-id');
        var nombre = $(this).closest('tr[data-trabajador-id]').find('td[data-id="nombre"]').text();
        var salario_basico = $(this).closest('tr[data-trabajador-id]').find('td[data-id="salario_basico"]').text();

        $(this).prop('disabled', true);
        $(this).closest('tr[data-trabajador-id]').find('td[data-id="nombre"]').html('<input type="text" class="form-control" value="' + nombre + '">');
        $(this).closest('tr[data-trabajador-id]').find('td[data-id="salario_basico"]').html('<input type="number" class="form-control" value="' + salario_basico + '">');
        $(this).closest('tr[data-trabajador-id]').find('td[data-id="salario_basico"] input').focus();

        $(this).closest('tr[data-trabajador-id]').find('td[data-id="nombre"] input, td[data-id="salario_basico"] input').on('keydown', function (event) {
            if (event.keyCode === 13) { // Verificar si se ha presionado la tecla "Enter"
                var nombre = $(this).closest('tr[data-trabajador-id]').find('td[data-id="nombre"] input').val();
                var salario_basico = $(this).closest('tr[data-trabajador-id]').find('td[data-id="salario_basico"] input').val();

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
                    url: '/actualizar_trabajador/',
                    data: {
                        'id': ventaId,
                        'nombre': nombre,
                        'salario_basico': salario_basico,
                        'csrfmiddlewaretoken': csrftoken,
                    },
                    beforeSend: function () {
                        // Agregar una capa de carga con la biblioteca "jQuery Loading Overlay"
                        // Mostrar el indicador de carga antes de enviar la solicitud AJAX
                        document.getElementById("loading-indicator").style.display = "block";
                    },
                    success: function (response) {
                        console.log('Actualización de venta exitosa:', response);
                        location.reload();
                    },
                    error: function (error) {
                        console.error('Error al actualizar venta:', error);
                    },
                    complete: function () {
                        // Ocultar el indicador de carga después de completar la solicitud AJAX
                        document.getElementById("loading-indicator").style.display = "none";
                    }
                });
            }
        });
    });


}); // Función para obtener el valor de una cookie por su nombre
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
