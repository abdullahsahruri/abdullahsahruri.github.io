---
layout: page
title: Conference Deadlines
subtitle: Automatically updated conference submission deadlines
---

<div class="search-filter-section" style="margin-bottom: 2rem;">
    <input type="text" id="searchBox" placeholder="🔍 Search conferences..."
           style="width: 100%; max-width: 400px; padding: 0.75rem; border: 2px solid var(--border-color); border-radius: 5px; font-size: 1rem; margin-bottom: 1rem;">

    <div class="filter-buttons" style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
        <button class="btn" onclick="filterTable('all')" style="background: var(--primary-color);">All</button>
        <button class="btn btn-secondary" onclick="filterTable('2025')">2025</button>
        <button class="btn btn-secondary" onclick="filterTable('2026')">2026</button>
        <button class="btn btn-secondary" onclick="filterTable('upcoming')">Upcoming Deadlines</button>
    </div>
</div>

<div id="tableContainer">
    <p style="text-align: center; padding: 40px; color: var(--text-light);">
        <em>Loading conference data...</em>
    </p>
</div>

<p style="text-align: right; color: var(--text-light); font-size: 0.9em; margin-top: 1.5rem; font-style: italic;" id="lastUpdated">
    Last updated: Loading...
</p>

<script>
// Load conference data from JSON
async function loadConferences() {
    try {
        const response = await fetch('/assets/conference_database.json');
        const data = await response.json();

        displayConferences(data);
        setupSearch(data);
    } catch (error) {
        document.getElementById('tableContainer').innerHTML =
            '<p style="color: var(--accent-color); text-align: center;">Error loading conference data. Please check back later.</p>';
        console.error('Error:', error);
    }
}

function displayConferences(data) {
    const conferences = Object.values(data);
    const now = new Date();
    const oneWeek = 7 * 24 * 60 * 60 * 1000;

    // Sort by deadline status: upcoming first, then soon, then expired
    conferences.sort((a, b) => {
        const dateA = new Date(a.paper_deadline || '9999-12-31');
        const dateB = new Date(b.paper_deadline || '9999-12-31');
        const diffA = dateA - now;
        const diffB = dateB - now;

        // Categorize: 0=upcoming, 1=soon (within week), 2=expired
        const categoryA = diffA < 0 ? 2 : (diffA < oneWeek ? 1 : 0);
        const categoryB = diffB < 0 ? 2 : (diffB < oneWeek ? 1 : 0);

        if (categoryA !== categoryB) {
            return categoryA - categoryB;
        }
        return dateA - dateB;
    });

    let html = `
        <table class="conference-table" id="confTable">
            <thead>
                <tr>
                    <th>Conference</th>
                    <th>Paper Deadline</th>
                    <th>Type</th>
                    <th>Website</th>
                    <th>Last Checked</th>
                </tr>
            </thead>
            <tbody>
    `;

    conferences.forEach(conf => {
        const deadline = conf.paper_deadline || 'TBD';
        const submissionType = conf.submission_type || 'Regular Paper';
        const lastChecked = conf.last_checked ? conf.last_checked.split('T')[0] : 'N/A';
        const url = conf.url || '#';
        const urlDisplay = url.length > 50 ? url.substring(0, 50) + '...' : url;

        // Calculate deadline status for highlighting
        let rowStyle = '';
        if (deadline !== 'TBD') {
            const deadlineDate = new Date(deadline);
            const timeDiff = deadlineDate - now;

            if (timeDiff < 0) {
                // Expired - red background
                rowStyle = 'background-color: #ffcdd2;';
            } else if (timeDiff < oneWeek) {
                // Soon - yellow background
                rowStyle = 'background-color: #fff9c4;';
            }
        }

        html += `
            <tr style="${rowStyle}" data-conference="${conf.name.toLowerCase()}" data-deadline="${deadline}">
                <td style="font-weight: 600;">${conf.name}</td>
                <td style="color: var(--accent-color); font-weight: 600;">${deadline}</td>
                <td>${submissionType}</td>
                <td><a href="${url}" target="_blank">${urlDisplay}</a></td>
                <td>${lastChecked}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    document.getElementById('tableContainer').innerHTML = html;
    document.getElementById('lastUpdated').textContent =
        `Last updated: ${new Date().toLocaleDateString()} | Total conferences: ${conferences.length}`;
}

function setupSearch(data) {
    const searchBox = document.getElementById('searchBox');
    searchBox.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = document.querySelectorAll('#confTable tbody tr');

        rows.forEach(row => {
            const confName = row.dataset.conference;
            if (confName.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

function filterTable(filter) {
    const rows = document.querySelectorAll('#confTable tbody tr');
    const buttons = document.querySelectorAll('.filter-buttons .btn');

    // Update active button
    buttons.forEach(btn => {
        if (btn.onclick && btn.onclick.toString().includes(`'${filter}'`)) {
            btn.style.background = 'var(--primary-color)';
            btn.classList.remove('btn-secondary');
        } else {
            btn.style.background = 'var(--accent-color)';
            btn.classList.add('btn-secondary');
        }
    });

    const now = new Date();

    rows.forEach(row => {
        const confName = row.dataset.conference;
        const deadline = row.dataset.deadline;
        const deadlineDate = new Date(deadline);

        let show = false;

        switch(filter) {
            case 'all':
                show = true;
                break;
            case '2025':
                show = confName.includes('2025');
                break;
            case '2026':
                show = confName.includes('2026');
                break;
            case 'upcoming':
                show = deadlineDate > now;
                break;
        }

        row.style.display = show ? '' : 'none';
    });
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', loadConferences);
</script>
