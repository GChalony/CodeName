var socket = io("/grid");

function drawVotes(cell, n){
    cell.style.background = '#'+n+''+n+''+n;
}

function selectCell(event){
    console.log(event);
    event.target.dataset.selected = "true";
}

function voteCell(event){
    console.log(event);
<<<<<<< HEAD
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/cell?code=" + event.target.id);
    xhr.send(null);

    var target = event.target;

    xhr.addEventListener("readystatechange", function(e){
        console.log(e);
        console.log(xhr);
        target.dataset.selected = "true";
        target.dataset.code = xhr.response;
    });

=======
    socket.emit('vote_cell', event.target.id);
>>>>>>> bd28feee76e39b5e154a7c89116e6b11ce44e38f
}


var cells = document.getElementsByTagName("td"),
    ncells = cells.length;

for (var i=0; i<ncells; i++){
    var cell = cells[i];
<<<<<<< HEAD
    cell.addEventListener("click", askCellValue);
=======
    cell.addEventListener('click', voteCell);
>>>>>>> bd28feee76e39b5e154a7c89116e6b11ce44e38f
}

socket.on('update_votes', function(votes){
    for (var cellCode in votes){
        var cell = getElementsById(cellCode);
        drawVotes(cell, votes[cell]);
    }
});

socket.on('vote_done', function(data){
    console.log(data);
    target = document.getElementById(data.cell);
    target.dataset.selected = "true";
    target.dataset.code = parseInt(data.value);
});

socket.on('switch_teams', function(data){
    console.log(data);

});