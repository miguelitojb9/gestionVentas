$(function () {
    var local_id = $("#local_id").val();
    var fecha = $('#fecha_n').val()


    $("#boton-eliminar-ventas").on('click', function () {
        // Obtener el token CSRF del cookie
        var csrftoken = getCookie('csrftoken');
        // Incluir el token CSRF en los encabezados de la solicitud AJAX
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': csrftoken,
            }
        });
        $.ajax({
            url: '/eliminar_ventas/',
            type: 'POST',
            data: {
                'fecha': fecha,
                'local': local_id,
                'csrfmiddlewaretoken': csrftoken,
            },
            success: function (data) {
                alert('Se eliminaron ' + data.total_eliminadas + ' ventas.');
                window.location.reload();
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Ocurrió un error al eliminar las ventas.');
            }
        });
    });


    $('.editar-venta-btn').on('click', function () {
        var ventaId = $(this).closest('tr[data-venta-id]').attr('data-venta-id');
        var cantidadVenta = $(this).closest('tr[data-venta-id]').find('td[data-id="cantidad_venta"]').text();
        var cantidadMerma = $(this).closest('tr[data-venta-id]').find('td[data-id="cantidad_merma"]').text();

        $(this).prop('disabled', true);
        $(this).closest('tr[data-venta-id]').find('td[data-id="cantidad_venta"]').html('<input type="number" class="form-control" value="' + cantidadVenta + '">');
        $(this).closest('tr[data-venta-id]').find('td[data-id="cantidad_merma"]').html('<input type="number" class="form-control" value="' + cantidadMerma + '">');
        $(this).closest('tr[data-venta-id]').find('td[data-id="cantidad_venta"] input').focus();

        $(this).closest('tr[data-venta-id]').find('td[data-id="cantidad_venta"] input, td[data-id="cantidad_merma"] input').on('keydown', function (event) {
            if (event.keyCode === 13) { // Verificar si se ha presionado la tecla "Enter"
                var nuevaCantidadVenta = $(this).closest('tr[data-venta-id]').find('td[data-id="cantidad_venta"] input').val();
                var nuevaCantidadMerma = $(this).closest('tr[data-venta-id]').find('td[data-id="cantidad_merma"] input').val();

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
                    url: '/actualizar_venta_diaria/',
                    data: {
                        'id': ventaId,
                        'cantidad_venta': nuevaCantidadVenta,
                        'cantidad_merma': nuevaCantidadMerma,
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


    // Configurar el botón de "Eliminar"
    $('.eliminar-venta-btn').on('click', function () {
        var ventaId = $(this).closest('tr[data-venta-id]').attr('data-venta-id');

        if (confirm('¿Está seguro de que desea eliminar esta venta?')) {
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
                url: '/eliminar_venta/',
                data: {
                    'id': ventaId,
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

    $('.nav-tabs a').on('shown.bs.tab', function (event) {
        // Actualizar URL con el hash de la pestaña activa
        history.pushState(null, null, event.target.hash);
    });
    // Seleccionar la pestaña activa según la URL
    if (window.location.hash) {
        $('.nav-tabs a[href="' + window.location.hash + '"]').tab('show');
    }
    $('.btn-cancelar').on('click', function () {
        window.location.reload();
    });
    const form = document.getElementById('new-venta');
    // Enviar el formulario cuando se envía el modal
    $('#new-venta').on('submit', function (event) {
        event.preventDefault();

        if (form.checkValidity()) {
            // El formulario es válido, enviarlo
            $('#crear-venta-modal').css('display', 'block');
            this.submit();


        } else {

            alert('Hay errores en el formulario');
        }

    });


});


// Detectar cuando se muestra una pestaña
// $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
//     // Obtener el ID de la pestaña que se muestra
//     var idPestana = $(e.target).attr('href');
//     var fecha_p = $(e.target).attr('id');
//     var local_id = $("#local_id").val();
//
//
//     // Si la pestaña contiene una tabla que aún no se ha inicializado con DataTables
//     if ($(idPestana + ' table').length > 0 && !$.fn.DataTable.isDataTable($(idPestana + ' table'))) {
//
//         // Inicializar DataTables en la tabla correspondiente
//
//         var tabla = $(idPestana + ' table').DataTable(
//             // Aquí debes definir las opciones de DataTables para la tabla correspondiente
//             {
//                 ajax: {
//                     url: '/ventas_diarias/',// Aquí debes definir la URL que devuelve los datos
//
//                     type: 'GET',
//                     // Si es necesario, define el método HTTP utilizado para la solicitud
//                     data: function (d) {
//                         // Si es necesario, puedes enviar datos adicionales en la solicitud
//                         return $.extend({}, d, {
//                             fecha: fecha_p,
//                             local_id: local_id,
//                         });
//                     }
//                 },
//                 "columns": [
//                     {"data": "id"},
//                     {"data": "producto"},
//                     {"data": "fecha"},
//                     {"data": "cantidad_disponible"},
//                     {"data": "cantidad_merma"},
//                     {"data": "cantidad_venta"},
//                     {"data": "precio_venta_producto"},
//                     {"data": "importe_precio_venta"},
//                     {"data": "precio_costo_producto"},
//                     {"data": "importe_precio_costo"},
//                     {
//                         "data": null,
//                         "defaultContent": '<a class="btn btn-warning btn-sm editar-venta-btn"><span class="glyphicon glyphicon-pencil" aria-hidden="true"></span></a><a class="btn btn-danger btn-sm eliminar-venta-btn"><span class="glyphicon glyphicon-trash" aria-hidden="true"></span></a>'
//                     }
//                 ],
//                 // Aquí debes definir las opciones de DataTables
//                 createdRow: function (row, datos, indice) {
//                     $('td:eq(4)', row).attr('data-id', 'cantidad_merma');
//                     $('td:eq(5)', row).attr('data-id', 'cantidad_venta');
//                 },
//                 columnDefs: [
//                     {
//                         targets: -1, // Último columna
//                         data: null, // Usar el objeto de datos completo
//                         defaultContent: '<button class="btn btn-primary btn-editar"><i class="fas fa-pencil-alt"></i> Editar</button>'
//                     }
//                 ]
//             }
//         );
//     }
// });
