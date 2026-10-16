const historyList = document.getElementById("historyList");
const statusMessage = document.getElementById("status");
const details = document.getElementById("details");

function fillList(id, items) {
    const list = document.getElementById(id);
    list.replaceChildren();

    (items || []).forEach((value) => {
        const li = document.createElement("li");
        li.textContent = value;
        list.appendChild(li);
    });

    if (!items || items.length === 0) {
        const li = document.createElement("li");
        li.textContent = "None recorded.";
        list.appendChild(li);
    }
}

async function api(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options
    });

    const data = await response.json();

    if (response.status === 401) {
        window.location.replace("/");
        throw new Error("Please log in.");
    }

    if (!response.ok) {
        throw new Error(data.error || "Request failed");
    }

    return data;
}

async function viewAnalysis(id) {
    try {
        const data = await api(`/api/analyses/${id}`);
        const savedSuggestions = data.suggestions || {};

        document.getElementById("detailTitle").textContent =
            data.job_title;

        document.getElementById("detailScore").textContent =
            `Weighted match score: ${data.match_score}%`;

        fillList("detailMatched", data.matched_skills);
        fillList("detailMissing", data.missing_skills);
        fillList(
            "detailSuggestions",
            savedSuggestions.suggestions || []
        );

        document.getElementById("detailSummary").textContent =
            data.summary || "";

        details.hidden = false;
        details.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        statusMessage.textContent = error.message;
    }
}

async function deleteAnalysis(id) {
    if (!window.confirm("Delete this analysis permanently?")) {
        return;
    }

    try {
        await api(`/api/analyses/${id}`, { method: "DELETE" });
        details.hidden = true;
        await loadHistory();
        statusMessage.textContent = "Analysis deleted.";
    } catch (error) {
        statusMessage.textContent = error.message;
    }
}

async function loadHistory() {
    try {
        const data = await api("/api/analyses");
        historyList.replaceChildren();

        if (data.analyses.length === 0) {
            statusMessage.textContent = "No analyses saved yet.";
            return;
        }

        statusMessage.textContent =
            `${data.analyses.length} saved analysis/analyses.`;

        data.analyses.forEach((item) => {
            const card = document.createElement("article");
            card.className = "history-card";

            const title = document.createElement("h3");
            title.textContent = item.job_title;

            const score = document.createElement("p");
            score.textContent = `Match score: ${item.match_score}%`;

            const date = document.createElement("p");
            date.textContent = `Created: ${item.created_at}`;

            const view = document.createElement("button");
            view.textContent = "View";
            view.addEventListener("click", () => viewAnalysis(item.id));

            const remove = document.createElement("button");
            remove.textContent = "Delete";
            remove.addEventListener(
                "click", () => deleteAnalysis(item.id)
            );

            card.append(title, score, date, view, remove);
            historyList.appendChild(card);
        });

    } catch (error) {
        statusMessage.textContent = error.message;
    }
}

document.getElementById("logoutButton").addEventListener("click", async () => {
    await fetch("/api/logout", { method: "POST" });
    window.location.replace("/");
});

loadHistory();