const fetch = require('node-fetch');

const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL || 'https://stealth-tinko-prod-app-1762804410.azurewebsites.net';

module.exports = async function (context, req) {
    context.log('Health check API called');
    
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    };

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        context.res = {
            status: 200,
            headers: headers
        };
        return;
    }

    if (req.method !== 'GET') {
        context.res = {
            status: 405,
            headers: headers,
            body: JSON.stringify({ error: 'Method not allowed' })
        };
        return;
    }

    try {
        // Check backend health
        const response = await fetch(`${BACKEND_BASE_URL}/health`, {
            method: 'GET',
            timeout: 10000
        });
        
        const backendHealth = await response.json();
        
        const healthStatus = {
            status: 'healthy',
            timestamp: new Date().toISOString(),
            services: {
                swa: {
                    status: 'healthy',
                    version: '1.0.0'
                },
                backend: {
                    status: response.ok ? 'healthy' : 'unhealthy',
                    url: BACKEND_BASE_URL,
                    response: backendHealth
                }
            }
        };

        context.res = {
            status: 200,
            headers: headers,
            body: JSON.stringify(healthStatus)
        };
    } catch (error) {
        context.log.error('Health check failed:', error);
        
        context.res = {
            status: 503,
            headers: headers,
            body: JSON.stringify({
                status: 'unhealthy',
                timestamp: new Date().toISOString(),
                error: error.message,
                services: {
                    swa: {
                        status: 'healthy',
                        version: '1.0.0'
                    },
                    backend: {
                        status: 'unhealthy',
                        url: BACKEND_BASE_URL,
                        error: 'Connection failed'
                    }
                }
            })
        };
    }
};