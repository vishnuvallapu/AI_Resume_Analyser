const analyzeForm = document.getElementById("analyzeForm");
const analyzeButton = document.getElementById("analyzeButton");
const statusMessage = document.getElementById("status");
const results = document.getElementById("results");

function showList(elementId, items) {
    const list = document.getElementById(elementId);
    list.replaceChildren();

    if (!items || items.length === 0) {
        const item = document.createElement("li");
        item.textContent = "No items to display.";
        list.appendChild(item);
        return;
    }

    items.forEach((value) => {
        const item = document.createElement("li");
        item.textContent = value;
        list.appendChild(item);
    });
}

async function loadUser() {
    const response = await fetch("/api/me");

    if (!response.ok) {
        window.location.replace("/");
        return;
    }

    const data = await response.json();
    document.getElementById("welcome").textContent =
        `Welcome, ${data.user.name}!`;
}

analyzeForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const resume = document.getElementById("resume").files[0];
    const jobDescription =
        document.getElementById("jobDescription").value.trim();

    if (!resume || !jobDescription) {
        statusMessage.textContent =
            "Select a resume and enter a job description.";
        return;
    }

    if (resume.size > 5 * 1024 * 1024) {
        statusMessage.textContent = "The PDF must be smaller than 5 MB.";
        return;
    }

    const formData = new FormData(analyzeForm);

    analyzeButton.disabled = true;
    statusMessage.textContent = "Analyzing resume. Please wait...";
    results.hidden = true;

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            body: formData,
            credentials: "same-origin"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Analysis failed");
        }

        document.getElementById("score").textContent =
            `${data.match_score}%`;

        document.getElementById("scoreNote").textContent =
            "This score measures weighted coverage of recognized skills, not a guaranteed ATS ranking.";

        showList("matchedSkills", data.matched_skills);
        showList("missingSkills", data.missing_skills);
        showList("strengths", data.strengths);
        showList("suggestions", data.suggestions);

        document.getElementById("summary").textContent =
            data.summary || "No summary available.";

        document.getElementById("aiStatus").textContent =
            data.ai_used
                ? "AI feedback generated successfully."
                : "Basic feedback displayed; AI feedback was unavailable.";

        results.hidden = false;
        statusMessage.textContent =
            "Analysis completed and saved successfully.";

    } catch (error) {
        statusMessage.textContent = error.message;
    } finally {
        analyzeButton.disabled = false;
    }
});

document.getElementById("logoutButton").addEventListener("click", async () => {
    await fetch("/api/logout", {
        method: "POST",
        credentials: "same-origin"
    });

    window.location.replace("/");
});

loadUser().catch(() => {
    window.location.replace("/");
});