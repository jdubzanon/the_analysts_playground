"use strict"

const currencyTopHandler = document.querySelectorAll(".topHandler")
if (currencyTopHandler.length > 0) {
    currencyTopHandler.forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            })
        })
    })
}



document.body.addEventListener("htmx:afterSettle", function (ev) {
    const currencyTopHandler = document.querySelectorAll(".topHandler")
    if (currencyTopHandler.length > 0) {
        currencyTopHandler.forEach(link => {
            link.addEventListener("click", function (event) {
                event.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                })
            })
        })
    }
})


function scrollToTop() {
    document.querySelector('.matching-div').scrollTop = 0;

}
