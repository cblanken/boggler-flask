let theme_toggle = document.querySelector(".theme-switch input[type='checkbox']")
theme_toggle.addEventListener("change", e => {
    if (e.target.checked) {
        document.documentElement.setAttribute("data-theme", "dark");
    } else {
        document.documentElement.setAttribute("data-theme", "light");
    }
}, false);