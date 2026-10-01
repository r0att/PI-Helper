const hardModeData =
    document.getElementById("hard-mode-data");

const startDigit = Number(
    hardModeData.dataset.startDigit
);

const piDigits =
    hardModeData.dataset.piDigits;

const hasEndDigit =
    hardModeData.dataset.endDigit !== "None";

const endDigit =
    hardModeData.dataset.endDigit;

const finishUrl =
    hardModeData.dataset.finishUrl;

const csrfToken =
    hardModeData.dataset.csrfToken;


const bestTimeElement =
    document.getElementById("best-time");

if (bestTimeElement) {
    const bestTimeMs =
        Number(bestTimeElement.dataset.time);

    if (bestTimeMs < 60000) {
        bestTimeElement.textContent =
            (bestTimeMs / 1000).toFixed(3) + " s";
    } else {
        const minutes =
            Math.floor(bestTimeMs / 60000);

        const seconds =
            ((bestTimeMs % 60000) / 1000).toFixed(3);

        bestTimeElement.textContent =
            minutes + " m " + seconds + " s";
    }
}


let currentIndex = 0;
let enteredDigits = "";
let lives = 1;
let statsSaved = false;
let startTime = null;
let timerInterval = null;
let finalTimeMs = 0;

const input =
    document.getElementById("digit-input");

const enteredDisplay =
    document.getElementById("entered-digits");

const livesDisplay =
    document.getElementById("lives");

const timerDisplay =
    document.getElementById("timer");


input.addEventListener("input", () => {
    const digit = input.value;

    if (!/^\d$/.test(digit)) {
        input.value = "";
        return;
    }

    if (digit === piDigits[currentIndex]) {
        if (startTime === null) {
            startTime = performance.now();

            timerInterval = setInterval(() => {
                const elapsed =
                    performance.now() - startTime;

                timerDisplay.textContent =
                    (elapsed / 1000).toFixed(3);
            }, 10);
        }

        enteredDigits += digit;
        currentIndex++;

        enteredDisplay.textContent =
            enteredDigits.slice(-4);

        input.value = "";

        if (
            hasEndDigit &&
            currentIndex >=
                Number(endDigit) - startDigit + 1
        ) {
            const elapsed =
                performance.now() - startTime;

            timerDisplay.textContent =
                (elapsed / 1000).toFixed(3);

            finalTimeMs =
                Math.round(elapsed);

            input.disabled = true;

            finishHardMode(true);

            alert("Hard Mode completed!");

            return;
        }

        if (currentIndex === piDigits.length) {
            const elapsed =
                performance.now() - startTime;

            timerDisplay.textContent =
                (elapsed / 1000).toFixed(3);

            finalTimeMs =
                Math.round(elapsed);

            input.disabled = true;

            finishHardMode(true);

            alert("No more PI digits available.");

            return;
        }
    } else {
        lives--;

        livesDisplay.textContent = lives;

        input.value = "";

        if (lives === 0) {
            input.disabled = true;

            finishHardMode(false);

            alert("Game over!");
        }
    }
});


function finishHardMode(won) {
    clearInterval(timerInterval);

    if (statsSaved) {
        return;
    }

    statsSaved = true;

    const formData =
        new URLSearchParams();

    formData.append(
        "start_digit",
        startDigit
    );

    formData.append(
        "end_digit",
        hardModeData.dataset.endDigit
    );

    formData.append(
        "digits_entered",
        enteredDigits.length
    );

    formData.append(
        "won",
        won
    );

    formData.append(
        "time_ms",
        finalTimeMs
    );

    fetch(finishUrl, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type":
                "application/x-www-form-urlencoded",
        },
        body: formData,
    });
}