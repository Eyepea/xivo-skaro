
function certinit(mode) {
    $('#it-validity-end-format').css('display','none');

    if(mode == "add")
    {
        $('#fd-validity-start').css('display','none');
        $('#fd-fingerprint').css('display','none');
        $('#fd-length_text').css('display','none');
        $('#it-validity-end').datepicker({
            changeMonth: true,
            changeYear: true,
            minDate: +1,
            altField: '#it-validity-end-format',
            altFormat: 'yy-mm-dd'
        });

        cacheck = function() {
            var c1 = $('#it-CA').attr('checked');
            var c2 = $('#it-autosigned').attr('checked');

            if(c1 || c2)
            {
                $('#fd-ca_authority').css('display','none');
                $('#fd-ca_password').css('display','none');
            } else {
                $('#fd-ca_authority').css('display','block');
                $('#fd-ca_password').css('display','block');
            }
        };

        $('#it-CA').click(cacheck);
        $('#it-autosigned').click(cacheck);

        // called once to init when redisplayed form after an error
        cacheck();

    } else {
        $('input').attr('disabled','true').addClass('it-disabled');

        $('#fd-ca_authority').css('display','none');
        $('#fd-ca_password').css('display','none');
        $('#fd-password').css('display','none');
        $('#fd-length').css('display','none');
        $('#fd-cipher').css('display','none');

        if ($('#it-CA').attr('checked'))
            $('#fd-autosigned').css('visibility','hidden');
    }
}

