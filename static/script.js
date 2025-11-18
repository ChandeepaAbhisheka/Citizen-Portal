// async function leadServices(){
//     const res = await fetch('/api/services');
//     const services = await res.json();
//     const div = document.getElementById('services');
//     div.innerHTML = '';
//     services.forEach(service => {
//         const p = document.createElement('p');
//         p.textContent = service.name;
//         div.appendChild(p);
//     });
// }
// window.onload = leadServices;

// -------------------------------------------------------------
// Global Variables
// -------------------------------------------------------------
let lang = "en";
let services = [];
let currentServiceName = "";

// -------------------------------------------------------------
// Load Services from Backend
// -------------------------------------------------------------
async function loadServices() {
    const res = await fetch("/api/services");
    services = await res.json();

    const list = document.getElementById("service-list");
    list.innerHTML = "";

    services.forEach(service => {
        const li = document.createElement("li");
        li.textContent = service.name[lang] || service.name.en;
        li.onclick = () => loadSubservices(service);
        list.appendChild(li);
    });
}

// -------------------------------------------------------------
// Language Switcher
// -------------------------------------------------------------
function setLang(l) {
    lang = l;
    loadServices();

    // Reset UI Panels
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("question-list").innerHTML = "";
    document.getElementById("answer-box").innerHTML = "";
}

// -------------------------------------------------------------
// Load Subservices
// -------------------------------------------------------------
function loadSubservices(service) {
    currentServiceName = service.name[lang] || service.name.en;

    const subList = document.getElementById("sub-list");
    subList.innerHTML = "";

    document.getElementById("sub-title").innerText = currentServiceName;

    (service.subservices || []).forEach(sub => {
        const li = document.createElement("li");
        li.textContent = sub.name[lang] || sub.name.en;
        li.onclick = () => loadQuestions(sub);
        subList.appendChild(li);
    });
}

// -------------------------------------------------------------
// Load Questions Under a Subservice
// -------------------------------------------------------------
function loadQuestions(sub) {
    const qList = document.getElementById("question-list");
    qList.innerHTML = "";

    document.getElementById("q-title").innerText =
        sub.name[lang] || sub.name.en;

    (sub.questions || []).forEach(q => {
        const li = document.createElement("li");
        li.textContent = q.q[lang] || q.q.en;
        li.onclick = () => showAnswer(q);
        qList.appendChild(li);
    });
}

// -------------------------------------------------------------
// Display Answer with Downloads, Location & Instructions
// -------------------------------------------------------------
function showAnswer(q) {
    let html = `
        <h3>${q.q[lang] || q.q.en}</h3>
        <p>${q.answer[lang] || q.answer.en}</p>
    `;

    // Downloads
    if (q.downloads && q.downloads.length > 0) {
        const links = q.downloads
            .map(file => `<a href="${file}" target="_blank">${file.split("/").pop()}</a>`)
            .join(", ");

        html += `<p><b>Downloads:</b> ${links}</p>`;
    }

    // Map / Location
    if (q.location) {
        html += `<p><b>Location:</b> 
                    <a href="${q.location}" target="_blank">View Map</a>
                 </p>`;
    }

    // Instructions
    if (q.instructions) {
        html += `<p><b>Instructions:</b> ${q.instructions}</p>`;
    }

    document.getElementById("answer-box").innerHTML = html;

    // ---------------------------------------------------------
    // Optional Engagement Prompt (Non-blocking)
    // ---------------------------------------------------------
    setTimeout(async () => {
        const age = prompt("Enter your age (optional):");
        const job = prompt("Enter your job (optional):");
        const desire = prompt("What is your main interest here (optional)?");

        await fetch("/api/engagement", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: null,
                age,
                job,
                desires: desire ? [desire] : [],
                question_clicked: q.q[lang] || q.q.en,
                service: currentServiceName
            })
        });
    }, 200);
}

// -------------------------------------------------------------
// Initialize Page
// -------------------------------------------------------------
window.onload = loadServices;

