// Pseudo input
function getCookie(key, default_val){
    var cookies = "; " + document.cookie;
    var parts = cookies.split("; "+key+"=")
    if (parts.length == 2) return parts.pop().split(";").shift();
    return default_val;
}

var pseudo = getCookie("pseudo", "");
document.getElementById("inputPseudo").value = decodeURI(pseudo);

// Avatar handling
var index = 0;
var avatar = document.getElementById("avatar");

var imagesUrls = [avatar.attributes['src'].value];

function updateImg(){
    // Could directly use _images array, but I like not to rely on it
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

function getImagesURLs(n){
    var req = new XMLHttpRequest();
    req.open('GET', '/avatar/random?t=' + Date.now() + '&n='+n);
    req.addEventListener('readystatechange', function() {
        if (req.readyState === XMLHttpRequest.DONE) {
            var resp = JSON.parse(req.responseText);
            console.log(resp);
            resp.forEach(function(val, i){
                imagesUrls.push(val.url);
                cacheImg(val.url);
            });
        }
    });
    req.send(null);
}

function cacheImg(url){
    var img = new Image();
    img.src = url;
    img.onload = () => console.log(url + " cached ?");
}

var N_PRELOAD = 10;

$(function(){
    getImagesURLs(N_PRELOAD);
});
