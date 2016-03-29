/*global $, document */

var csrftoken = $('meta[name=csrf-token]').attr('content');

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        'use strict';
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


function update_metadata_progress(status_url, l, year, doy) {
        // send GET request to status URL
        console.log('updating status...')
        $.getJSON(status_url, function(data) {
            // update UI
            console.log(data)
            if (data['state'] == 'FAILURE') {
                l.stop()
                $('#xlsButton').html('<span class="ladda-label">Error creating metadata file</span>');
                $('#xlsButton').prop("onclick", "");
                $('#xlsButton').attr("data-color","red");
            }
            else if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
                // show result
                l.stop()
                $('#xlsButton').prop("href", data['url']);
                $('#xlsButton').html('<span class="ladda-label">View metadata</span>');
                $('#xlsButton').prop("onclick", "");
                console.log(data['state'])
            }
            else {
                // rerun in 2 seconds
                console.log(data['state'])
                console.log(data)
                setTimeout(function() {
                    update_metadata_progress(status_url, l, year, doy);
                }, 500);
            }
        });
    }

function create_metadata(year, doy) {
    'use strict';
    var l = Ladda.create(document.querySelector( '#BuildButton' ));
    console.log(year)
    console.log(doy)
    console.log(l)
    l.start();
    $.ajax({
        type: "POST",
        url: '../../ajax/create_metadata',
        data: {
            'year': year,
            'doy': doy
        },
        success: function (data, status, request) {
            console.log('hello');
            console.log(request.getResponseHeader('Location'));
            update_metadata_progress(request.getResponseHeader('Location'), l, year, doy);
        },
        error: function (response) {
            l.stop();
            $('#BuildButton').html("Oops! It didn't work.");
            $('#BuildButton').prop("onclick", "");
            $('#BuildButton').attr("data-color","red");
        }
    });
}
