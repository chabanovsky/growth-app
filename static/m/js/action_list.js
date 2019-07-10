var verifyClass = ".verify";

$(document).ready(function() {
    $(verifyClass).click(function(event){
        event.preventDefault();
        href = event.target.href;

        loadHelper(href, function(data){
            if (data.status) {
                location.reload();
            } else {
                alert(data.msg);
            }
        }, function(){
            alert(localeManager.cannotReviewActionStr);
        })

        return false;
    });
})