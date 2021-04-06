from fake_useragent import UserAgent
import requests
from time import sleep


def get_requests(url, is_stream=False, cookies=None):
    retry_count = 1
    while retry_count < 6:
        try:
            html = requests.get(url, headers={'User-Agent': UserAgent().random}, stream=is_stream, cookies=cookies)
            if html.status_code == 200 or html.status_code == 404:
                return html
            sleep(retry_count * 2)
            retry_count += 1
        except Exception as ex:
            print(f"get_requests Exception {ex}")
            retry_count += 1
            if retry_count == 6:
                raise ex
