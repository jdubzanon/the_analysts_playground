

// CLEAR SEARCH BAR WHEN PAGE IS DISPLAYED (BACK BUTTON OPERATIONS)
// remove any prior searches
// if statement for hx-push-url and variable defined errors
if (typeof globalThis.tickerInputBox === "undefined") {
    const tickerInputBox = document.getElementById("ticker-input-box");
    window.addEventListener('pageshow', function (event) {
        tickerInputBox.value = ""
    });
}
