from config import settings

import json
import requests


class BetonAPI:
    def __init__(self) -> None:
        self.url = settings.BETON_API_URL
        self.auth_token = settings.BETON_API_AUTH_TOKEN

    def sendRequest(self, method: str, url: str, data: dict = {}, headers: dict = {}) -> dict:
        """
        Sends request to Beton API.

        :param request_method: http request method (`get`, `post`, `patch`, `delete`).
        :param api_method: the required method in Beton API.
        """

        args = (url, data)
        kwargs = {'headers': headers}
        match method.upper():
            case 'GET': r = requests.get(*args, **kwargs)
            case 'POST': r = requests.post(*args, **kwargs)
            case 'PATCH': r = requests.patch(*args, **kwargs)
            case 'DELETE': r = requests.delete(*args, **kwargs)

        response = {
            'code': r.status_code,
            'text': r.text,
        }
        
        return response

    def getOrder(self, order_id: str) -> dict:
        endpoint_url = self.url + f'store/orders/{order_id}/'

        response = self.sendRequest('get', endpoint_url)
        response_data = json.loads(response['text'])
        
        order = response_data['details']['order']
        return order

    def getOrdersList(self, status: str = None) -> list:
        endpoint_url = self.url + 'store/orders/'

        data = {}
        if status:
            data['status'] = status

        response = self.sendRequest('get', endpoint_url, data)
        response_data = json.loads(response['text'])
        
        orders = response_data['details']['orders']
        return orders
