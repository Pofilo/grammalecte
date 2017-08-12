// JavaScript
// Panel creator

"use strict";


function createPanelFrame (sId, sTitle, nWidth, nHeight) {
    try {
        let xPanel = document.createElement("div");
        xPanel.style = "position: fixed; left: 50%; top: 50%; z-index: 100; border-radius: 10px;"
                     + "color: hsl(210, 10%, 4%); background-color: hsl(210, 20%, 90%); border: 10px solid hsla(210, 20%, 70%, .5); overflow: auto;"
                     + getPanelSize(nWidth, nHeight);
        let xBar = document.createElement("div");
        xBar.style = "position: fixed; width: "+nWidth+"px ; background-color: hsl(210, 0%, 100%); border-bottom: 1px solid hsl(210, 10%, 50%); font-size: 20px;";
        xBar.appendChild(createCloseButton(xPanel));
        xBar.appendChild(createDiv(sId+"_title", "Grammalecte · " + sTitle));
        xPanel.appendChild(xBar);
        xPanel.appendChild(createDiv(sId+"_empty_space", "", "", "height: 40px;")); // empty space to fill behind the title bar
        return xPanel;
    }
    catch (e) {
        showError(e);
    }
}

function getPanelSize (nWidth, nHeight) {
    let s = "width: "+ nWidth.toString() + "px; height: " + nHeight.toString() + "px;";
    s += "margin-top: -" + (nHeight/2).toString() + "px; margin-left: -" + (nWidth/2).toString() + "px;";
    return s;
}

function createCloseButton (xParentNode) {
    let xButton = document.createElement("div");
    xButton.style = "float: right; padding: 2px 10px; color: hsl(210, 0%, 100%); text-align: center;"
                  + "font-size: 22px; font-weight: bold; background-color: hsl(0, 80%, 50%); border-radius: 0 0 0 3px; cursor: pointer;";
    xButton.textContent = "×";
    xButton.onclick = function () {
        xParentNode.style.display = "none";
    }
    return xButton;
}


/*
    Common functions
*/
function createDiv (sId, sContent, sClass="", sStyle="") {
    let xDiv = document.createElement("div");
    xDiv.id = sId;
    xDiv.className = sClass;
    xDiv.style = sStyle;
    xDiv.textContent = sContent;
    return xDiv;
}

function createCheckbox (sId, bDefault, sClass="")  {
    let xInput = document.createElement("input");
    xInput.type = "checkbox";
    xInput.id = sId;
    xInput.className = sClass;
    xInput.dataset.default = bDefault;
    return xInput;
}

function createLabel (sForId, sLabel, sClass="") {
    let xLabel = document.createElement("label");
    xLabel.setAttribute("for", sForId);
    xLabel.textContent = sLabel;
    return xLabel;
}

function loadImage (sContainerClass, sImagePath) {
    let xRequest = new XMLHttpRequest();
    xRequest.open('GET', browser.extension.getURL("")+sImagePath, false);
    xRequest.responseType = "arraybuffer";
    xRequest.send();
    let blobTxt = new Blob([xRequest.response], {type: 'image/png'});
    let img = document.createElement('img');
    img.src = (URL || webkitURL).createObjectURL(blobTxt);
    Array.filter(document.getElementsByClassName(sContainerClass), function (oElem) {
        oElem.appendChild(img);
    });
}
