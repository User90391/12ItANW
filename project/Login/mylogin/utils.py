import requests

async def fetch_data_from_api(url, params=None, headers=None):
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Löst eine Exception bei HTTP-Fehlern aus
        return response.json()  # Antwort als JSON zurückgeben
    except requests.exceptions.RequestException as e:
        print(f"API-Fehler: {e}")
        return None

async def send_data_to_api(url, data=None, headers=None):
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API-Fehler: {e}")
        return None

async def get_all_organizations():
    url = "Base_URL/api/organizations"
    response_body = await fetch_data_from_api(url)
    limit = response_body.get("totalCount")
    params = {"limit":limit}
    response_body = await fetch_data_from_api(url,params)
    organizations = response_body.get("result")
    return organizations
