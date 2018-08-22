let get_text_data = function() {
    let text = $("input#txt").val()

    return {'text': text} 
};

let send_text_json = function(text) {
    $.ajax({
        url: '/submit-predict',
        contentType: "application/json; charset=utf-8",
        type: 'POST',
        success: function (data) {
            display_solutions(data);
            console.log("hi")
        },
        data: JSON.stringify(text)
    });
};

let display_solutions = function(data) {
    $("span#solution").html(data['prediction'])
};


$(document).ready(function() {

    $("button#predict").click(function() {
        let text_json = get_text_data();
        send_text_json(text_json);
    })

})