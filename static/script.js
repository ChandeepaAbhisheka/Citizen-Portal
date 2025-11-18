async function leadServices(){
    const res = await fetch('/api/services');
    const services = await res.json();
    const div = document.getElementById('services');
    div.innerHTML = '';
    services.forEach(service => {
        const p = document.createElement('p');
        p.textContent = service.name;
        div.appendChild(p);
    });
}
window.onload = leadServices;
    