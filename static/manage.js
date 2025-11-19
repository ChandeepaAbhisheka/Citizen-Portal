// Load services on page load
window.onload = function() {
    loadServices();
};

// Fetch all services and show in table
async function loadServices() {
    const res = await fetch("/api/admin/services");
    const services = await res.json();

    let table = document.getElementById("services_table");
    table.innerHTML = "";

    services.forEach(s => {
        let row = `
            <tr>
                <td>${s.id}</td>
                <td>${s.name}</td>
                <td>${(s.questions || []).join(", ")}</td>
                <td>
                    <button onclick="editService('${s.id}', '${s.name}', '${(s.questions || []).join(", ")}')">Edit</button>
                    <button onclick="deleteService('${s.id}')">Delete</button>
                </td>
            </tr>
        `;
        table.innerHTML += row;
    });
}

// Fill form with selected data
function editService(id, name, questions) {
    document.getElementById("service_id").value = id;
    document.getElementById("service_name").value = name;
    document.getElementById("service_questions").value = questions;
}

// Save the service (CREATE or UPDATE)
async function saveService() {
    let id = document.getElementById("service_id").value;
    let name = document.getElementById("service_name").value;
    let questions = document.getElementById("service_questions").value.split(",");

    let payload = {
        id: id,
        name: name,
        questions: questions.map(q => q.trim())
    };

    const res = await fetch("/api/admin/services", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        alert("Saved successfully!");
        loadServices();
    } else {
        alert("Error saving service");
    }
}

// Delete a service
async function deleteService(id) {
    if (!confirm("Are you sure?")) return;

    const res = await fetch(`/api/admin/services/${id}`, {
        method: "DELETE"
    });

    if (res.ok) {
        alert("Deleted successfully!");
        loadServices();
    } else {
        alert("Error deleting service");
    }
}
