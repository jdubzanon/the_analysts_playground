


// const mainActionLink = document.querySelector(".main-action-link")
const mainActionsDiv = document.querySelector(".actions")
const actionsDiv = document.querySelector(".actions-div")
const actionsMainLink = document.querySelector(".actions-link-main")
const caretDownLink = document.querySelector(".caret-down-link")

const promptDiv = document.getElementById("watchlist-prompt")
const competitorDiv = document.getElementById("competitor-swap")
const showComptetitorsLink = document.querySelector(".show-competitors")
const companyInfo = document.getElementById("company-info-swap")
const overlay = document.getElementById("page-overlay")
const companyInfoLink = document.querySelector(".company-info")
const indexSwap = document.getElementById("index-swap")

const closeRelated = function () {
    if (indexSwap.classList.contains("expand-right")) {
        indexSwap.classList.remove("expand-right")
        overlay.style.display = "none"
    }

}


// CHANGING LINK COLOR
actionsMainLink.addEventListener("mouseover", function () {
    caretDownLink.style.color = "#37b24d"
    actionsMainLink.style.color = "#37b24d"
})

caretDownLink.addEventListener("mouseover", function () {
    actionsMainLink.style.color = "#37b24d"
    caretDownLink.style.color = "#37b24d"
})


actionsMainLink.addEventListener("mouseout", function () {
    caretDownLink.style.color = "#4263eb"
    actionsMainLink.style.color = "#4263eb"
})

caretDownLink.addEventListener("mouseout", function () {
    caretDownLink.style.color = "#4263eb"
    actionsMainLink.style.color = "#4263eb"
})


for (let child of actionsDiv.children) {
    child.addEventListener("click", function (event) {
        event.preventDefault()
        mainActionsDiv.classList.toggle("expanded")
    })
}




if (showComptetitorsLink) {
    showComptetitorsLink.addEventListener("click", function (event) {
        event.preventDefault();
        if (competitorDiv) {
            competitorDiv.classList.toggle("expand-right")
        } else {
            indexSwap.classList.toggle("expand-right")
        }
        const overlay = document.getElementById("page-overlay")
        overlay.style.display = "block"
        overlay.addEventListener("click", function () {
            if (competitorDiv) {

                if (competitorDiv.classList.contains("expand-right")) {
                    competitorDiv.classList.remove("expand-right")
                    overlay.style.display = "none"
                }
            } else {
                if (indexSwap.classList.contains("expand-right")) {
                    indexSwap.classList.remove("expand-right")
                    overlay.style.display = "none"
                }

            }
        })
    })
}





if (companyInfoLink) {
    companyInfoLink.addEventListener("click", function (event) {
        event.preventDefault();
        companyInfo.classList.add("expand-right")
        overlay.style.display = "block"
        overlay.addEventListener("click", function () {
            if (companyInfo.classList.contains("expand-right")) {
                companyInfo.classList.remove("expand-right")
                overlay.style.display = "none"
            }
        })
    })

}


const closePopup = (popup) => {
    if (popup === "companyInfo") {
        companyInfo.classList.toggle("expand-right")
        if (overlay.style.display === "block") {
            overlay.style.display = "none"
        }

    } else if (popup === "relatedStocks") {
        competitorDiv.classList.toggle("expand-right")
        if (overlay.style.display === "block") {
            overlay.style.display = "none"
        }
    }
}



document.body.addEventListener("htmx:afterSettle", function (evt) {
    const companyInfoClose = document.querySelector(".close-link-company-info")
    if (companyInfoClose) {
        companyInfoClose.addEventListener("click", function (evt) {
            evt.preventDefault()
        })

    };

    const competitorCloseLink = document.querySelector(".competitor-close")
    if (competitorCloseLink) {
        competitorCloseLink.addEventListener("click", function (evt) {
            evt.preventDefault()
        })
    }

    const relatedIndexClose = document.querySelector(".related-indices-close-link")
    if (relatedIndexClose) {
        relatedIndexClose.addEventListener("click", function (evt) {
            evt.preventDefault()
        })
    }


    if (evt.detail.xhr.responseText === "Remove from watchlist") {
        promptDiv.style.color = "#c2255c"
        promptDiv.textContent = "Added to Watchlist!!"
        if (promptDiv.style.display == "none") {
            promptDiv.style.display = "block"

        }
        setTimeout(function () {
            promptDiv.style.display = "none"
        }, 1500)
    } else if (evt.detail.xhr.responseText == "Add to watchlist") {
        promptDiv.style.color = "#c2255c"
        promptDiv.textContent = "Removed from Watchlist!!"
        if (promptDiv.style.display == "none") {
            promptDiv.style.display = "block"
        }
        setTimeout(function () {
            promptDiv.style.display = "none"
        }, 1500)
    }
})

window.addEventListener('pageshow', function (event) {
    if (competitorDiv) {
        if (competitorDiv.classList.contains("expand-right")) {
            competitorDiv.classList.remove("expand-right")
        };
    } else if (companyInfo) {

        if (companyInfo.classList.contains("expand-right")) {
            companyInfo.classList.remove("expand-right")
        };

    } else if (indexSwap) {
        if (indexSwap.classList.contains("expand-right")) {
            indexSwap.classList.remove("expand-right")
        }
    }

});
