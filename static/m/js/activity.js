var submitActionInputTag = "#submit-action"
var submitActionButtonTag = "#submit-action-button"
var submitActionEndpoint = "/api/submit_action"
var activityIdTag = "#activity-id"

$(document).ready(function() {
    submitActionSetup();
})

function submitActionSetup() {
    $(submitActionInputTag).keypress(function (e) {
        if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
            $(submitActionButtonTag).click();
            return false;
        } else {
            return true;
        }
    });
    $(submitActionButtonTag).click(function(event){
        event.preventDefault();
        var link = $(submitActionInputTag).val();
        var url = submitActionEndpoint + "?link=" + encodeURIComponent(link) + "&activity_id=" + $(activityIdTag).text()
        loadHelper(url, function(data){
            if (data.status) {
                alert(data.msg);
                location.reload();
            } else {
                alert(data.msg);
            }
        }, function(){
            alert(localeManager.cannotSubmitActionStr);
        });
    })
}

function build_url(base_url) {
    return base_url
}
