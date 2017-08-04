// Background 

"use strict";

let xGCEWorker = new Worker("gce_worker.js");

xGCEWorker.postMessage(["init", browser.extension.getURL(".")]);

function handleMessage (oRequest, xSender, sendResponse) {
  console.log(`[background] received: ${oRequest.content}`);
  sendResponse({response: "response from background script"});
}

browser.runtime.onMessage.addListener(handleMessage);
