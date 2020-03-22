# API for the web

## Using the Grammalecte API for the web

**With Grammalecte 1.8+.** (beta stage)

If Grammalecte is installed by the user on his browser (like Firefox or Chrome), you can call
several methods for a better integration of grammar checking for your website. This is mostly usefull
if you use non-standard textareas.

You can:

- disable the Grammalecte button (spinning pearl),

- launch the Grammalecte panel with custom button (or when you think it’s necessary),

- get the modified text via events (instead of having the node content directly modified),

- get raw results (list of errors) of grammar checking and spell checking,

- get spelling suggestions for a wrong word.


### How it works

Usually, webpage scripts can’t call methods or functions of browser extensions.

The Grammalecte API is injected within your webpage, with methods launching events that Grammalecte is listening. When Grammalecte receives one of these events, it launches the requested tasks. Results may be sent via events on webpage nodes.

For information purpose only, here are the layers of code explaining why you can’t access directly to the grammar checker:

    ·> webpage script
    <> Grammalecte API (injected by the content-script, callable by the webpage script)
    <> Content-script (injected by the extension, not callable by the webpage script)
    <> Background script (extension core)
    <· Worker running the grammar checker on a different process


### Detecting if the Grammalecte API is here

Every call to the Grammalecte API will be done via an object called `oGrammalecteAPI`.

    if (typeof(oGrammalecteAPI) === "object"  &&  oGrammalecteAPI !== null) {
        ...
    }


### Version of the Grammalecte API

    oGrammalecteAPI.sVersion


### Disabling the Grammalecte button (the spinning pearl)

By default, Grammalecte inserts a button (a spinning pearl) on each textarea node and editable node (unless the user disabled it).
You can tell Grammalete not to create these buttons on your text areas with the property: `data-grammalecte_button="false"`.


### Open the Grammalecte panel for a node

If you have disabled the spinning button, you can launch the Grammalecte panel with your custom button.

    oGrammalecteAPI.openPanelForNode("node_id")
    oGrammalecteAPI.openPanelForNode(node)

The node can be a textarea, an editable node or an iframe.
If the node is an iframe, the content won’t be modified by Grammalecte.


### Prevent Grammalecte to modify the node content

If you don’t want Grammalecte to modify directly the node content, add the property: `data-grammalecte_result_via_event="true"`.

With this property, Grammalecte will send an event to the node each times the text is modified within the panel.
The text can be retrieved with:

    node.addEventListener("GrammalecteResult", function (event) {
        const detail = (typeof(event.detail) === 'string') && JSON.parse(event.detail);
        if (detail.sType  &&  detail.sType == "text") {
            let sText = detail.sText;
            ...
        }
    }


### Open the Grammalecte panel for any text

    oGrammalecteAPI.openPanelForText("your text")
    oGrammalecteAPI.openPanelForText("your text", "node_id")
    oGrammalecteAPI.openPanelForText("your text", node)

With the second parameter, Grammalecte will send an event to the node each times the text is modified within the panel.


### Parse a node and get errors

    oGrammalecteAPI.parseNode("node_id")
    oGrammalecteAPI.parseNode(node)

The node can be a textarea, an editable node or an iframe. The node must have an identifier.
Results (for each paragraph) will be sent in a succession of events at the node.

    node.addEventListener("GrammalecteResult", function (event) {
        const detail = (typeof(event.detail) === 'string') && JSON.parse(event.detail);
        if (detail.sType  &&  detail.sType == "proofreading") {
            let oResult = detail.oResult; // null when the text parsing is finished
            ...
        }
    }

For the last event, `oResult` will be `null`.


### Parse text and get errors

    oGrammalecteAPI.parseText(text, "node_id")
    oGrammalecteAPI.parseText(text, node)

The node must have an identifier.
Like with parseNode, results (for each paragraph) will be sent in a succession of events at the node.



### Get spelling suggestions

    oGrammalecteAPI.getSpellingSuggestions(word, destination, request_identifier)

Parameters:

- word (string)

- destination: node_id (string)

- request_identifier: a custom identifier (string) [default = ""]

Suggestions will be sent within an event at the node identified by `destination`.

    node.addEventListener("GrammalecteResult", function (event) {
        const detail = (typeof(event.detail) === 'string') && JSON.parse(event.detail);
        if (detail.sType  &&  detail.sType == "spellsugg") {
            let oResult = detail.oResult;
            let oInfo = detail.oInfo; // object containing the destination and the request_identifier
            ...
        }
    }
