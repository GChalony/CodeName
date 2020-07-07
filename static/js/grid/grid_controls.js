var socket;
function initGrid(){
    socket = io("/grid");

    var toastContent = $('#toast').children()[0]

    socket.on('disconnect', function(){
        console.log('Disconnected');
        toastContent.innerText = "Déconnecté";
        $('#toast').toast('show');
    });
    socket.on('connect', function(){
        console.log('Connected');
        toastContent.innerText = "Connecté";
        $('#toast').toast('show');
    });

    votes = []

    function drawVotes(cell, n){
        // draw votes during voting phase
        cell.style.backgroundImage = "url('/static/vote.png'),".repeat(n).slice(0, -1);
        var pos = "";
        for (var i=0; i<n; i++){
            pos += 100 - n - 2 + "%,";
        }
        cell.style.backgroundPositionX = pos.slice(0, -1);
        cell.style.backgroundPositionY = "2%";
        cell.style.backgroundRepeat = "no-repeat";
        votes.push(cell.id);
    }

    function undrawVotes(cell){
        cell.removeAttribute("style");
    }


    socket.on('update_votes', function(votes){
        console.log("updating votes"+votes);
        for (var cellCode in votes){
            var cell = document.getElementById(cellCode);
            console.log(cell);
            console.log(votes);
            console.log(votes[cellCode]);
            drawVotes(cell, votes[cellCode]);
        }
    });

    socket.on('vote_done', function(data){
        console.log(data);
        votes.forEach(function(cell_id, index, array) {
          undrawVotes(document.getElementById(cell_id));
        });
        console.log(data);
        target = document.getElementById(data.cell);
        target.dataset.enabled = "false";
        target.dataset.votedfor = "true";
        target.dataset.code = parseInt(data.value);
    });

    var players = document.getElementById("players").children,
        nplayers = players.length;

    socket.on('change_current_player', function(players_id){
        console.log('Switching '+players_id);
        for (var i=0; i<nplayers; i++){
            var player = players[i];
            if (players_id.indexOf(player.id) == -1){
                player.classList.remove('current-player');
            }
            else{
                player.classList.add('current-player');
            }
        }
    });

    var title = document.getElementById('toptitle');
    socket.on('change_title', function(new_title){
        title.innerHTML = new_title.title;
        title.style.color = new_title.color;
    });

    /* On Game End */
    var control_panel = document.getElementById('control_panel');
    socket.on('change_controls', function(html){
        console.log('html');
        control_panel.innerHTML = html;
    });
}

function initChat(){
    console.log("Initiating chat")

    function sendMsg(){
        var m = document.getElementById("m");
        var txt = m.value;
        console.log("Sending "+ txt);
        socket.emit("chat_message", txt);
        m.value = "";
    }

    var form = document.getElementById("msgform");
    form.addEventListener("submit", function(e){
        console.log(e);
        e.preventDefault();
        sendMsg();
    });

    var messages = document.getElementById("messages");
    socket.on("chat_msg", function(msg){
        console.log("received : "+msg);
        var li = document.createElement("li");
        li.textContent = msg;
        messages.append(li);
        messages.scrollTo(0, messages.scrollHeight);
    });

    console.log('Initiating events chat');

    var event_chat = document.getElementById("events_msglist");

    socket.on('add_event', function(msg){
        console.log('Adding event');
        var li = document.createElement("li");
        li.textContent = msg;
        event_chat.append(li);
        event_chat.scrollTo(0, event_chat.scrollHeight);
    });
}