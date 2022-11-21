let theme_toggle = document.querySelector("#theme-switch");
let theme_toggle_slider = document.querySelector("#theme-switch .toggle-slider");
let theme_toggle_checkbox = document.querySelector("#theme-switch input[type='checkbox']");
theme_toggle.addEventListener("click", e => {
    theme_toggle_checkbox.checked = !theme_toggle_checkbox.checked;
    if (theme_toggle_checkbox.checked) {
        document.documentElement.setAttribute("data-theme", "dark");
        theme_toggle_slider.classList.add("toggle-slider-anim-dark")
        change_theme("toggle-slider-anim-light");
    } else {
        document.documentElement.setAttribute("data-theme", "light");
        theme_toggle_slider.classList.add("toggle-slider-anim-light")
        change_theme("toggle-slider-anim-dark");
    }
    save_theme();
}, false);

function debounce(func, timeout = 250) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args) }, timeout);
    }
}

function change_theme(anim_class) {
    debounce(() => {
        theme_toggle_slider.classList.add(anim_class);
    });
    theme_toggle_slider.classList.remove(anim_class);
}

function save_theme() {
    let theme = document.documentElement.getAttribute("data-theme");
    localStorage.setItem("theme", theme);
}

function get_theme_setting() {
    return document.documentElement.getAttribute("data-theme") ?? localStorage.getItem("theme");
}

let theme = get_theme_setting();
if (theme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
    theme_toggle_slider.classList.add("toggle-slider-anim-dark")
}