document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const claimInput = document.getElementById('claimInput').value.trim();
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const errorBox = document.getElementById('errorBox');

    // Reset UI
    resultsDiv.classList.add('hidden');
    errorBox.classList.add('hidden');

    if (!claimInput) {
        errorBox.textContent = "Please enter a claim to analyze.";
        errorBox.classList.remove('hidden');
        return;
    }

    // Show loading spinner
    loadingDiv.classList.remove('hidden');

    try {
        // Send POST request to Flask backend
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim: claimInput })
        });

        const data = await response.json();

        if (!response.ok) throw new Error(data.error || "Server error occurred");

        // Populate results
        const verdictEl = document.getElementById('verdictTitle');
        verdictEl.textContent = `Verdict: ${data.verdict}`;
        
        // Color code verdict
        verdictEl.className = ''; 
        if (data.verdict === 'REAL') verdictEl.classList.add('text-success');
        else if (data.verdict === 'FAKE') verdictEl.classList.add('text-danger');
        else verdictEl.classList.add('text-warning');

        document.getElementById('tierBadge').textContent = `Resolved via: ${data.tier_used}`;
        document.getElementById('summaryText').textContent = data.summary;
        document.getElementById('explanationText').textContent = data.explanation;

        // Populate sources list
        const sourcesList = document.getElementById('sourcesList');
        sourcesList.innerHTML = '';
        data.sources.forEach(source => {
            const li = document.createElement('li');
            if (source.startsWith('http')) {
                li.innerHTML = `<a href="${source}" target="_blank">${source}</a>`;
            } else {
                li.textContent = source;
            }
            sourcesList.appendChild(li);
        });

        // Hide loading, show results
        loadingDiv.classList.add('hidden');
        resultsDiv.classList.remove('hidden');

    } catch (error) {
        loadingDiv.classList.add('hidden');
        errorBox.textContent = error.message;
        errorBox.classList.remove('hidden');
    }
});