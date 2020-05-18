var socket = io("/room");  // Connect to namespace /room

var player_panels
var pseudo
var my_user_id
var nb_players = 10
var players

socket.emit("get_players_in_room")

socket.on("response_players_in_room", function(data){
    console.log("in response_players_in_room, data=", data)
    players = data.players
})

socket.emit("initialize_room")
socket.on("response_initialize_room", function(data){
    console.log("response_initialize_room, data=", data)
    player_panels = data.teams
    my_pseudo = data.pseudo
    my_user_id = data.user_id
    InitiatePannelButtons(nb_players, my_pseudo, my_user_id)
    createPanelsFromObject(player_panels, my_pseudo, my_user_id)
});


var home = document.getElementById("home");
home.addEventListener("click", function(){
    socket.emit("leave_room", {"current_url": window.location.href});
    // window.location = "/";
});

var go = document.getElementById("go");
go.addEventListener("click", function(e){
    e.preventDefault();
    console.log(socket);
    socket.emit("start_game");
});

socket.on("url_redirection", function(data){
    window.location = data.url;
});

socket.on("response_teams", function(data){
    player_panels = data.teams
    console.log("RETOUR player_panels", player_panels)
    createPanelsFromObject(player_panels, my_pseudo, my_user_id)
})

function InitiatePannelButtons(nb_players=10, pseudo, user_id) {
    blue_team_panel_body = document.getElementById("blue_team_panel_body")
    red_team_panel_body = document.getElementById("red_team_panel_body")
    
    blue_team_panel_body.appendChild(createPannelDiv(pseudo, user_id, index=0, color="blue", spy=true))
    red_team_panel_body.appendChild(createPannelDiv(pseudo, user_id, index=0, color="red", spy=true))
    nb_pannel_box = nb_players/2
    for (var i = 1; i < nb_pannel_box; i++) {
        blue_team_panel_body.appendChild(createPannelDiv(pseudo, user_id, index=i, color="blue"))
        red_team_panel_body.appendChild(createPannelDiv(pseudo, user_id, index=i, color="red"))
    }
}

function createPannelDiv(pseudo, user_id, index, color="blue", spy=false) {
    new_div = document.createElement('div')
    pannel_class = "panel-body"
    if (spy) {
        pannel_class += " spy-border"
        if (color == "red") {
            pannel_class += " red-border"
        }
    }
    if (color == "red") {
        pannel_id = "red-"
    } else {
        pannel_id = "blue-"
    }
    pannel_id += index
    new_div.setAttribute("id", pannel_id)
    new_div.setAttribute("class", pannel_class)
    new_join_button = createJoinButton(pseudo, user_id)
    new_div.appendChild(new_join_button)
    return new_div
}

function createJoinButton(pseudo, user_id) {
    new_button = document.createElement('button')
    new_button.setAttribute("class", "btn display-btn")
    new_button.textContent = "Rejoindre"
    new_button.addEventListener("click", function(e){ joinButtonCallback(this, pseudo, user_id) })
    return new_button
}

function joinButtonCallback(self, pseudo, user_id) {
    id = self.parentNode.id.split('-')
    team_color = id[0]
    index = id[1]
    player_panels[team_color][index] = user_id

    previous_player_div = document.getElementById(user_id)
    if (previous_player_div) {
        old_id = previous_player_div.parentNode.id.split('-')
        old_team_color = old_id[0]
        old_index = old_id[1]
        player_panels[old_team_color][old_index] = null
    }
    socket.emit("update_teams", player_panels)
}

function createPlayer(pseudo, user_id) {
    new_player = document.createElement('div')
    new_player.textContent = pseudo
    new_player.setAttribute("id", user_id)
    new_player.setAttribute("class", "pseudo-div")
    return new_player
}

function getPlayerTeam(user_id){
    player_location = document.getElementById(user_id)
    if (player_location) {
        if (player_location.parentNode.className.includes("red-border")) {
            return true
        }
    }
    return false
}
function playerIsSpy(user_id){
    player_location = document.getElementById(user_id)
    if (player_location) {
        if (player_location.parentNode.className.includes("spy-border")) {
            return true
        }
    }
    return false
}

function getPannelDiv(team_color, index){
    div_id = team_color + "-" + index
    return document.getElementById(div_id)
}


function createPanelsFromObject(player_panels, pseudo, user_id){
    nb_pannel_box = nb_players/2
    colors = ["blue", "red"]

    for (var c = 0; c < colors.length; c++) {
        color = colors[c]
        for (var i = 0; i < nb_pannel_box; i++) {
            var user_id2 = player_panels[color][i]
            div = getPannelDiv(color, i)
            div.removeChild(div.firstElementChild); 
            if (user_id2) {
                pseudo2 = getPseudoFromId(user_id2)
                div.appendChild(createPlayer(pseudo2, user_id2))
            } else {
                div.appendChild(createJoinButton(pseudo, user_id))
            }
        }
    }
}

function getPseudoFromId(user_id){
    for (var i = 0; i < players.length; i++) {
        p = players[i]
        if (p.id == user_id) {
            return p.pseudo
        }
    }
    return null
}

var debug_button = document.getElementById("debug_button");
debug_button.addEventListener("click", function(e){
    e.preventDefault();
    console.log("click debug_button!");
    // socket.emit("on_debug_button");
    // socket.emit("debug_button", {"current_url": window.location.href});
});
