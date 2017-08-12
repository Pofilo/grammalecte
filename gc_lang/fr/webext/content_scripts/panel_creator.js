// JavaScript
// Panel creator

"use strict";


function createPanelFrame (sId, sTitle, nWidth, nHeight) {
    try {
        let xPanel = document.createElement("div");
        xPanel.style = "position: fixed; left: 50%; top: 50%; z-index: 100; border-radius: 10px;"
                     + "color: hsl(210, 10%, 4%); background-color: hsl(210, 20%, 90%); border: 10px solid hsla(210, 20%, 70%, .5);"
                     + 'font-family: "Trebuchet MS", "Liberation Sans", sans-serif;'
                     + getPanelSize(nWidth, nHeight);
        let xBar = document.createElement("div");
        xBar.style = "position: fixed; width: "+nWidth+"px ; background-color: hsl(210, 0%, 100%); border-bottom: 1px solid hsl(210, 10%, 50%); font-size: 20px;";
        xBar.appendChild(createCloseButton(xPanel));
        let xTitle = createDiv(sId+"_title", "", "", "padding: 10px 20px;");
        xTitle.appendChild(createLogo());
        xTitle.appendChild(createDiv(sId+"_label", "Grammalecte · " + sTitle, "", "display: inline-block; padding: 0 10px;"));
        xBar.appendChild(xTitle);
        xPanel.appendChild(xBar);
        xPanel.appendChild(createDiv(sId+"_empty_space", "", "", "height: 50px;")); // empty space to fill behind the title bar
        xPanel.appendChild(createDiv(sId+"_content", "", "", "overflow: auto;"));
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

function createLogo () {
    let xImg = document.createElement("img");
    xImg.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAC8UlEQVQ4jX3TbUgTcRwH8P89ddu5u9tt082aZmpFEU4tFz0QGTUwCi0heniR9MSUIKRaD0RvIlKigsooo+iNFa0XJYuwIjEK19OcDtPElsG0ktyp591t7u7+vUh7MPX3+vf5/n8/+P0BmKJIPUUVlh2rdVVeesWlzEybqg+bFOsoylnqPmNavGFfknV2Omu2Lvja3vxAURKJib3opHizu8riLK6gjRyuKgmoSoMRFENRUqfXTzvBGK62LC2uoFkOl4RhjQ8+qWt7dPNE3sbdp+2LXbsGe9qb4rIo/BfwFy6nWQ4ThWGNDzbcfu29dMDh2nHU7CypYNLmzTda0/L5cNuzmDQi/A4Y27k6eQxLI79wS/11D0AAMNvs6XT6ojVJjJEgTbMy2BT77xBMp09KcpaWV1uc41jQoi0NdUHfjeOO9WWn7AVF7s7n986SithPJGeupBh2PCSP/xxqxAp3eq6wuUV7Wc6MSZIEhA8vHjbfOe/OcW3zmAuKy+nUzAyD2bow8ODaEROFq8AyZ5WBYdEZXGqGxZ61HJV+9HYCJRbTNA0QBA40HWunaKN5dKg/DBKxeCIe09Th/m4MJwiMSZmLEzMQAABQRuNqgu8NYX3doTcMpvCkLbtQZ2AJkrPOZG1zlnY13T+Hy9EehY90h57eqcorcZ/lctZuMzAsOjLEqwNv66/6vZcPYRBC+C3cGaBxhSet2av1BpYgTTY7k5y2JPT41slIR6Axv8R9nnOs+4Pf+2r992uOxGVJwgAAAEINfgt3BGgsESWtWas1iGDyl+CT/u7WpvxNFRc4x7qtBoZFhSFejb7z1fq9NYfjsiT+cwcQavBruCOgU4SIGo18amuoq3Js3FNlynVtH385+s53ze+t8cRkURx3yMTTRBAEQVAUXbFlf3XystJKA2NExeFBdWASDAAA+MQACCEEmqbJ0b6PMC7JwhDU8YFHV5u9NZ64LErT/oW/63tPV6uJwmKoOND78u7Fg5NhAAD4CVbzY9cwrWQrAAAAAElFTkSuQmCC";
    return xImg;
}

function loadImage (sContainerClass, sImagePath) {
    let xRequest = new XMLHttpRequest();
    xRequest.open('GET', browser.extension.getURL("")+sImagePath, false);
    xRequest.responseType = "arraybuffer";
    xRequest.send();
    let blobTxt = new Blob([xRequest.response], {type: 'image/png'});
    let img = document.createElement('img');
    img.src = (URL || webkitURL).createObjectURL(blobTxt); // webkitURL is obsolete: https://bugs.webkit.org/show_bug.cgi?id=167518
    Array.filter(document.getElementsByClassName(sContainerClass), function (oElem) {
        oElem.appendChild(img);
    });
}
