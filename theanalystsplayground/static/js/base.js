// DIV SLIDE OUT
// main outer if statement added for hx-push-url and variable already defined errors

if (typeof globalThis.navBar == "undefined" && typeof globalThis.overlay == "undefined" && typeof globalThis.navLink == "undefined") {

  // remove all links
  const allLinks = document.querySelectorAll("a");
  allLinks.forEach(link => {
    link.addEventListener("click", function (evt) {
      if (this.getAttribute("href") === "#") {
        evt.preventDefault();
      }
    });
  });

  const navBar = document.getElementById("nav-bar-div")
  const overlay = document.getElementById("page-overlay")
  const navLink = document.querySelector(".navigation-link")
  const closeIcon = document.getElementById("closeIcon")

  closeIcon.addEventListener("click", function () {
    navBar.classList.toggle("show")
    if (overlay.style.display === "block") {
      overlay.style.display = "none"
    }
  })


  window.addEventListener('pageshow', function (event) {
    if (navBar.classList.contains("show")) {
      navBar.classList.remove("show")
    }
  });


  navLink.addEventListener("click", function () {
    if (!navBar.classList.contains("show")) {
      navBar.classList.toggle("show")
      overlay.style.display = "block"
      overlay.addEventListener("click", function () {
        if (navBar.classList.contains("show")) {
          navBar.classList.remove("show")
        }
        overlay.style.display = "none"
      })

    } else if (navBar.classList.contains("show")) {
      navBar.classList.remove("show")
      if (overlay.style.display === "block") {
        overlay.style.display = "none"
      }
    }
  })
}
