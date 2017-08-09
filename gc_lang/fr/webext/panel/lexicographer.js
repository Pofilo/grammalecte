// JavaScript



/*
    Actions
*/

function startWaitIcon () {
	document.getElementById("waiticon").hidden = false;
}

function stopWaitIcon () {
	document.getElementById("waiticon").hidden = true;
}

function clearList () {
	document.getElementById("tokens_list").textContent = "";
}

function addSeparator (sText) {
    if (document.getElementById("tokens_list").textContent !== "") {
        let xElem = document.createElement("p");
        xElem.className = "separator";
        xElem.textContent = sText;
        document.getElementById("tokens_list").appendChild(xElem);
    }
}

function addMessage (sClass, sText) {
    let xNode = document.createElement("p");
    xNode.className = sClass;
    xNode.textContent = sText;
    document.getElementById("tokens_list").appendChild(xNode);
}

function addParagraphElems (sJSON) {
    try {
        let xNodeDiv = document.createElement("div");
        xNodeDiv.className = "paragraph";
        let lElem = JSON.parse(sJSON);
        for (let oToken of lElem) {
            xNodeDiv.appendChild(createTokenNode(oToken));
        }
        document.getElementById("tokens_list").appendChild(xNodeDiv);
    }
    catch (e) {
        console.error(e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
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
