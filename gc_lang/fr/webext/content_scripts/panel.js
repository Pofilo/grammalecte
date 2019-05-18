// JavaScript
// Panel creator

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global GrammalectePanel, oGrammalecte, xGrammalectePort, showError, window, document, console */

"use strict";


class GrammalectePanel {

    constructor (sId, sTitle, nWidth, nHeight, bFlexible=true) {
        this.sId = sId;
        this.nWidth = nWidth;
        this.nHeight = nHeight;
        this.bFlexible = bFlexible;
        this.bHorizStrech = false;
        this.bVertStrech = false;
        this.nPositionX = 2;
        this.nPositionY = 2;
        this.bWorking = false;

        this.bShadow = document.body.createShadowRoot || document.body.attachShadow;
        if (this.bShadow) {
            this.xShadowPanel = oGrammalecte.createNode("div", {id: this.sId+"_shadow", style: "width:0;height:0;"});
            this.xShadow = this.xShadowPanel.attachShadow({mode: "open"});
            this.xParent = this.xShadow;
        } else {
            this.xParent = document;
        }

        this.xPanelBar = oGrammalecte.createNode("div", {className: "grammalecte_panel_bar"});
        this.xPanelContent = oGrammalecte.createNode("div", {className: "grammalecte_panel_content"});
        this.xWaitIcon = this._createWaitIcon();
        this.xCloseButton = null;
        this.xPanel = this._createPanel(sTitle);
        this.center();
    }

    _createPanel (sTitle) {
        try {
            let xPanel = oGrammalecte.createNode("div", {id: this.sId, className: "grammalecte_panel"});
            this.xPanelBar.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_panel_invisible_marker", textContent: "__grammalecte_panel__"}));
            this.xPanelBar.appendChild(this._createButtons());
            let xTitle = oGrammalecte.createNode("div", {className: "grammalecte_panel_title"});
            xTitle.appendChild(this._createLogo());
            xTitle.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_panel_label", textContent: sTitle}));
            this.xPanelBar.appendChild(xTitle);
            xPanel.appendChild(this.xPanelBar);
            this._createMesssageBlock();
            xPanel.appendChild(this.xPanelMessageBlock);
            xPanel.appendChild(this.xPanelContent);
            return xPanel;
        }
        catch (e) {
            showError(e);
        }
    }

    _createLogo () {
        let xImg = document.createElement("img");
        xImg.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAC8UlEQVQ4jX3TbUgTcRwH8P89ddu5u9tt082aZmpFEU4tFz0QGTUwCi0heniR9MSUIKRaD0RvIlKigsooo+iNFa0XJYuwIjEK19OcDtPElsG0ktyp591t7u7+vUh7MPX3+vf5/n8/+P0BmKJIPUUVlh2rdVVeesWlzEybqg+bFOsoylnqPmNavGFfknV2Omu2Lvja3vxAURKJib3opHizu8riLK6gjRyuKgmoSoMRFENRUqfXTzvBGK62LC2uoFkOl4RhjQ8+qWt7dPNE3sbdp+2LXbsGe9qb4rIo/BfwFy6nWQ4ThWGNDzbcfu29dMDh2nHU7CypYNLmzTda0/L5cNuzmDQi/A4Y27k6eQxLI79wS/11D0AAMNvs6XT6ojVJjJEgTbMy2BT77xBMp09KcpaWV1uc41jQoi0NdUHfjeOO9WWn7AVF7s7n986SithPJGeupBh2PCSP/xxqxAp3eq6wuUV7Wc6MSZIEhA8vHjbfOe/OcW3zmAuKy+nUzAyD2bow8ODaEROFq8AyZ5WBYdEZXGqGxZ61HJV+9HYCJRbTNA0QBA40HWunaKN5dKg/DBKxeCIe09Th/m4MJwiMSZmLEzMQAABQRuNqgu8NYX3doTcMpvCkLbtQZ2AJkrPOZG1zlnY13T+Hy9EehY90h57eqcorcZ/lctZuMzAsOjLEqwNv66/6vZcPYRBC+C3cGaBxhSet2av1BpYgTTY7k5y2JPT41slIR6Axv8R9nnOs+4Pf+2r992uOxGVJwgAAAEINfgt3BGgsESWtWas1iGDyl+CT/u7WpvxNFRc4x7qtBoZFhSFejb7z1fq9NYfjsiT+cwcQavBruCOgU4SIGo18amuoq3Js3FNlynVtH385+s53ze+t8cRkURx3yMTTRBAEQVAUXbFlf3XystJKA2NExeFBdWASDAAA+MQACCEEmqbJ0b6PMC7JwhDU8YFHV5u9NZ64LErT/oW/63tPV6uJwmKoOND78u7Fg5NhAAD4CVbzY9cwrWQrAAAAAElFTkSuQmCC";
        return xImg;
    }

    _createButtons () {
        let xButtonLine = oGrammalecte.createNode("div", {className: "grammalecte_panel_commands"});
        xButtonLine.appendChild(this.xWaitIcon);
        if (this.sId === "grammalecte_gc_panel") {
            xButtonLine.appendChild(this._createCopyButton());
        }
        if (this.bFlexible) {
            xButtonLine.appendChild(this._createMoveButton("changeWidth", "⭾", "Bascule la largeur"));
            xButtonLine.appendChild(this._createMoveButton("changeHeight", "⭿", "Bascule la hauteur"));
        }
        xButtonLine.appendChild(this._createMoveButton("up", " ", "Monter")); // use char ⏶ when Windows 10 be vast majority of OS (Trebuchet MS not updated on other OS)
        xButtonLine.appendChild(this._createMoveButton("left", " ", "À gauche")); // use char ⏴ when Windows 10 be vast majority of OS (Trebuchet MS not updated on other OS)
        xButtonLine.appendChild(this._createMoveButton("center", "•", "Centrer"));
        xButtonLine.appendChild(this._createMoveButton("right", " ", "À droite")); // use char ⏵ when Windows 10 be vast majority of OS (Trebuchet MS not updated on other OS)
        xButtonLine.appendChild(this._createMoveButton("down", " ", "Descendre")); // use char ⏷ when Windows 10 be vast majority of OS (Trebuchet MS not updated on other OS)
        this.xCloseButton = this._createCloseButton();
        xButtonLine.appendChild(this.xCloseButton);
        return xButtonLine;
    }

    _createWaitIcon () {
        let xWaitIcon = oGrammalecte.createNode("div", {className: "grammalecte_spinner"});
        return xWaitIcon;
    }

    _createCopyButton () {
        let xButton = oGrammalecte.createNode("div", {id: "grammalecte_clipboard_button", className: "grammalecte_panel_button grammalecte_copy_button", textContent: "📋", title: "Copier le contenu de l’éditeur dans le presse-papiers"});
        xButton.onclick = () => { this.copyTextToClipboard(); };
        return xButton;
    }

    _createMoveButton (sAction, sLabel, sTitle) {
        let xButton = oGrammalecte.createNode("div", {className: "grammalecte_panel_button grammalecte_move_button grammalecte_move_button_"+sAction, textContent: sLabel, title: sTitle});
        xButton.onclick = () => { this[sAction](); };
        return xButton;
    }

    _createCloseButton () {
        let xButton = oGrammalecte.createNode("div", {className: "grammalecte_panel_button grammalecte_close_button", textContent: "×", title: "Fermer la fenêtre"});
        xButton.onclick = () => { this.hide(); };
        return xButton;
    }

    _createMesssageBlock () {
        this.xPanelMessageBlock = oGrammalecte.createNode("div", {id: "grammalecte_panel_message_block"});
        let xPanelMessageCloseButton = oGrammalecte.createNode("div", {id: "grammalecte_panel_message_close_button", textContent: "×"});
        xPanelMessageCloseButton.onclick = () => { this.hideMessage() };
        this.xPanelMessageBlock.appendChild(xPanelMessageCloseButton);
        this.xPanelMessage = oGrammalecte.createNode("div", {id: "grammalecte_panel_message"});
        this.xPanelMessageBlock.appendChild(this.xPanelMessage);
    }

    insertIntoPage () {
        if (this.bShadow) {
            oGrammalecte.createStyle("content_scripts/panel.css", null, this.xShadow);
            oGrammalecte.createStyle("content_scripts/panel_gc.css", null, this.xShadow);
            oGrammalecte.createStyle("content_scripts/panel_lxg.css", null, this.xShadow);
            oGrammalecte.createStyle("content_scripts/panel_conj.css", null, this.xShadow);
            oGrammalecte.createStyle("content_scripts/panel_tf.css", null, this.xShadow);
            this.xShadow.appendChild(this.xPanel);
            document.body.appendChild(this.xShadowPanel);
        } else {
            if (!document.getElementById("grammalecte_csspanel")) {
                oGrammalecte.createStyle("content_scripts/panel.css", "grammalecte_csspanel", document.head);
                oGrammalecte.createStyle("content_scripts/panel_gc.css", null, document.head);
                oGrammalecte.createStyle("content_scripts/panel_lxg.css", null, document.head);
                oGrammalecte.createStyle("content_scripts/panel_conj.css", null, document.head);
                oGrammalecte.createStyle("content_scripts/panel_tf.css", null, document.head);
            }
            document.body.appendChild(this.xPanel);
        }
    }

    show () {
        this.xPanel.style.display = "flex";
    }

    hide () {
        this.xPanel.style.display = "none";
    }

    center () {
        this.nPosition = 5;
        this.setSizeAndPosition();
    }

    left () {
        if (![1, 4, 7].includes(this.nPosition)) { this.nPosition -= 1 };
        this.setSizeAndPosition();
    }

    right () {
        if (![3, 6, 9].includes(this.nPosition)) { this.nPosition += 1 };
        this.setSizeAndPosition();
    }

    up () {
        if (![7, 8, 9].includes(this.nPosition)) { this.nPosition += 3 };
        this.setSizeAndPosition();
    }

    down () {
        if (![1, 2, 3].includes(this.nPosition)) { this.nPosition -= 3 };
        this.setSizeAndPosition();
    }

    changeWidth () {
        this.bHorizStrech = !this.bHorizStrech;
        this.setSizeAndPosition();
    }

    changeHeight () {
        this.bVertStrech = !this.bVertStrech;
        this.setSizeAndPosition();
    }

    setSizeAndPosition () {
        // size
        let nWidth = (this.bFlexible && this.bHorizStrech) ? Math.min(this.nWidth*1.5, window.innerWidth-200) : Math.min(this.nWidth, window.innerWidth-200);
        let nHeight = this.nHeight;
        if ([4, 5, 6].includes(this.nPosition)) {
            nHeight = (this.bFlexible && this.bVertStrech) ? (window.innerHeight-100) : Math.min(window.innerHeight-100, this.nHeight);
        } else {
            nHeight = (this.bFlexible) ? Math.floor(window.innerHeight*0.45) : this.nHeight;
        }
        this.xPanel.style.width = `${nWidth}px`;
        this.xPanel.style.height = `${nHeight}px`;
        // position
        let oPos = null;
        switch (this.nPosition) {
            case 1: oPos = { top:"",     right:"",     bottom:"-2px", left:"-2px", marginTop:"",                marginLeft:"" }; break;
            case 2: oPos = { top:"",     right:"",     bottom:"-2px", left:"50%",  marginTop:"",                marginLeft:`-${nWidth/2}px` }; break;
            case 3: oPos = { top:"",     right:"-2px", bottom:"-2px", left:"",     marginTop:"",                marginLeft:"" }; break;
            case 4: oPos = { top:"50%",  right:"",     bottom:"",     left:"-2px", marginTop:`-${nHeight/2}px`, marginLeft:"" }; break;
            case 5: oPos = { top:"50%",  right:"",     bottom:"",     left:"50%",  marginTop:`-${nHeight/2}px`, marginLeft:`-${nWidth/2}px` }; break;
            case 6: oPos = { top:"50%",  right:"-2px", bottom:"",     left:"",     marginTop:`-${nHeight/2}px`, marginLeft:"" }; break;
            case 7: oPos = { top:"-2px", right:"",     bottom:"",     left:"-2px", marginTop:"",                marginLeft:"" }; break;
            case 8: oPos = { top:"-2px", right:"",     bottom:"",     left:"50%",  marginTop:"",                marginLeft:`-${nWidth/2}px` }; break;
            case 9: oPos = { top:"-2px", right:"-2px", bottom:"",     left:"",     marginTop:"",                marginLeft:"" }; break;
        }
        // change
        this.xPanel.style.top = oPos.top;
        this.xPanel.style.right = oPos.right;
        this.xPanel.style.bottom = oPos.bottom;
        this.xPanel.style.left = oPos.left;
        this.xPanel.style.marginTop = oPos.marginTop;
        this.xPanel.style.marginLeft = oPos.marginLeft;
    }

    reduce () {
        // todo
    }

    getWidth () {
        return this.xPanelContent.offsetWidth;
    }

    logInnerHTML () {
        // for debugging
        console.log(this.xPanel.innerHTML);
    }

    startWaitIcon () {
        this.bWorking = true;
        this.xWaitIcon.style.visibility = "visible";
    }

    stopWaitIcon () {
        this.bWorking = false;
        this.xWaitIcon.style.visibility = "hidden";
    }

    showMessage (sMessage) {
        this.xPanelMessageBlock.style.display = "block";
        this.xPanelMessage.textContent = sMessage;
    }

    hideMessage () {
        this.xPanelMessageBlock.style.display = "none";
    }

    openURL (sURL) {
        xGrammalectePort.postMessage({
            sCommand: "openURL",
            dParam: {"sURL": sURL},
            dInfo: {}
        });
    }
}
