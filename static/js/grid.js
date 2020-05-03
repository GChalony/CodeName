function selectCell(event){
console.log(event);
    event.target.dataset.selected = "true";
}

function askCellValue(event){
    console.log(event);
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

}

var cells = document.getElementsByTagName("td"),
    ncells = cells.length;

for (var i=0; i<ncells; i++){
    var cell = cells[i];
    cell.addEventListener("click", askCellValue);
}
