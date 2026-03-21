document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const resultCard = document.getElementById('result');
    const resultLabel = document.getElementById('result-label');
    const resultConfidence = document.getElementById('result-confidence');

    // Tab switching logic
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // Analyze button logic
    const analyzeButtons = {
        'url-analyze': '/predict-url',
        'email-analyze': '/predict-email',
        'scam-analyze': '/predict-scam',
        'job-analyze': '/predict-job'
    };

    Object.keys(analyzeButtons).forEach(buttonId => {
        document.getElementById(buttonId).addEventListener('click', async () => {
            const inputId = buttonId.replace('-analyze', '-input');
            const input = document.getElementById(inputId).value;
            const endpoint = analyzeButtons[buttonId];

            // Show loading spinner
            resultCard.classList.remove('red', 'green');
            resultCard.classList.add('hidden');
            resultLabel.textContent = 'Loading...';
            resultConfidence.textContent = '';
            resultCard.classList.remove('hidden');

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(buttonId === 'url-analyze' ? { url: input } : { text: input })
                });

                const data = await response.json();
                resultLabel.textContent = data.result;
                resultConfidence.textContent = `Confidence: ${data.confidence}%`;
                resultCard.classList.add(data.result === 'Legitimate' ? 'green' : 'red');
            } catch (error) {
                resultLabel.textContent = 'Error occurred';
                resultConfidence.textContent = '';
                resultCard.classList.add('red');
            }
        });
    });
});