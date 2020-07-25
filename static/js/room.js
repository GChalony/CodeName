var socket;

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

function createButton(pos){
    var b = document.createElement("button");
    b.classList.add("btn"); b.classList.add("btn-default"); b.classList.add("join-btn");
    b.dataset.pos = pos;
    b.innerHTML = "Rejoindre";
    return b;
}

function createPseudoDiv(user){
    var d = document.createElement("div");
    d.classList.add("pseudo-div");
    var av = new Image();
    av.classList.add("icon");
    av.src = user.avatar_src
    d.append(av);
    d.innerHTML += user.pseudo;
    return d;
}

function emptyTeams(){
    var red_panel = document.getElementById("red_team_panel_body"),
        blue_panel = document.getElementById("blue_team_panel_body"),
        nred = red_panel.children.length,
        nblue = blue_panel.children.length;

    // Spies
    red_panel.getElementsByClassName("spy-container")[0].innerHTML = "";
    blue_panel.getElementsByClassName("spy-container")[0].innerHTML = "";
    // Guessers
    for (var i=1; i<nred; i++){
        red_panel.removeChild(red_panel.children[1]);
    }
    for (var i=1; i<nblue; i++){
        blue_panel.removeChild(blue_panel.children[1]);
    }
}

function create_teams(teams){
    console.log(teams);
    var red_panel = document.getElementById("red_team_panel_body"),
        blue_panel = document.getElementById("blue_team_panel_body");
    var b0 = createButton(0), b2 = createButton(2);

    var tred = teams[0], tblue = teams[1];
    // Red team
    if (tred.spy == "None"){
        red_panel.children[0].append(b0);
    } else {
        red_panel.children[0].append(createPseudoDiv(tred.spy));
    }
    for (var g=0; g<tred.guessers.length; g++){
        red_panel.append(createPseudoDiv(tred.guessers[g]));
    }
    // Blue team
    if (tblue.spy == "None"){
        blue_panel.children[0].append(b2);
    } else {
        blue_panel.children[0].append(createPseudoDiv(tblue.spy));
    }
    for (var g=0; g<tblue.guessers.length; g++){
        blue_panel.append(createPseudoDiv(tblue.guessers[g]));
    }
    addJoinButtonListeners();
}

function change_teams(teams){
    emptyTeams();
    create_teams(teams);
}


$(function(){
    socket = io("/room");

    var go = document.getElementById("go");
    if (go !== null) {
        // Creator of the game
        go.addEventListener("click", function(e){
            e.preventDefault();
            console.log(socket);
            socket.emit("start_game");
        });

        socket.on('toggle_start', function(on){
            console.log("toggling: " + on);
            if (on == 0){
                go.disabled = true;
            }
            else{
                go.disabled = false;
            }
        });
    }

    /* Received when starting game */
    socket.on("url_redirection", function(data){
        window.location = data.url;
    });

    addJoinButtonListeners();

    socket.on('teams_changed', change_teams);
});