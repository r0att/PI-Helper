const registerData =
    document.getElementById("register-data");

const checkUsernameUrl =
    registerData.dataset.checkUsernameUrl;

const usernameInput =
    document.getElementById("id_username");

const usernameAvailability =
    document.createElement("p");

usernameInput.parentElement.appendChild(
    usernameAvailability
);

let usernameCheckTimeout = null;

usernameInput.addEventListener("input", () => {
    clearTimeout(usernameCheckTimeout);

    const username =
        usernameInput.value.trim();

    usernameAvailability.textContent = "";

    if (!username) {
        return;
    }

    usernameCheckTimeout = setTimeout(async () => {
        const response = await fetch(
            `${checkUsernameUrl}?username=${encodeURIComponent(username)}`
        );

        const data = await response.json();

        if (data.available) {
            usernameAvailability.textContent =
                "Username is available.";
        } else {
            usernameAvailability.textContent =
                "Username is already taken.";
        }
    }, 300);
});