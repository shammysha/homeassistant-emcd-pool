import json

class EMCDAPIException(Exception):

    def __init__(self, response, status_code, text):
        self.error = ''
        try:
            json_res = json.loads(text)
            self.status_code = json_res.get("code", "")
            self.description = json_res.get("message", "")            
        except ValueError:
            self.message = f"Response: {response}; Status Code: {status_code}; Message: {text}"

        self.status_code = status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return f'APIError(code={self.status_code}): {self.error} - {self.description}'
