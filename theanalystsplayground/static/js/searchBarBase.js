

// MUTANT OBSERVER TO CONTROL THE POPUP FOR AUTO SEARCH

const targetNode = document.getElementById("htmx-result");
targetNode.style.display = "none"

const config = { childList: true, subtree: true };

const callback = (mutationList, observer) => {
    for (const mutation of mutationList) {
        if (mutation.type === "childList") {
            if (targetNode.childNodes.length > 0) {
                targetNode.style.display = "block"
                const closeLink = document.querySelector(".close-link")
                closeLink.addEventListener("click", function (ev) {
                    ev.preventDefault()
                    targetNode.style.display = "none"
                })
            } else {
                targetNode.style.display = "none"
            }
        };
    };
};

const observer = new MutationObserver(callback)
observer.observe(targetNode, config)


// CLEAR SEARCH BAR WHEN PAGE IS DISPLAYED (BACK BUTTON OPERATIONS)
// Select the search input element
var searchInput = document.getElementById('bar-for-search');
var autoMatchSearchBox = document.getElementById("htmx-result")
// Add event listener for pageshow event
window.addEventListener('pageshow', function (event) {
    // Clear the content of the search input
    searchInput.value = '';
    autoMatchSearchBox.innerHTML = ""

});

// close htmx window
const closeHtmxWindow = () => {
    targetNode.style.display = "none"
}
