import requests


class RestClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, headers):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=headers)

        # Get response status code
        status_code = response.status_code

        # Check if response status is OK (200)
        if response.ok:
            # Parse JSON response body
            try:
                json_data = response.json()
                return status_code, json_data
            except ValueError:
                return status_code, None
        else:
            # If response status is not OK, return None for JSON data
            return status_code, None

    def post(self, endpoint, headers, payload):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, headers=headers, data=payload)

        # Get response status code
        status_code = response.status_code

        # Check if response status is OK (200)
        if response.ok:
            # Parse JSON response body
            try:
                json_data = response.json()
                return status_code, json_data
            except ValueError:
                return status_code, "VALUE ERROR"
        else:
            # If response status is not OK, return None for JSON data
            return status_code, "ERROR"
