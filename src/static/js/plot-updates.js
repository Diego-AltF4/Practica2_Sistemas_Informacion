
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

function updateServiciosMas() {
    var rango = document.getElementById("updateServicios").value;
    if (!rango) {
        rango = 3;
    }
    var request = "/servicios/" + rango + "?valorServicio=1";
    servicio = false;
    fetch(request)
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
        })
        .then(function (data) {
            var table = new Tabulator("#services-table", {
                data:data,
                autoColumns:true,
                resizableColumnFit:true,
                layout:"fitDataStretch"
            });
        })
        .catch(function (error) {
            console.error(error);
        });

}

function updateServiciosMenos() {
    var rango = document.getElementById("updateServicios").value;
    if (!rango) {
        rango = 3;
    }
    var request = "/servicios/" + rango + "?valorServicio=0";
    servicio = true;

    fetch(request)
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
        })
        .then(function (data) {
            var table = new Tabulator("#services-table", {
                data:data,
                autoColumns:true,
                resizableColumnFit:true,
                layout:"fitDataStretch"
            });
        })
        .catch(function (error) {
            console.error(error);
        });

}

function cveDisplay() {
    fetch("/cves")
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
        })
        .then(function (data) {
            var table = new Tabulator("#cve-table", {
                data:data,
                autoColumns:true,
                resizableColumnFit:true,
                layout:"fitDataStretch"
            });
        })
        .catch(function (error) {
            console.error(error);
        });
}