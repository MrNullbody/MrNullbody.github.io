import requests
import os
import traceback
import config
from bs4 import BeautifulSoup

log_dir = os.path.join(os.path.dirname(__file__), '..', 'log')

def beautiful_html(html_content: str):
    soup = BeautifulSoup(html_content, 'html5lib')
    beautified_html = soup.prettify()
    return beautified_html
    # return html_content

def compile(pathname: str, wrapper_before: str = '', wrapper_after: str = ''):
    with open(pathname, 'r') as f:
        data = f.readlines()

    index = -1

    for cur_index, line in enumerate(data):
        processed = ''.join(line.split())
        if processed.endswith(r'%preamble'):
            index = cur_index

    upload_data = {'code': '', 'preamble': ''}

    if index != -1:
        upload_data['code'] = '\n'.join(data[index + 1:])
        upload_data['preamble'] = '\n'.join(data[:index])
    else:
        upload_data['code'] = '\n'.join(data)

    error = None

    try:

        result = requests.post(config.btex_server_url, json = upload_data)

    except Exception as e:

        log_file = os.path.join(log_dir, 'compiler_error.txt')

        with open(log_file, 'w') as f:
            f.write(traceback.format_exc())

        error = f'Server connection error, log file written to {log_file}.'

    if error:
        raise Exception(error)

    if str(result.status_code) != '200':
        raise Exception(f'Server error. The returned status code is {result.status_code}.')

    # return beautiful_html(wrapper_before + result.json()['html'] + wrapper_after)
    return wrapper_before + result.json()['html'] + wrapper_after
