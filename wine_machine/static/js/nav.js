
(function(){

    $('#sidebar-top-level-items').find('li').filter(function(){
        return $(this).find('>a[href="' + location.pathname + '"]').length > 0;
    }).addClass('active');

    $('.header-content .navbar-nav').find('li').filter(function(){
        return $(this).find('>a[href="' + location.pathname + '"]').length > 0;
    }).addClass('chose');

    $('#signout').click(function(event){
        event.preventDefault();
        var req_data = {}
        $.ajax({
            type: 'POST',
            contentType: 'application/json; charset=UTF-8',
            url: '/api/logout',
            data: JSON.stringify(req_data),
            dataType: 'json',
            success: function(res_data) {
                window.location = '/login';
            },
            error: function(error) {
                window.location = '/login';
            }
        });
    });

    $('.dropdown-menu-toggle').on('click', function() {
        if($(this).attr('aria-expanded') == 'false') {
            $(this).attr('aria-expanded', 'true');
            $(this).closest('.dropdown').addClass('open');
        } else {
            $(this).attr('aria-expanded', 'false');
            $(this).closest('.dropdown').removeClass('open');
        }
        return false;
    });

    $('.dropdown-menu').on('click', 'a', function(){
        $('.dropdown-menu-toggle').click();
        $(this).closest('.dropdown').find('.dropdown-toggle-text').attr('val', $(this).attr('val')).text($(this).text());
        return false;
    });

    $(document.body).on('click', '.view_task', function() {
        var task_id = $(this).find('span').attr('val');
        window.location = '/task_detail?task_id=' + task_id;
        return false;
    });

})();
