document.querySelector("form").addEventListener("submit", function () {
    alert("Login submitted");
});



// Login form validation
const loginForm = document.querySelector("form");

if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
        const inputs = loginForm.querySelectorAll("input");
        let isValid = true;

        inputs.forEach(input => {
            if (input.value.trim() === "") {
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
            alert("Please fill all fields before logging in.");
        }
    });
}
