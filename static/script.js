//Using our API

function login(){
    var uname = document.getElementById("uname").value;
    var passw = document.getElementById("passw").value;
    var code = document.getElementById("code").value;  // Add this line to get the TOTP code

    var dat = {'username':uname, 'password':passw, 'code': code};  // Pass the TOTP code to the server

    $.ajax('/api/v1.0/storeLoginAPI/',{
        method: 'POST',
        data: JSON.stringify(dat),
        dataType: "json",
        contentType: "application/json",
    }).done(function(res){
        if (res['status'] === 'success'){
            $("#stat").html('<b>Successful Login<b>');
        } else if (res['status'] === 'totp_fail') {
            $("#stat").html('<b>Incorrect TOTP Code</b>');
        } else {
            $("#stat").html('<b>Login Failed</b>');
        }
    }).fail(function(err){
        $("#stat").html(err);
    });
}


function search() {
    var item = document.getElementById("searchItem").value;

    $.ajax('/api/v1.0/storeAPI/' + item, {
        method: 'GET',
    }).done(function (res) {

        $(".res").remove(); //remove previous results

        $(res).each(function () {
            var r = "<tr class='res'><td>" + this['name'] + "</td>";
            // Display the image using the <img> tag
            r += "<td><img src=" + this['image'] + "></td>"; // xss vulnerability. insert "/><script>alert('heyyy')</script>
            r += "<td>" + this['price'] + "</td></tr>";
            $("#results").append(r);
        });

    }).fail(function (err) {
        $("#stat").html(err);
    });
}

function addItem(){
    var name = document.getElementById("itemName").value;
    var img = document.getElementById("itemImage").value;
    var price = document.getElementById("itemPrice").value;
    if (/[<>]/.test(img)) {
        $("#stat").html("Please enter only letters, numbers, spaces, /, \\, ;, or + in the image link.");
        return;
    }

    var dat = {'name':name, 'image':img, 'price':price};


    $.ajax('/api/v1.0/storeAPI',{
        method: 'POST',
        data: JSON.stringify(dat),
        dataType: "json",
        contentType: "application/json",
    }).done(function(res){
        $("#stat").html("Successfully Added");
    }).fail(function(err){
        $("#stat").html("Error Sending Request");
    });
}

$(document).ready(function(){

    $("#navbar ul li a").on('click', function(event){
        event.preventDefault();
        var page = $(this).attr("href");

        $("#main").load(page);
    });
});
