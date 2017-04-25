// JavaScript

let bExpanded = true;

// events

document.getElementById('close').addEventListener("click", function (event) {
    bExpanded = true; // size is reset in ui.js
    self.port.emit('closePanel');
});

document.getElementById('expand_reduce').addEventListener("click", function (event) {
    if (bExpanded) {
        self.port.emit("resize", "reduce", 10); // the number has no meaning here
        bExpanded = false;
    } else {
        self.port.emit("resize", "expand", 10); // the number has no meaning here
        bExpanded = true;
    }
});

/*
// Conjugueur
document.getElementById('conjugueur').addEventListener("click", function (event) {
    self.port.emit('openConjugueur');
});
*/

self.port.on("addSeparator", function (sText) {
    if (document.getElementById("wordlist").innerHTML !== "") {
        let xElem = document.createElement("p");
        xElem.className = "separator";
        xElem.innerHTML = sText;
        document.getElementById("wordlist").appendChild(xElem);
    }
});

self.port.on("addElem", function (sHtml) {
    let xElem = document.createElement("div");
    xElem.innerHTML = sHtml;
    document.getElementById("wordlist").appendChild(xElem);
});

self.port.on("clear", function (sHtml) {
    document.getElementById("wordlist").textContent = "";
});

self.port.on("startWaitIcon", function() {
    document.getElementById("waiticon").hidden = false;
});

self.port.on("stopWaitIcon", function() {
    document.getElementById("waiticon").hidden = true;
});


window.addEventListener(
    "click",
    function (xEvent) {
        let xElem = xEvent.target;
        if (xElem.id) {
            if (xElem.id.startsWith("resize")) {
                self.port.emit("resize", xElem.id, 10);
            }
        }
    },
    false
);


// display selection

function displayClasses () {
    setHidden("ok", document.getElementById("ok").checked);
    setHidden("mbok", document.getElementById("mbok").checked);
    setHidden("nb", document.getElementById("nb").checked);
    setHidden("unknown", document.getElementById("unknown").checked);
}

function setHidden (sClass, bHidden) {
    for (let i = 0; i < document.getElementsByClassName(sClass).length; i++) {
        document.getElementsByClassName(sClass)[i].hidden = bHidden;
    }
}
