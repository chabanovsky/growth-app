function loadHelper(url, onSuccess, onError) {
    $.ajax({
        url: url,
        method: 'GET',
        success: onSuccess,
        error: onError
    });
}

var smbAlertTag = ".smbalrt"
$(document).ready(function() {
    $(smbAlertTag).click(function(event){
        event.preventDefault();
        href = event.target.href;

        loadHelper(href, function(data){
            if (data.status) {
                alert(data.msg)
                window.location.reload();
            } else {
                alert(data.msg)
            }
        }, function(){
            alert("Something went wrong. Please try again later.");
        })

        return false;
    });

})