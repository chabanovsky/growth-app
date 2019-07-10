var submitButtonTag = "#submit";
var descriptionTag = "#description";
var metaPostLinkTag = "#meta-post-link";
var locationTag = "#location";
var dateTimeTag = "#date-time";
var titleTag = "#title";
var chatLinkTag = "#chat-link"
var tabTag = "#event-type";

var submitEndpoint = "/api/submit_event/"

$(document).ready(function() {
    setupSubmit();
})

function setupSubmit() {
    $(submitButtonTag).click(function(event){
        event.preventDefault();
        var data = new Object();

        data.tab = $(tabTag).text()
        data.title = $(titleTag).val()
        data.description = $(descriptionTag).val();
        data.meta = $(metaPostLinkTag).val();
        data.date = $(dateTimeTag).val()
        data.chat = $(chatLinkTag).val()

        if (data.title.length == 0 ||
            data.description.length == 0 ||
            data.meta.length == 0 ||
            data.date.length == 0 ||
            data.chat.length == 0) {
            alert("Please, fill all fields.");
            return;
        }

        if (data.tab == "meetups") {
            data.location = $(locationTag).val();
            if (data.location.length == 0) {
                alert("Please, fill all fields.");
                return;
            }
        }

        $.ajax({
            type: "POST",
            url: submitEndpoint,
            data: JSON.stringify(data),
            contentType: "application/json",
            success: function(data){
                if (data.status) {
                    alert(data.msg);
                    location.reload();
                } else {
                    alert(data.msg);
                }
            },
            error: function(data){
                alert(localeManager.cannotSubmitEventStr);
            }
        });
    })
}
