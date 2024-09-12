// TOP SEARCH BAR OF HOMEPAGE
if (typeof globalThis.targetNode === "undefined") {

    const targetNode = document.getElementById("htmx-general");
    const config = { childList: true, subtree: true }

    const callback = (mutationList, observer) => {
        for (const mutation of mutationList) {
            if (mutation.type === "childList") {
                if (targetNode.childNodes.length > 0) {
                    targetNode.style.display = "block";
                    const closeLink = document.querySelector(".close-link")
                    closeLink.addEventListener("click", function () {
                        targetNode.style.display = "none"
                    })
                } else {
                    targetNode.style.display = "none";
                };
            };
        };
    };

    const observer = new MutationObserver(callback);
    observer.observe(targetNode, config);
}



if (typeof globalThis.searchInput === "undefined" && typeof globalThis.autoMatchSearchBox == "undefined") {

    // WATCHING THE WINDOW FOR PAGE DISPLAY (BACK BUTTON OPERATIONS)
    const searchInput = document.getElementById("bar-for-search");
    const autoMatchSearchBox = document.getElementById("htmx-general");

    const searchInputMiddlePage = document.getElementById("bar-for-search-center");
    const autoMatchSearchBoxMiddle = document.getElementById("htmx-search-middle-result");

    window.addEventListener("pageshow", function (event) {
        searchInput.value = "";
        autoMatchSearchBox.innerHTML = "";

    })
}

if (typeof globalThis.autoMatchSearchBox == "undefined") {
    const autoMatchSearchBox = document.getElementById("htmx-general");
    autoMatchSearchBox.addEventListener("htmx:afterSettle", function () {
        const closeLink = document.querySelector(".close-link")
        if (closeLink) {
            closeLink.addEventListener("click", function (evt) {
                evt.preventDefault()
                const searchInput = document.getElementById("bar-for-search");
                searchInput.value = ""
            })
        }
    })
}
