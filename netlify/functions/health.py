"""
Netlify Function: Health Check

Check if API is healthy and registry loaded
"""

import json
import sys
from pathlib import Path

function_dir = Path(__file__).parent
project_root = function_dir.parent.parent
sys.path.insert(0, str(project_root))

from app.services.drug_registry import DrugRegistry

REGISTRY_PATH = project_root / "data" / "registry"
registry = DrugRegistry(REGISTRY_PATH)


def handler(event, context):
    """Netlify Function handler"""

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Content-Type': 'application/json'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'status': 'healthy',
            'service': 'BAA-2025',
            'version': '1.0.0',
            'platform': 'Netlify Functions',
            'registry_loaded': len(registry._drugs) > 0,
            'drug_count': len(registry._drugs)
        })
    }
