const challengeData = document.getElementById("challenge-data");

const startDigit = Number(
    challengeData.dataset.startDigit
);

const piDigits = challengeData.dataset.piDigits;

const hasEndDigit =
    challengeData.dataset.endDigit !== "None";

const endDigit = challengeData.dataset.endDigit;

const finishUrl = challengeData.dataset.finishUrl;

const csrfToken = challengeData.dataset.csrfToken;


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
let lives = 3;
let totalEntered = 0;
let statsSaved = false;
let startTime = null;
let timerInterval = null;
let finalTimeMs = 0;

const input =
    document.getElementById("digit-input");

const enteredCount =
    document.getElementById("entered-count");

const enteredDisplay =
    document.getElementById("entered-digits");

const currentDigit =
    document.getElementById("current-digit");

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
        totalEntered++;

        enteredCount.textContent =
            enteredDigits.length;

        enteredDisplay.textContent =
            enteredDigits;

        if (totalEntered % 100 === 0) {
            lives = 3;
            livesDisplay.textContent = lives;
        }

        input.value = "";

        if (
            hasEndDigit &&
            currentIndex >=
                Number(endDigit) - startDigit + 1
        ) {
            finalTimeMs =
                Math.round(
                    Number(timerDisplay.textContent) * 1000
                );

            input.disabled = true;

            finishChallenge(true);

            alert("Challenge completed!");

            return;
        }

        if (currentIndex === piDigits.length) {
            finalTimeMs =
                Math.round(
                    Number(timerDisplay.textContent) * 1000
                );

            input.disabled = true;

            finishChallenge(true);

            alert("No more PI digits available.");

            return;
        }

        currentDigit.textContent =
            startDigit + currentIndex;
    } else {
        lives--;

        livesDisplay.textContent = lives;

        input.value = "";

        if (lives === 0) {
            input.disabled = true;

            finishChallenge(false);

            alert("Game over!");
        }
    }
});


function finishChallenge(won) {
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
        challengeData.dataset.endDigit
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