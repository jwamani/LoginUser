function displayFlashMessages(status, message) {
    const flashContainer = document.getElementById("flash-messages"); 
    flashContainer.innerHTML = '';
    const msgElement = document.createElement("div");
    msgElement.className = `flash-message ${status}`;
    msgElement.textContent = message;
    flashContainer.appendChild(msgElement);
}
document.addEventListener("DOMContentLoaded", function() {
        document.getElementById('logout-link').addEventListener("click", async function(e) {
        console.log("Logout link clicked");
        e.preventDefault();
        const response = await fetch("/logout", {method: "GET"});
        const result = await response.json();
        
        displayFlashMessages(result.status, result.message);

        if (result.status == "info") {
            setTimeout(() => window.location.href = "/login", 1000);
        }
        });
    
});








