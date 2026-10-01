const profileDataElement = document.getElementById("profile-data");

const checkUsernameUrl =
    profileDataElement.dataset.checkUsernameUrl;

const hasErrors =
    profileDataElement.dataset.hasErrors === "true";

const editButton = document.getElementById("edit-profile-button");
const modal = document.getElementById("edit-profile-modal");
const closeButton = document.getElementById("close-profile-modal");

const usernameInput = document.getElementById("id_username");

const usernameAvailability = document.createElement("p");
usernameInput.parentElement.appendChild(usernameAvailability);

let usernameCheckTimeout = null;

usernameInput.addEventListener("input", () => {
    clearTimeout(usernameCheckTimeout);

    const username = usernameInput.value.trim();

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
                "Username is already taken";
        }
    }, 300);
});

editButton.addEventListener("click", () => {
    modal.style.display = "flex";
});

closeButton.addEventListener("click", () => {
    modal.style.display = "none";
});

if (hasErrors) {
    modal.style.display = "flex";
}