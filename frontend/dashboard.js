window.onload = function () {

    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3NTU2ODA2LCJpYXQiOjE3Nzc1NTY1MDYsImp0aSI6IjQ4ODIxYmE3ZWI1OTQ0ZDJiMjI0ODNlMTZiZTc3ODA3IiwidXNlcl9pZCI6IjIifQ.cEbnozYCuU1dmNFdy6Nwne-weEa9bLT7YvPSu_pcvKM";

    fetch("http://127.0.0.1:8000/api/analytics/dashboard/", {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {

        // ✅ Cards
        document.getElementById("total").innerText = data.overall.total_attempts;
        document.getElementById("correct").innerText = data.overall.correct_answers;
        document.getElementById("accuracy").innerText = data.overall.accuracy + "%";

        // ✅ Topic List
        const topicList = document.getElementById("topics");
        topicList.innerHTML = "";
        data.topics.forEach(t => {
            const li = document.createElement("li");
            li.textContent = `${t.topic} - ${t.accuracy}%`;
            topicList.appendChild(li);
        });

        // ✅ Weak Topics
        const weakList = document.getElementById("weak");
        weakList.innerHTML = "";
        data.weak_topics.forEach(t => {
            const li = document.createElement("li");
            li.textContent = `${t.topic} - ${t.accuracy}%`;
            li.classList.add("weak");
            weakList.appendChild(li);
        });

        // ✅ Chart 1 (Bar)
        const topicLabels = data.topics.map(t => t.topic);
        const topicValues = data.topics.map(t => t.accuracy);

        new Chart(document.getElementById("topicChart"), {
            type: "bar",
            data: {
                labels: topicLabels,
                datasets: [{
                    label: "Accuracy %",
                    data: topicValues
                }]
            }
        });

        // ✅ Chart 2 (Pie)
        const correct = data.overall.correct_answers;
        const wrong = data.overall.total_attempts - correct;

        new Chart(document.getElementById("performanceChart"), {
            type: "pie",
            data: {
                labels: ["Correct", "Wrong"],
                datasets: [{
                    data: [correct, wrong]
                }]
            }
        });

    });
};