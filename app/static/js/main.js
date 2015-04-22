/*global $, document */

$(document).ready(function () {
    'use strict';
    // Let's spruce up our progress bars:
    $('.progress .progress-bar').progressbar({
        transition_delay: 1500,
        use_percentage: true,
        display_text: 'fill'
        });
    $('#datafiletabs a:first').tab('show');
});
