// script.js
let username = 
document.querySelector("#emailid")
document.querySelector("#formid")
    .addEventListener("submit", (e) => {
        e.preventDefault();
        let valueinput = username.value
        if (valueinput.length < 5 ||
            valueinput.includes(" ")) {
            alert("please enter valid email")
        }
    }
    )