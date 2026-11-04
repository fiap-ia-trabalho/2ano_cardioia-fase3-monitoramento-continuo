import json

import requests


class RestClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def post_sample(self, sample):
        response = requests.post(
            f"{self.base_url}/samples",
            json=sample,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_latest_sample(self):
        response = requests.get(
            f"{self.base_url}/samples/latest",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_health(self):
        response = requests.get(
            f"{self.base_url}/health",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
