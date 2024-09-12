
document.body.addEventListener('htmx:beforeOnLoad', function (event) {
    if (event.detail.xhr.status === 200) {
        document.getElementById('index-swap').innerHTML = event.detail.xhr.responseText;
        document.getElementById('error-div').innerHTML = '';
    } else {
        document.getElementById('error-div').innerHTML = event.detail.xhr.responseText || 'An error occurred';
        setTimeout(function () {
            document.getElementById('error-div').innerHTML = ""
        }, 2000)
        htmx.process(document.body);

    }
});




function scrollToTop() {
    document.querySelector('.swap-div').scrollTop = 0;

}
document.body.addEventListener('htmx:afterSwap', function (event) {
    if (event.detail.successful) {
        scrollToTop()
    }
})
