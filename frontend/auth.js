const authForm = document.getElementById("authForm");
const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");
const nameField = document.getElementById("nameField");
const nameInput = document.getElementById("name");
const submitButton = document.getElementById("submitButton");
const message = document.getElementById("message");

let mode = "login";

function setMode(nextMode) {
    mode = nextMode;
    const registering = mode === "register";

    nameField.hidden = !registering;
    nameInput.required = registering;
    loginTab.classList.toggle("active", !registering);
    registerTab.classList.toggle("active", registering);
    submitButton.textContent = registering ? "Create account" : "Login";
    message.textContent = "";
}

loginTab.addEventListener("click", () => setMode("login"));
registerTab.addEventListener("click", () => setMode("register"));

authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    message.textContent = "";
    submitButton.disabled = true;

    const payload = {
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value
    };

    if (mode === "register") {
        payload.name = nameInput.value.trim();
    }

    try {
        const response = await fetch(
            mode === "register" ? "/api/register" : "/api/login",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
                body: JSON.stringify(payload)
            }
        );

        let data;
        try {
            data = await response.json();
        } catch {
            throw new Error("Server returned an unexpected response. Check the Flask terminal.");
        }

        if (!response.ok) {
            throw new Error(data.error || "Authentication failed");
        }

        window.location.replace("/dashboard");
    } catch (error) {
        message.textContent = error.message || "Could not connect to the server.";
    } finally {
        submitButton.disabled = false;
    }
});

// Start in login mode.
setMode("login");
