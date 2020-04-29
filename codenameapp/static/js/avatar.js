var canvas = document.getElementById("av");
var context = canvas.getContext('2d');
var w = canvas.width, h = canvas.height;

function getCookie(key){
    var cookies = "; " + document.cookie;
    var parts = cookies.split("; "+key+"=")
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function drawAvatar(body, head, mouth){
    context.beginPath();
    context.strokeStyle = "#000000"
    // Body
    context.fillStyle = body;
    context.arc(w/2, h/2+110, 70, 0, Math.PI * 2); // Ici le calcul est simplifié
    context.fill();
    context.stroke();


    // Head
    context.fillStyle = head;
    context.arc(w/2, h/2, 50, 0, Math.PI * 2); // Ici le calcul est simplifié
    context.fill();

    context.beginPath(); // La bouche, un arc de cercle
    context.fillStyle = mouth;
    context.arc(w/2, h/2, 40, 0, Math.PI); // Ici aussi
    context.fill();

    context.beginPath(); // L'œil gauche
    context.arc(w/2 - 20, h/2 - 5, 20, (Math.PI / 180) * 220, (Math.PI / 180) * 320);
    context.stroke();

    context.beginPath(); // L'œil droit
    context.arc(w/2 + 20, h/2 - 5, 20, (Math.PI / 180) * 220, (Math.PI / 180) * 320);
    context.stroke();
}

backcol = document.getElementById("backcol");
mouthcol = document.getElementById("mouthcol");

backcol.addEventListener('change', function(e){
    drawAvatar(e.target.value, e.target.value, mouthcol.value);
});
mouthcol.addEventListener('change', function(e){
    drawAvatar(backcol.value, backcol.value, e.target.value);
});

var pseudo = getCookie("pseudo");
if (typeof pseudo == "undefined"){
    pseudo = ""
}
var col1 = getCookie("avatar-col1");
if (typeof col1 == "undefined"){
    col1 = "#ffff00"
}
else{
    col1 = "#" + col1;
}
var col2 = getCookie("avatar-col2");
if (typeof col2 == "undefined"){
    col2 = "#ff0000"
}
else{
    col2 = "#" + col2;
}
console.log(col1, col2);
drawAvatar(col1, col1, col2);

document.getElementById("nickname-input").value = pseudo;

