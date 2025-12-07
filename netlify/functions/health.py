"""
Netlify Function: Health Check (Simplified)

Simple health check that doesn't require external dependencies
"""

import json


def handler(event, context):
    """Netlify Function handler"""

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Content-Type': 'application/json'
    }

    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    # Return health status
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'status': 'healthy',
            'service': 'BAA-2025',
            'version': '1.0.0',
            'platform': 'Netlify Functions (Python)',
            'message': 'API is running. Full drug registry available.',
            'note': 'This is a simplified health check. Full functionality requires proper deployment.'
        })
    }
