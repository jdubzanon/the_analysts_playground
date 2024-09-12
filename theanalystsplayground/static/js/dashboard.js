"use strict";

const portfolioFormOpenClose = document.querySelector(".portfolio-form-link-class")
if (portfolioFormOpenClose) {
    portfolioFormOpenClose.addEventListener("click", function (evt) {
        evt.preventDefault()
    })
}

// input box itself
const entryForm = document.getElementById("entry-form");
entryForm.style.display = "none";

// link itself
const stockAddLink = document.getElementById("add-stock-link");

// done link
const doneLink = document.getElementById("done-link");
doneLink.style.display = "none";

// response target for htmx
const resultDiv = document.getElementById("responseTarget");

// FORMS
// watchlist form
const form = document.getElementById("add-stock-form");
// add portfolio form
const portfolioForm = document.getElementById("portfolio-form-id");



// where the response from form.event listener that is filled out
const addedPrompt = document.getElementById("responseTarget");
const portfolioAddedPrompt = document.getElementById("htmxPortfolioResponse");


// the input box where ticker is filled out for watchlist
const tickerInputBox = document.getElementById("add-stock-input-box");

// const formTarget = document.getElementById("portfolio-form-id");
// formTarget.style.display = "none";

// add ticker to portfolio form
const tickerBox = document.getElementById("id_ticker");
const sharesOwnedBox = document.getElementById("id_shares_owned");
const pricePerUnitBox = document.getElementById("id_price_per_unit");

// watchlist add button
const watchlistSubmitbtn = document.querySelector(".watchlist-submit-btn")

// for watchlist deletion
const divSwapper = (stock) => {
    addedPrompt.textContent = `${stock} deleted from watchlist!`;
    setTimeout(() => {
        addedPrompt.innerHTML = "";
    }, 1000);
}

// watchlist
const boxToggler = () => {
    stockAddLink.style.display = "none";
    entryForm.style.display = "block";
    doneLink.style.display = "block";
    if (addedPrompt.textContent !== "") {
        addedPrompt.textContent = "";
    };
};
// watchlist
const originalState = () => {
    stockAddLink.style.display = "block";
    entryForm.style.display = "none";
    doneLink.style.display = "none";
    addedPrompt.textContent = "";
};



const getPresetValues = (sharesOwned, pricePerUnit, ticker, companyName) => {
    if (editForm.style.display === "block") {
        const editInputs = editForm.querySelectorAll("input");
        editInputs[1].value = `${ticker}`
        editInputs[1].disabled = true
        editInputs[2].value = `${companyName}`
        editInputs[2].disabled = true
        editInputs[3].value = sharesOwned
        editInputs[4].value = pricePerUnit

    }
}

// EDIT FORM
const formTarget = document.getElementById("portfolio-form-id");
formTarget.style.display = "none";
const editForm = document.getElementById("edit-form-id");
editForm.style.display = "none";
const portfolioEditBtn = document.getElementById("portfolio-edit-btn")
let overlay;

const editFormToggler = (command) => {
    if (command == "open") {
        editForm.style.display = "block";
        formTarget.style.display = "none"
        if (!overlay) {
            overlay = document.getElementById("page-overlay")
            overlay.style.display = "block"
        } else {
            overlay.style.display = "block"
        }
        overlay.addEventListener("click", function () {
            if (editForm.style.display === "block") {
                editForm.style.display = "none"
            }
            overlay.style.display = "none"
        })
    } else {
        overlay.style.display = "none"
        editForm.style.display = "none";

    }
}
// i need to enable this when form is submitted so that value is sent in the request
// EDIT FORM
const forValidation = () => {
    const editFormTickerInput = editForm.querySelector("#id_ticker");
    editFormTickerInput.disabled = false;
    const editCompanyName = editForm.querySelector("#id_company_name")
    editCompanyName.disabled = false;
}


const formToggler = (arg) => {
    if (arg === "open") {
        formTarget.style.display = "block";
        editForm.style.display = "none"
        if (!overlay) {
            overlay = document.getElementById("page-overlay")
            overlay.style.display = "block"
        } else {
            overlay.style.display = "block"
        };
        overlay.style.display = "block"
        overlay.addEventListener("click", function () {
            if (formTarget.style.display == "block") {
                formTarget.style.display = "none"
            }
            overlay.style.display = "none"
        })

    } else {
        formTarget.style.display = "none";
        overlay.style.display = "none"
        tickerBox.value = "";
        sharesOwnedBox.value = "";
        pricePerUnitBox.value = "";
        portfolioAddedPrompt.innerHTML = "";

    };
};




// HTMX LISTENERS BELOW

// listening to portfolio form
portfolioForm.addEventListener("htmx:afterRequest", (ev) => {
    if (ev.detail.successful) {
        tickerBox.value = "";
        sharesOwnedBox.value = "";
        pricePerUnitBox.value = "";
        portfolioAddedPrompt.innerHTML = "Success! stock added to your portfolio"
        setTimeout(() => {
            portfolioAddedPrompt.innerHTML = ""
        }, 1500)
    } else {
        portfolioAddedPrompt.innerHTML = ev.detail.xhr.responseText;
        setTimeout(() => {
            portfolioAddedPrompt.innerHTML = ""
        }, 1500)
    };
});

// had to enable input box to send request
// after request disable the input again
editForm.addEventListener("htmx:afterRequest", (ev) => {
    const target = editForm.querySelector("#javaScriptResponseTarget");
    if (!ev.detail.successful) {
        target.innerHTML = ev.detail.xhr.responseText
        setTimeout(() => {
            target.innerHTML = ""
        }, 1500)
    } else {
        editForm.querySelector("#id_company_name").disabled = true;
        editForm.querySelector("#id_ticker").disabled = true;
        target.innerHTML = "Success, portfolio has been update";
        setTimeout(() => {
            target.innerHTML = ""
        }, 1500)
    };
});


// watchlist form control
form.addEventListener("htmx:afterRequest", (ev) => {
    if (ev.detail.successful) {
        tickerInputBox.value = "";
    } else {
        addedPrompt.innerHTML = ev.detail.xhr.responseText;
        tickerInputBox.value = "";
        setTimeout(() => {
            addedPrompt.innerHTML = "";
        }, 1500);
    };
});



document.body.addEventListener("htmx:afterOnLoad", function (ev) {
    const mulitResponseBox = document.querySelector(".multiResponse")
    if (mulitResponseBox) {
        const links = mulitResponseBox.querySelectorAll("a[hx-get]")
        links.forEach(link => {
            link.addEventListener("htmx:afterRequest", function (ev) {
                if (ev.detail.failed) {
                    addedPrompt.innerHTML = ev.detail.xhr.responseText
                    setTimeout(() => {
                        addedPrompt.innerHTML = ""
                    }, 1500);
                } else {
                    addedPrompt.innerHTML = "added to watchlist!!"
                    setTimeout(() => {
                        addedPrompt.innerHTML = ""
                    }, 1500);
                };
            })
        })
    };
})




document.body.addEventListener("htmx:afterSettle", function () {
    const portfolioAddItemLink = document.getElementById("portfolio-form-link")
    portfolioAddItemLink.addEventListener("click", function (evt) {
        evt.preventDefault()
    })
    const cardDivs = document.querySelectorAll(".data-grid-item")
    cardDivs.forEach(selectedDiv => {
        let atags = selectedDiv.querySelectorAll("a")
        atags.forEach(aTag => {
            if (aTag.getAttribute("href") == "#") {
                aTag.addEventListener("click", function (evt) {
                    evt.preventDefault()
                })
            }
        })
    })
})


// next 3 for multi ticker matches when trying to add to watchlist
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

function scrollToElementIfNeeded(el) {
    if (!isElementInViewport(el)) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}


document.body.addEventListener('htmx:afterSwap', (event) => {
    const swappedElement = document.querySelector('.multiResponse-wrapper');

    if (swappedElement) {
        scrollToElementIfNeeded(swappedElement);
    }
});






window.addEventListener("pageshow", function () {
    if (editForm.style.display == "block") {
        editForm.style.display = "none"
    } else if (formTarget.style.display == "block") {
        formTarget.style.display = "none"
    }
})
