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
    //display_txt = display_txt.replace(/\n/g, "<br />");
    $("span#solution1").html(data['prediction_1'].replace(/\n/g, "<br />"))
    //$("span#solution2").html(data['prediction_2'].replace(/\n/g, "<br />"))
    //$("span#solution3").html(data['prediction_3'].replace(/\n/g, "<br />"))
    //$("span#solution4").html(data['prediction_4'].replace(/\n/g, "<br />"))
};

$(function ()
{
    $('textarea#code-input').keyup(function () {

        delay(function(){
            
        let text = $("textarea#code-input").val()
        console.log(text)

        let text_json = get_text_data();
        send_text_json(text_json);

        
          }, 1000 );
    });
});

var delay = (function(){
    var timer = 0;
    return function(callback, ms){
      clearTimeout (timer);
      timer = setTimeout(callback, ms);
    };
  })();


$(document).ready(function() {

    $("button#predict").click(function() {
        let text_json = get_text_data();
        send_text_json(text_json);
    })

})