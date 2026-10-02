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

const deleteAccountButton =
    document.getElementById("delete-account-button");

const deleteAccountPopup =
    document.getElementById("delete-account-popup");

const deleteAccountCancel =
    document.getElementById("delete-account-cancel");

const deleteAccountConfirmPopup =
    document.getElementById("delete-account-confirm-popup");

const deleteAccountConfirmCancel =
    document.getElementById(
        "delete-account-confirm-cancel"
    );

if (
    deleteAccountButton &&
    deleteAccountPopup &&
    deleteAccountCancel &&
    deleteAccountConfirmPopup &&
    deleteAccountConfirmCancel
) {
    const deleteAccountForm =
        deleteAccountPopup.querySelector("form");
    const deleteAccountErrors =
        document.getElementById("delete-account-errors");

    // Keep the confirmation step closed until the first form is accepted.
    deleteAccountPopup.hidden = true;
    deleteAccountConfirmPopup.hidden = true;

    deleteAccountButton.addEventListener("click", () => {
        deleteAccountConfirmPopup.hidden = true;
        deleteAccountErrors.hidden = true;
        deleteAccountErrors.textContent = "";
        deleteAccountPopup.hidden = false;
    });

    deleteAccountCancel.addEventListener("click", () => {
        deleteAccountPopup.hidden = true;
    });

    deleteAccountConfirmCancel.addEventListener("click", () => {
        deleteAccountConfirmPopup.hidden = true;
    });

    deleteAccountForm.addEventListener(
        "submit",
        async (event) => {
            event.preventDefault();
            deleteAccountErrors.hidden = true;
            deleteAccountErrors.textContent = "";

            const formData =
                new FormData(deleteAccountForm);

            try {
                const response = await fetch(
                    deleteAccountForm.action,
                    {
                        method: "POST",
                        body: formData,
                    }
                );

                const data = await response.json();

                if (!response.ok || !data.success) {
                    const fieldLabels = {
                        confirmation: 'Type "DELETE" to confirm.',
                        password: "Invalid password.",
                        confirm_password: "Passwords do not match.",
                        __all__: "Please check the entered details.",
                    };
                    const errors = Object.entries(data.errors || {})
                        .flatMap(([field, fieldErrors]) => {
                            const messages = Array.isArray(fieldErrors)
                                ? fieldErrors.map(error =>
                                    typeof error === "string"
                                        ? error
                                        : error.message
                                )
                                : [String(fieldErrors)];

                            return messages.map(message =>
                                fieldLabels[field] || message
                            );
                        });

                    deleteAccountErrors.textContent = errors.length
                        ? [...new Set(errors)].join(" ")
                        : "Unable to verify the account details. Please try again.";
                    deleteAccountErrors.hidden = false;
                    return;
                }

                deleteAccountPopup.hidden = true;
                deleteAccountConfirmPopup.hidden = false;
            } catch (error) {
                deleteAccountErrors.textContent =
                    "Could not verify the details. Please try again.";
                deleteAccountErrors.hidden = false;
            }
        }
    );
}
