


const targetWatch = document.getElementById("included-result-main-div");

var autoScroll = function autoScrollDown() {
    window.scrollBy(0, 400); // You can adjust the second parameter to control the speed of the scroll

}
if (targetWatch.childNodes.length > 1) { // Check if target element has child nodes
    autoScroll()
    var scrollInterval = setInterval(autoScroll, 400);
    setTimeout(function () {
        clearInterval(scrollInterval); // Stop auto-scrolling after 5 seconds
    }, 10);
}

// const topHandler = document.querySelectorAll(".topHandler")

// if (topHandler.length > 0) {
//     topHandler.forEach(link => {
//         link.addEventListener("click", function (event) {
//             event.preventDefault();
//             window.scrollTo({
//                 top: 0,
//                 behavior: "smooth"
//             })
//         })
//     })
// }

// function scrollToTop() {
//     document.getElementById("included-result-main-div").scrollTop = 0;

// }
