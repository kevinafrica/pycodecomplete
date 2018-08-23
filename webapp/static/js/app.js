let get_text_data = function () {
    let text = $("textarea#code-input").val()
    return { 'text': text }
};

let send_text_json = function (text) {
    $.ajax({
        url: '/predict',
        contentType: "application/json; charset=utf-8",
        type: 'POST',
        success: function (data) {
            display_prediction(data);
            console.log("predict")
        },
        data: JSON.stringify(text)
    });
};

let display_prediction = function (data) {
    $("span#solution").html(data['prediction'])
};

$(function ()
{
    $('textarea#code-input').keyup(function () {
        let text = $("textarea#code-input").val()
        console.log(text)

        let text_json = get_text_data();
        send_text_json(text_json);
    });
});




$(document).ready(function() {

    $("button#predict").click(function() {
        let text_json = get_text_data();
        send_text_json(text_json);
    })

})