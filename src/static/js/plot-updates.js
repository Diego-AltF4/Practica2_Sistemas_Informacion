
function updateDir() {
    var nDirecciones = document.getElementById("direcciones").value;
    if (nDirecciones === undefined) {
        nDirecciones = 10;
    }
    var request = "/direcciones?direcciones=" + nDirecciones
    Plotly.d3.json(request, function(error, data) {
        if (error) console.log(error);
        Plotly.react('graphDir', data, {}, {displayModeBar: false});
    });
    document.getElementById("displayDir").innerHTML = "Top " + nDirecciones + " direcciones";


}

function updateDev() {
    var nDispositivos = document.getElementById("dispositivos").value;
    if (nDispositivos === undefined) {
        nDispositivos = 10;
    }
    var request = "/dispositivos?dispositivos=" + nDispositivos
    Plotly.d3.json(request, function(error, data) {
        if (error) console.log(error);
        Plotly.react('graphDev', data, {}, {displayModeBar: false});
    });
    document.getElementById("displayDispositivos").innerHTML = "Top " + nDispositivos + " dispositivos";


}