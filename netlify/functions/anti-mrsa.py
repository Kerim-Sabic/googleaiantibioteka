"""
Netlify Function: Anti-MRSA Drugs

Get all drugs with anti-MRSA activity
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

    try:
        drugs = registry.find_anti_mrsa()

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'success',
                'drugs': drugs,
                'count': len(drugs)
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }
