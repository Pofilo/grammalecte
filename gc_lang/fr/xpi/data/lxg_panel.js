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
    addSeparator(sText);
});

self.port.on("addParagraphElems", function (sJSON) {
    addParagraphElems(sJSON);
});

self.port.on("addMessage", function (sClass, sText) {
    addMessage(sClass, sText);
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


/*
    Actions
*/

function addSeparator (sText) {
    if (document.getElementById("wordlist").textContent !== "") {
        let xElem = document.createElement("p");
        xElem.className = "separator";
        xElem.textContent = sText;
        document.getElementById("wordlist").appendChild(xElem);
    }
}

function addMessage (sClass, sText) {
    let xNode = document.createElement("p");
    xNode.className = sClass;
    xNode.textContent = sText;
    document.getElementById("wordlist").appendChild(xNode);
}

function addParagraphElems (sJSON) {
    try {
        let xNodeDiv = document.createElement("div");
        xNodeDiv.className = "paragraph";
        let lElem = JSON.parse(sJSON);
        for (let oToken of lElem) {
            xNodeDiv.appendChild(createTokenNode(oToken));
        }
        document.getElementById("wordlist").appendChild(xNodeDiv);
    }
    catch (e) {
        console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
        console.error(sJSON);
    }
}

function createTokenNode (oToken) {
    let xTokenNode = document.createElement("div");
    xTokenNode.className = "token " + oToken.sType;
    let xTokenValue = document.createElement("b");
    xTokenValue.className = oToken.sType;
    xTokenValue.textContent = oToken.sValue;
    xTokenNode.appendChild(xTokenValue);
    let xSep = document.createElement("s");
    xSep.textContent = " : ";
    xTokenNode.appendChild(xSep);
    if (oToken.aLabel.length === 1) {
        xTokenNode.appendChild(document.createTextNode(oToken.aLabel[0]));
    } else {
        let xTokenList = document.createElement("ul");
        for (let sLabel of oToken.aLabel) {
            let xTokenLine = document.createElement("li");
            xTokenLine.textContent = sLabel;
            xTokenList.appendChild(xTokenLine);
        }
        xTokenNode.appendChild(xTokenList);
    }
    return xTokenNode;
}


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
