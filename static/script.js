//Using our API

function login() {
    console.log("login running")
    var uname = document.getElementById("uname").value;
    var passw = document.getElementById("passw").value;

    var dat = { 'username': uname, 'password': passw, 'email': '', 'code': '123' };

    $.ajax('/api/v1.0/storeLoginAPI/', {
        method: 'POST',
        data: JSON.stringify(dat),
        dataType: "json",
        contentType: "application/json",
    }).done(function (res) {
        console.log(res);

        if (res['status'] === 'success') {
            console.log("success")
            // Hide the initial login form
            $("#loginForm").hide();

            // Show the verification code form
            $("#codeForm").show();

            console.log("API Response:", res);
            // Display the email in the placeholder
            var email = res["email"];
            console.log("email:", email)
            document.getElementById("emailDisplay").innerHTML = "Enter verification code sent to " + email;

            // Clear previous status messages
            $("#stat").html('');
        } else {
            $("#stat").html('<b>Login Failed</b>');
        }
    }).fail(function (err) {
        console.log(err);
        $("#stat").html(err);
    });
}

function submitCode() {
    var code = document.getElementById("code").value;

    // For now, use a static code "123" for demonstration
    if (code === "123") {
        $("#stat").html('<b>Code Submitted Successfully<b>');
        // Perform additional actions on successful code submission
        // For example, you can redirect the user to another page or perform other actions
    } else {
        $("#stat").html('<b>Incorrect Code</b>');
    }
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
