var socket = io("/room");  // Connect to namespace /room

var home = document.getElementById("home");
home.addEventListener("click", function(){
    window.location = "/";
});

var go = document.getElementById("go");
go.addEventListener("click", function(e){
    e.preventDefault();
    console.log(socket);
    socket.emit("start_game");
});

/* Received when starting game */
socket.on("url_redirection", function(data){
    window.location = data.url;
});

/* Need to
 - Add listener on buttons to send "change_position" event with position code
 - Add function to update team display when receiving "teams_changed" event
    - Need to add / hide buttons if spot available
 */
function askChangePosition(event){
    var pos = event.target.dataset.pos;
    console.log(pos);
    socket.emit("change_position", pos);
}

function addJoinButtonListeners(){
    var buttons = document.getElementsByClassName('join-btn'),
        nbuttons = buttons.length;

    for (var i=0; i<nbuttons; i++){
        buttons[i].addEventListener('click', askChangePosition);
    }
}
addJoinButtonListeners();

// Updating teams

var red_panel = document.getElementById("red_team_panel_body"),
    blue_panel = document.getElementById("blue_team_panel_body");

var red_spy = red_panel.children[0], blue_spy = blue_panel.children[0];


function createButton(pos){
    var b = document.createElement("button");
    b.classList.add("btn"); b.classList.add("btn-default"); b.classList.add("join-btn");
    b.dataset.pos = pos;
    b.innerHTML = "Rejoindre";
    return b;
}
var b0 = createButton(0), b2 = createButton(2);
var b1 = red_panel.children[red_panel.childElementCount-1],
    b3 = blue_panel.children[blue_panel.childElementCount-1];

function createPseudoDiv(pseudo){
    var d = document.createElement("div");
    d.classList.add("pseudo-div");
    d.innerHTML = pseudo;
    return d;
}

function emptyTeams(){
    var nred = red_panel.children.length, nblue = blue_panel.children.length;
    // Spies
    red_panel.children[0].innerHTML = "";
    blue_panel.children[0].innerHTML = "";
    // Guessers
    for (var i=1; i<nred-1; i++){
        red_panel.removeChild(red_panel.children[i]);
    }
    for (var i=1; i<nblue-1; i++){
        blue_panel.removeChild(blue_panel.children[i]);
    }
}

socket.on('teams_changed', function(teams){
    console.log(teams);
    var tred = teams[0], tblue = teams[1];
    // Remove all
    emptyTeams();
    // Red team
    if (tred.spy == "None"){
        red_panel.children[0].append(b0);
    } else {
        red_panel.children[0].append(createPseudoDiv(tred.spy.pseudo));
    }
    for (var g=0; g<tred.length; g++){
        red_panel.insertBefore(createPseudoDiv(tred.guessers[g]), b1);
    }
    // Blue team
    if (tblue.spy == "None"){
        blue_panel.children[0].append(b2);
    } else {
        blue_panel.children[0].append(createPseudoDiv(tblue.spy.pseudo));
    }
    for (var g=0; g<tblue.length; g++){
        blue_panel.insertBefore(createPseudoDiv(tblue.guessers[g]), b1);
    }
    addJoinButtonListeners();
});


