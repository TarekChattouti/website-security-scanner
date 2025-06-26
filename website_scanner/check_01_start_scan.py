def run(url, resp=None):
    return {
        'name': 'Start scan',
        'status': 'pass',
        'description': 'Scan started',
        'evidence': url,
        'risk': 1  # Info only
    }
