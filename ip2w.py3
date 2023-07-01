#!/usr/bin/python3

import json
import logging
import os
import re
from configparser import ConfigParser
from typing import Union, Tuple

import requests

CONFIG: str = "/usr/local/etc/ip2w.ini"

OK: int = 200
BAD_REQUEST: int = 400
INTERNAL_ERROR: int = 500

WEATHER_API_KEY: str = os.environ.get('WEATHER_API_KEY', '')


def is_valid_ip(ip_string: str) -> bool:
    pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"  # Regex pattern for a correct IP address
    return bool(re.match(pattern, ip_string))

def process_request(env: dict, config: dict) -> Tuple[int, Union[dict, str]]:
    code, ip = get_ip(env)
    if code != OK:
        return code, ip
    code, city = get_location_by_ip(ip)
    if code != OK:
        return code, city
    code, weather = get_weather_by_location(city)
    return code, weather


def get_ip(env: dict) -> Tuple[int, str]:
    try:
        ip = env['PATH_INFO']
        ip = ip.split('/')[-1]
        # logging.info(f"Got IP: {ip}")
        if not is_valid_ip(ip):
            return BAD_REQUEST, 'Invalid IP address'
        return OK, ip
    except KeyError:
        return BAD_REQUEST, 'PATH_INFO key error: bad configuration'


def get_location_by_ip(ip: str) -> Tuple[int, str]:
    try:
        url = f"https://ipinfo.io/{ip}"
        response = requests.get(url)
        response = response.json()
        if 'city' in response:
            return OK, response['city']
    except requests.RequestException:
        return INTERNAL_ERROR, "An exception occured during IP attribution"
    return INTERNAL_ERROR, "Other exception"


def get_weather_by_location(city: str) -> Tuple[int, Union[dict, str]]:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=en&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()
        result_code = int(response["cod"])
        if result_code == OK:
            temp = str(response["main"]["temp"])
            conditions = ", ".join([cond["description"] for cond in response["weather"]])
            result = {
                "city": response["name"],
                "temp": temp,
                "conditions": conditions
            }
            return OK, result
        else:
            return result_code, response["message"]
    except requests.RequestException:
        return INTERNAL_ERROR, "Unsuccessful request to weather server"


def application(env, start_response):
    config = ConfigParser()
    config.read(CONFIG)
    config = dict(config["ip2w"])

    handler = logging.FileHandler(filename=config['log'], encoding='utf-8')
    logging.basicConfig(
        handlers=[handler], level=logging.INFO,
        format='%(asctime)s %(levelname)s {%(pathname)s:%(lineno)d}: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logging.info(f"Request for IP: {env['PATH_INFO']} from {env['REMOTE_ADDR']}")

    global WEATHER_API_KEY
    # logging.info(f"API_KEY: {WEATHER_API_KEY} / {os.environ['WEATHER_API_KEY']} - before reading")
    # logging.info(f"All env: {os.environ}")
    logging.info(f"dict env: {env}")
    if not WEATHER_API_KEY:
        WEATHER_API_KEY = config['weather_api_key']
    logging.info(f"API_KEY: {WEATHER_API_KEY} - after reading")
    code, response = process_request(env, config)
    logging.info("Response: {}, {}".format(code, response))
    if not isinstance(response, str):
        response = json.dumps(response, indent="\t", ensure_ascii=False)  #
    response = response.encode(encoding="utf-8")

    start_response(str(code), [
        ('Content-Type', 'application/json; charset=UTF-8'),
        ('Content-Length', str(len(response))),
    ])
    return [response]


if __name__ == "__main__":
    # dev
    CONFIG: str = 'ip2w_dev.ini'
    env: dict = dict()
    env['PATH_INFO'] = '/ip2w/195.69.81.52'
    env['REMOTE_ADDR'] = '127.0.0.1'
    print(application(env, print))
