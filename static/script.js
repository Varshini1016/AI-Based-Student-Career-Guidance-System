document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prediction-form');
    const resultsContainer = document.getElementById('results-container');
    let featureChartInstance = null;
    
    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Predicting...';
        btn.disabled = true;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.status === 'success') {
                displayResults(result, data.student_skills);
                fetchAndRenderChart();
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Something went wrong. Please check if the server is running.');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });

    async function fetchAndRenderChart() {
        try {
            const res = await fetch('/feature_importance');
            const data = await res.json();
            if(data.status === 'success') {
                renderChart(data.labels, data.data);
            }
        } catch (err) {
            console.error("Failed to load chart", err);
        }
    }

    function renderChart(labels, dataPoints) {
        const ctx = document.getElementById('featureChart').getContext('2d');
        if (featureChartInstance) {
            featureChartInstance.destroy();
        }
        
        featureChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Feature Importance (%)',
                    data: dataPoints,
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#cbd5e1' }
                    },
                    x: {
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#cbd5e1' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc' } }
                }
            }
        });
    }

    function displayResults(data, userSkillsInput) {
        // Show container with animation
        resultsContainer.classList.remove('hidden');
        resultsContainer.classList.add('fade-in');
        
        // Update Career
        document.getElementById('res-career').innerText = data.career;
        
        // Update Confidence Bar
        document.getElementById('res-confidence-text').innerText = `${data.confidence}% Match`;
        setTimeout(() => {
            document.getElementById('res-confidence-fill').style.width = `${data.confidence}%`;
        }, 300);

        // Update Placement Probability (Circular Progress)
        document.getElementById('res-probability').style.background = `conic-gradient(var(--accent-color) ${data.placement_probability * 3.6}deg, rgba(255,255,255,0.1) 0deg)`;
        document.querySelector('.progress-value').innerText = `${data.placement_probability}%`;

        // Update Skill Gaps
        const skillList = document.getElementById('res-skill-gaps');
        skillList.innerHTML = '';
        const userSkillsStr = (userSkillsInput || '').toLowerCase();
        
        data.target_skills.forEach(skill => {
            const li = document.createElement('li');
            const hasSkill = userSkillsStr.includes(skill.toLowerCase());
            
            li.className = hasSkill ? 'skill-match' : 'skill-gap';
            li.innerHTML = `<span class="icon">${hasSkill ? '✓' : '✗'}</span> ${skill}`;
            skillList.appendChild(li);
        });

        // Update Learning Recommendations
        const learningList = document.getElementById('res-learning');
        learningList.innerHTML = '';
        data.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.innerText = rec;
            learningList.appendChild(li);
        });

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Resume Analyzer
    const resumeForm = document.getElementById('resume-form');
    resumeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('resume');
        if (!fileInput.files.length) return alert('Please select a file.');

        const btn = resumeForm.querySelector('button');
        btn.innerText = 'Analyzing...';
        
        const formData = new FormData();
        formData.append('resume', fileInput.files[0]);

        try {
            const response = await fetch('/analyze_resume', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            const resultDiv = document.getElementById('resume-result');
            
            if (result.status === 'success') {
                resultDiv.classList.remove('hidden');
                resultDiv.innerHTML = `<strong>Skills Extracted:</strong> ${result.skills_found.length > 0 ? result.skills_found.join(', ') : 'None identified.'}`;
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error(error);
        } finally {
            btn.innerText = 'Analyze';
        }
    });

    // Chatbot Logic
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotBody = document.getElementById('chatbot-body');
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat');
    const chatMessages = document.getElementById('chat-messages');

    chatbotToggle.addEventListener('click', () => {
        chatbotBody.classList.toggle('hidden');
        if (!chatbotBody.classList.contains('hidden')) {
            chatbotToggle.style.borderRadius = "16px 16px 0 0";
        } else {
            chatbotToggle.style.borderRadius = "16px";
        }
    });

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add user message
        addMessage(text, 'user');
        chatInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            addMessage(data.reply, 'bot');
        } catch (error) {
            addMessage('Error connecting to server.', 'bot');
        }
    }

    sendChatBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        div.innerText = text;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
