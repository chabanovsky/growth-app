var applyClassTag = ".smbent"

$(document).ready(function() {
    $(applyClassTag).click(function(event){
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
            alert("Cannot send verify request.");
        })

        return false;
    });

})