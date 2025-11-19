// =============================================================
// LOGIN HANDLING
// =============================================================
document.getElementById("login-form").onsubmit = async (e) => {
    e.preventDefault();

    const form = new FormData(e.target);
    const res = await fetch('/admin/login', {
        method: 'POST',
        body: form
    });

    // If express redirects
    if (res.redirected) {
        window.location = res.url;
    } else {
        loadDashboard();
    }
};



// =============================================================
// LOAD DASHBOARD AFTER LOGIN
// =============================================================
async function loadDashboard() {
    const dashboardEl = document.getElementById("dashboard");

    try {
        const r = await fetch('/api/admin/insights');

        // Not logged in
        if (r.status === 401) {
            document.getElementById("login-box").style.display    = "block";
            dashboardEl.style.display                             = "none";
            return;
        }

        const data = await r.json();

        // Logged in → show dashboard
        document.getElementById("login-box").style.display = "none";
        dashboardEl.style.display = "block";



        // =============================================================
        // CHARTS
        // =============================================================

        // Age Group Chart
        new Chart(document.getElementById("ageChart"), {
            type: 'bar',
            data: {
                labels: Object.keys(data.age_groups),
                datasets: [
                    { label: "Users", data: Object.values(data.age_groups) }
                ]
            }
        });

        // Jobs Pie Chart
        new Chart(document.getElementById("jobChart"), {
            type: 'pie',
            data: {
                labels: Object.keys(data.jobs),
                datasets: [
                    { label: "Jobs", data: Object.values(data.jobs) }
                ]
            }
        });

        // Services Doughnut Chart
        new Chart(document.getElementById("serviceChart"), {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.services),
                datasets: [
                    { label: "Services", data: Object.values(data.services) }
                ]
            }
        });

        // Top Questions Chart
        new Chart(document.getElementById("questionChart"), {
            type: 'bar',
            data: {
                labels: Object.keys(data.questions).slice(0, 10),
                datasets: [
                    {
                        label: "Top Questions",
                        data: Object.values(data.questions).slice(0, 10)
                    }
                ]
            }
        });



        // =============================================================
        // PREMIUM LIST
        // =============================================================
        const pl = document.getElementById("premiumList");

        pl.innerHTML = data.premium_suggestions.length
            ? data.premium_suggestions
                .map(p => `
                    <div>
                        User: ${p.user} <br>
                        Question: ${p.question} <br>
                        Count: ${p.count}
                    </div>
                `)
                .join("")
            : "<div>No suggestions</div>";



        // =============================================================
        // ENGAGEMENT TABLE
        // =============================================================
        const resEng = await fetch('/api/admin/engagements');
        const items  = await resEng.json();

        const tbody = document.querySelector("#engTable tbody");
        tbody.innerHTML = "";

        items.forEach(it => {
            const row = `
                <tr>
                    <td>${it.age || ""}</td>
                    <td>${it.job || ""}</td>
                    <td>${(it.desires || []).join(", ")}</td>
                    <td>${it.question_clicked || ""}</td>
                    <td>${it.service || ""}</td>
                    <td>${it.timestamp || ""}</td>
                </tr>
            `;

            tbody.insertAdjacentHTML('beforeend', row);
        });

    } catch (err) {
        console.error(err);
    }
}



// =============================================================
// LOGOUT BUTTON
// =============================================================
document.getElementById("logoutBtn")?.addEventListener("click", async () => {
    await fetch('/api/admin/logout', { method: "POST" });
    window.location = "/admin";
});



// =============================================================
// EXPORT CSV
// =============================================================
document.getElementById("exportCsv")?.addEventListener("click", () => {
    window.location = '/api/admin/export_csv';
});



// =============================================================
// INITIAL LOAD
// =============================================================
window.onload = loadDashboard;
