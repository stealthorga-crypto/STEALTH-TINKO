const jwt = require('jsonwebtoken');
const fetch = require('node-fetch');

const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL || 'https://stealth-tinko-prod-app-1762804410.azurewebsites.net';
const JWT_SECRET = process.env.JWT_SECRET || 'your-super-secret-jwt-key';

module.exports = async function (context, req) {
    context.log('Auth validation API called');
    
    const headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
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

    if (req.method !== 'POST') {
        context.res = {
            status: 405,
            headers: headers,
            body: JSON.stringify({ error: 'Method not allowed' })
        };
        return;
    }

    try {
        const { token } = req.body;
        
        if (!token) {
            context.res = {
                status: 400,
                headers: headers,
                body: JSON.stringify({ 
                    error: 'Token is required',
                    valid: false 
                })
            };
            return;
        }

        // Verify JWT token locally
        let decoded;
        try {
            decoded = jwt.verify(token, JWT_SECRET);
        } catch (jwtError) {
            context.res = {
                status: 401,
                headers: headers,
                body: JSON.stringify({ 
                    error: 'Invalid token',
                    valid: false 
                })
            };
            return;
        }

        // Optional: Verify with backend for additional validation
        try {
            const response = await fetch(`${BACKEND_BASE_URL}/auth/verify-token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ token }),
                timeout: 5000
            });

            if (response.ok) {
                const backendValidation = await response.json();
                
                context.res = {
                    status: 200,
                    headers: headers,
                    body: JSON.stringify({
                        valid: true,
                        user: decoded,
                        backend_validation: backendValidation
                    })
                };
            } else {
                context.res = {
                    status: 401,
                    headers: headers,
                    body: JSON.stringify({ 
                        error: 'Backend validation failed',
                        valid: false 
                    })
                };
            }
        } catch (backendError) {
            // If backend is down, still trust local JWT validation
            context.log.warn('Backend validation failed, using local validation:', backendError.message);
            
            context.res = {
                status: 200,
                headers: headers,
                body: JSON.stringify({
                    valid: true,
                    user: decoded,
                    note: 'Backend validation unavailable, using local JWT validation'
                })
            };
        }
    } catch (error) {
        context.log.error('Auth validation error:', error);
        
        context.res = {
            status: 500,
            headers: headers,
            body: JSON.stringify({
                error: 'Internal server error',
                valid: false
            })
        };
    }
};