// Pseudo input
function getCookie(key, default_val){
    var cookies = "; " + document.cookie;
    var parts = cookies.split("; "+key+"=")
    if (parts.length == 2) return parts.pop().split(";").shift();
    return default_val;
}

var pseudo = getCookie("pseudo", "");
document.getElementById("inputPseudo").value = pseudo;

// Avatar handling
var index = 0;
var avatar = document.getElementById("avatar");

var imagesUrls = [avatar.src];

function updateImg(){
    avatar.src = imagesUrls[index];
}
function nextImg(){
    index = (index + 1) % imagesUrls.length;
    updateImg();
}
function prevImg(){
    index = (index - 1 + imagesUrls.length) % imagesUrls.length;
    updateImg();
}

// Preload images
function preloadImg(){
    var req = new XMLHttpRequest();
    req.open('GET', '/avatar/random');
    req.addEventListener('readystatechange', function() {
        if (req.readyState === XMLHttpRequest.DONE) {
            var resp = JSON.parse(req.responseText);
            imagesUrls.push(resp.url);
        }
    });
    req.send(null);
}

// TODO preload only when main is loaded
var n_preload = 5;
for (var i=0; i<n_preload; i++){ preloadImg() }

