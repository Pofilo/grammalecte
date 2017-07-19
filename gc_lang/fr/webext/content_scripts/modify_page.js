
function do_something (request, sender, sendResponse) {
  //removeEverything();
  change(request.myparam);
  console.log("DONE!!");
  browser.runtime.onMessage.removeListener(do_something);
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
browser.runtime.onMessage.addListener(do_something);
