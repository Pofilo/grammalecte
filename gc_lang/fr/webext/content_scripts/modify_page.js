import { echo } from "../mymodule";

echo("CONTENT SCRIPRT!!!");

function handleMessage2 (oRequest, xSender, sendResponse) {
  console.log(`[Content script] received: ${oRequest.content}`);
  change(request.myparam);
  //browser.runtime.onMessage.removeListener(handleMessage);
  sendResponse({response: "response from content script"});
}

function removeEverything () {
  while (document.body.firstChild) {
    document.body.firstChild.remove();
  }
}

function change (param) {
  document.getElementById("title").setAttribute("background-color", "#809060");
  console.log("param: " + param);
  document.getElementById("title").setAttribute("background-color", "#FF0000");
}


/*
  Assign do_something() as a listener for messages from the extension.
*/
browser.runtime.onMessage.addListener(handleMessage2);