let questions = [];
let currentIndex = 0;
let answers = {};
let attemptId = null;
let timeLeft = 120; // 2 minutes (change later)
let timerInterval;

const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3NTU4MTM4LCJpYXQiOjE3Nzc1NTc4MzgsImp0aSI6IjJhNWQ1YjU2YTdiMzRjNzViZDM0YjNmYzdmMTU0NmVlIiwidXNlcl9pZCI6IjIifQ.OxEtnNzFn2MEZ2Mn1opwDLQm0TduPPfPo1hVZvSBLIg";

// 🔹 Start test + load questions
window.onload = function () {

    startTimer();
    // STEP 1: Start test
    fetch("http://127.0.0.1:8000/api/tests/1/start/", {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(startData => {

        attemptId = startData.attempt_id;

        // STEP 2: Get questions
        return fetch("http://127.0.0.1:8000/api/tests/1/", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });
    })
    .then(res => res.json())
    .then(data => {
        questions = data.questions;
        showQuestion();
    });
};

// 🔹 Show question
function showQuestion() {
    const q = questions[currentIndex];

    // Question number
    document.getElementById("questionNumber").innerText =
        `Question ${currentIndex + 1} of ${questions.length}`;

    document.getElementById("questionText").innerText = q.question_text;

    // Progress
    const answeredCount = Object.keys(answers).length;
    document.getElementById("progress").innerText =
        `Answered: ${answeredCount} / ${questions.length}`;

    const optionsDiv = document.getElementById("options");
    optionsDiv.innerHTML = "";

    ["a", "b", "c", "d"].forEach(opt => {
        const btn = document.createElement("button");
        btn.innerText = q["option_" + opt];

        if (answers[q.id] === opt.toUpperCase()) {
            btn.classList.add("selected");
        }

        btn.onclick = () => {
            answers[q.id] = opt.toUpperCase();
            showQuestion();
        };

        optionsDiv.appendChild(btn);
    });
}

// 🔹 Navigation
function nextQuestion() {
    if (currentIndex < questions.length - 1) {
        currentIndex++;
        showQuestion();
    }
}

function prevQuestion() {
    if (currentIndex > 0) {
        currentIndex--;
        showQuestion();
    }
}

// 🔹 Submit test
function submitTest() {

    clearInterval(timerInterval);
    if (!confirm("Are you sure you want to submit?")) return;

    fetch("http://127.0.0.1:8000/api/tests/submit/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            attempt_id: attemptId,
            answers: answers
        })
    })
    .then(res => res.json())
    .then(data => {

        // Hide test UI
        document.getElementById("questionBox").style.display = "none";
        document.querySelector(".buttons").style.display = "none";

        // Show result
        const resultBox = document.getElementById("resultBox");
        resultBox.style.display = "block";

        resultBox.innerHTML = `
            <h2>Test Completed</h2>
            <p>Score: ${data.score} / ${data.total}</p>
            <p>Accuracy: ${((data.score / data.total) * 100).toFixed(2)}%</p>
        `;
    });
}

function startTimer() {

    timerInterval = setInterval(() => {

        let minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;

        seconds = seconds < 10 ? "0" + seconds : seconds;

        document.getElementById("timer").innerText =
            `Time Left: ${minutes}:${seconds}`;

        timeLeft--;

        if (timeLeft < 0) {
            clearInterval(timerInterval);
            alert("Time's up! Submitting test...");
            submitTest();
        }

    }, 1000);
}