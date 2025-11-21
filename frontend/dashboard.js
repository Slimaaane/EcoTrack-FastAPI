const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
let currentToken = null;
let currentUser = null;
let chart = null;

// ====================
// AUTHENTIFICATION
// ====================

function showLogin() {
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('signupForm').classList.add('hidden');
}

function showSignup() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.remove('hidden');
}

async function login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentToken = data.access_token;
            localStorage.setItem('token', currentToken);
            await loadUserProfile();
            showDashboard();
        } else {
            showMessage('authMessage', data.detail || 'Erreur de connexion', 'error');
        }
    } catch (error) {
        showMessage('authMessage', 'Erreur de connexion au serveur', 'error');
    }
}

async function signup() {
    const email = document.getElementById('signupEmail').value;
    const username = document.getElementById('signupUsername').value;
    const password = document.getElementById('signupPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                username: username,
                password: password,
                role: 'user'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('signupMessage', 'Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success');
            setTimeout(() => {
                document.getElementById('loginEmail').value = email;
                showLogin();
            }, 2000);
        } else {
            showMessage('signupMessage', data.detail || 'Erreur lors de l\'inscription', 'error');
        }
    } catch (error) {
        showMessage('signupMessage', 'Erreur de connexion au serveur', 'error');
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data;
            document.getElementById('userWelcome').textContent = `Bienvenue, ${data.username}`;
            document.getElementById('userRole').textContent = `Rôle: ${data.role}`;
        }
    } catch (error) {
        console.error('Erreur chargement profil:', error);
    }
}

function logout() {
    currentToken = null;
    currentUser = null;
    localStorage.removeItem('token');
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('dashboard').style.display = 'none';
    showLogin();
}

function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    setTimeout(() => {
        element.innerHTML = '';
    }, 5000);
}

// ====================
// DASHBOARD
// ====================

async function showDashboard() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    
    await Promise.all([
        loadZones(),
        loadSources(),
        loadStats(),
        loadIndicators()
    ]);
}

async function loadZones() {
    try {
        const response = await fetch(`${API_BASE_URL}/zones`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        const data = await response.json();
        
        const select = document.getElementById('filterZone');
        if (data.items && Array.isArray(data.items)) {
            data.items.forEach(zone => {
                const option = document.createElement('option');
                option.value = zone.id;
                option.textContent = zone.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erreur chargement zones:', error);
    }
}

async function loadSources() {
    try {
        const response = await fetch(`${API_BASE_URL}/sources`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        const data = await response.json();
        
        const select = document.getElementById('filterSource');
        if (data.items && Array.isArray(data.items)) {
            data.items.forEach(source => {
                const option = document.createElement('option');
                option.value = source.id;
                option.textContent = source.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erreur chargement sources:', error);
    }
}

async function loadStats() {
    try {
        // Compter les zones
        const zonesResponse = await fetch(`${API_BASE_URL}/zones`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const zones = await zonesResponse.json();
        document.getElementById('totalZones').textContent = zones.total || 0;
        
        // Compter les sources
        const sourcesResponse = await fetch(`${API_BASE_URL}/sources`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const sources = await sourcesResponse.json();
        document.getElementById('totalSources').textContent = sources.total || 0;
        
        // Stats indicateurs
        const type = document.getElementById('filterType').value;
        const zone = document.getElementById('filterZone').value;
        const source = document.getElementById('filterSource').value;
        
        let indicatorsUrl = `${API_BASE_URL}/indicators?limit=1`;
        if (type) indicatorsUrl += `&type=${type}`;
        if (zone) indicatorsUrl += `&zone_id=${zone}`;
        if (source) indicatorsUrl += `&source_id=${source}`;
        
        const indicatorsResponse = await fetch(indicatorsUrl, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const indicators = await indicatorsResponse.json();
        
        document.getElementById('totalIndicators').textContent = indicators.total || 0;
        
        // Calculer la moyenne si on a des données
        if (indicators.items && indicators.items.length > 0) {
            // Faire une requête pour obtenir toutes les valeurs (max 1000)
            let avgUrl = `${API_BASE_URL}/indicators?limit=1000`;
            if (type) avgUrl += `&type=${type}`;
            if (zone) avgUrl += `&zone_id=${zone}`;
            if (source) avgUrl += `&source_id=${source}`;
            
            const avgResponse = await fetch(avgUrl, {
                headers: { 'Authorization': `Bearer ${currentToken}` }
            });
            const avgData = await avgResponse.json();
            
            if (avgData.items && avgData.items.length > 0) {
                const sum = avgData.items.reduce((acc, ind) => acc + parseFloat(ind.value), 0);
                const avg = sum / avgData.items.length;
                document.getElementById('avgValue').textContent = avg.toFixed(2);
            } else {
                document.getElementById('avgValue').textContent = '-';
            }
        } else {
            document.getElementById('avgValue').textContent = '-';
        }
        
    } catch (error) {
        console.error('Erreur chargement stats:', error);
    }
}

async function loadIndicators() {
    const tbody = document.getElementById('indicatorsBody');
    const loading = document.getElementById('loadingIndicators');
    
    loading.classList.remove('hidden');
    tbody.innerHTML = '';
    
    try {
        // Construire l'URL avec filtres
        const type = document.getElementById('filterType').value;
        const zone = document.getElementById('filterZone').value;
        const source = document.getElementById('filterSource').value;
        const limit = document.getElementById('filterLimit').value;
        
        let url = `${API_BASE_URL}/indicators?limit=${limit}`;
        if (type) url += `&type=${type}`;
        if (zone) url += `&zone_id=${zone}`;
        if (source) url += `&source_id=${source}`;
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        const data = await response.json();
        
        if (!data.items || data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">Aucun indicateur trouvé</td></tr>';
        } else {
            data.items.forEach(indicator => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${indicator.id}</td>
                    <td><span style="background: #667eea; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em;">${indicator.type}</span></td>
                    <td>${indicator.name}</td>
                    <td><strong>${indicator.value}</strong></td>
                    <td>${indicator.unit}</td>
                    <td>${new Date(indicator.timestamp).toLocaleString('fr-FR')}</td>
                    <td>${indicator.zone_id}</td>
                    <td>${indicator.source_id}</td>
                `;
                tbody.appendChild(row);
            });
            
            // Charger le graphique avec ces données
            loadChart(data.items);
        }
        
        // Recharger les stats
        await loadStats();
        
    } catch (error) {
        console.error('Erreur chargement indicateurs:', error);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px; color: red;">Erreur de chargement</td></tr>';
    } finally {
        loading.classList.add('hidden');
    }
}

function loadChart(data) {
    const ctx = document.getElementById('chart');
    
    if (chart) {
        chart.destroy();
    }
    
    // Regrouper par date
    const dateMap = new Map();
    data.forEach(indicator => {
        const date = new Date(indicator.timestamp).toLocaleDateString('fr-FR');
        if (!dateMap.has(date)) {
            dateMap.set(date, []);
        }
        dateMap.get(date).push(indicator.value);
    });
    
    // Calculer la moyenne par date
    const labels = Array.from(dateMap.keys()).slice(0, 10);
    const values = labels.map(date => {
        const vals = dateMap.get(date);
        return vals.reduce((a, b) => a + b, 0) / vals.length;
    });
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Valeur moyenne',
                data: values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// ====================
// INITIALISATION
// ====================

window.addEventListener('DOMContentLoaded', () => {
    // Vérifier si un token existe
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
        currentToken = savedToken;
        loadUserProfile().then(() => {
            showDashboard();
        }).catch(() => {
            localStorage.removeItem('token');
            showLogin();
        });
    } else {
        showLogin();
    }
});
