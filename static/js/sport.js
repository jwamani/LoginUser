document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('register-form').onsubmit = async function (e) {
        console.log("Sports registration form submitted");
        e.preventDefault();

        const formData = new FormData(e.target);
        const response = await fetch("/register_sport", {method: "POST", body: formData,});
        const result = await response.json();

        displayFlashMessages(result.status, result.message);
        
        // if (result.status == "success") {
        //     setTimeout(() => window.location.href = "/registrants", 1000);
        // }
    };
});