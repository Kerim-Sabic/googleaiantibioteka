// BAA-2025 Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Test API button
    const testApiBtn = document.getElementById('test-api-btn');
    const apiResponse = document.getElementById('api-response');

    if (testApiBtn) {
        testApiBtn.addEventListener('click', async function() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();

                apiResponse.classList.add('show');
                apiResponse.innerHTML = `
                    <h4>API Response:</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            } catch (error) {
                apiResponse.classList.add('show');
                apiResponse.innerHTML = `
                    <h4>Error:</h4>
                    <p style="color: red;">${error.message}</p>
                `;
            }
        });
    }
});
