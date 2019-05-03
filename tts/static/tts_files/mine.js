var make_btn_init = function(){
    $('#btn_image').attr('style', '');
    $('#btn_image').addClass('StartBtn__hidden___3Bku8');
    $('#btn_submit').removeClass('StartBtn__loading___BX_Ck').addClass('StartBtn__playing___2ci2H');
    $('#btn_submit').attr('disabled', null);
}
$('#text').on('click', function() {
    $('#text').val('');
    fill_text(txt_list[play_index]);
    play_index = play_index + 1;
    if(play_index == txt_list.length) {
        play_index = 0;
    }
});

$('.Voice__rect___39b3s').on('click', function(){
    $('.Voice__rect___39b3s').removeClass('Voice__active___3ctKE');
    $(this).addClass('Voice__active___3ctKE');
    tts_name = $(this).attr('tts_name');
});

var tts_name = 'hecuiru';

$("#btn_submit").on('click', function() {
    $('#btn_image').attr('style', 'top: 100px; left: 43px;');
    $('#btn_image').removeClass('StartBtn__hidden___3Bku8');
    $('#btn_submit').removeClass('StartBtn__playing___2ci2H').addClass('StartBtn__loading___BX_Ck');
    $.ajax({
        url: '/do_tts',
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify({'text': $('#text').val(), 'tts_name': tts_name}),
        dataType: 'json',
        success: function (json) {
            if (json.code == 200 && json.data) {
                $('#audio').attr('src', json.data + '?ts=' + new Date().getTime());
                $('#audio')[0].play();
                return;
            } else {
                make_btn_init();
            }
        },
        error: function(error) {
            make_btn_init();
        },
    });
    $('#btn_submit').attr('disabled', 'disabled');
    return false;
});
$('#audio').on('ended', function(){
    make_btn_init();
});

var play_index = 0;

var fill_text = function(text, callback) {
    for(var ic = 0 ; ic < text.length ; ic++) {
        (function(ic) {
            setTimeout(function() {
                $('#text').val($('#text').val() + text[ic]);
            }, 80 * (ic + 3));
        })(ic);
    }
}
