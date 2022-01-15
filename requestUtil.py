import codecs
import re
import configparser

import requests
import warnings

from urllib3 import encode_multipart_formdata

warnings.filterwarnings("ignore")

parser = configparser.ConfigParser()
parser.readfp(codecs.open('config.ini', "r", "utf-8"))
csrf_token = parser.get("SETTING", "csrf_token")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "x-csrftoken": f"{csrf_token}",
    "Connection": "close",
    "Referer": "https://src.sjtu.edu.cn/add/",
    "Cookie": f"csrftoken={csrf_token}; _ga=GA1.3.195620052.1631982405; sessionid=2ogtfyc4u7359aakeml9vp1cjpz14r6b"
}


def get_cookies(cookie_str):
    cookie_dict = {i.split("=")[0].strip(): "=".join(i.split("=")[1:]).strip() for i in cookie_str.split(";")}
    return cookie_dict


def get(url, cookies="", header=None, timeout=10, session=""):
    f_headers = dict.copy(headers)
    if cookies == "":
        cookies = {}
    else:
        cookies = get_cookies(cookies)
    if header == None:
        header = {}
    f_headers = dict(f_headers, **header)
    try:
        if session == "":
            resp = requests.get(url, verify=False, headers=f_headers, cookies=cookies, timeout=timeout)
        else:
            resp = session.get(url, cookies=cookies, headers=f_headers, verify=False, timeout=timeout)
        if not b"<title>" in resp.content[:400] and b"<meta http-equiv=" in resp.content[:200].lower():
            try:
                if session == "":
                    resp = requests.get(
                        url + "/" + re.findall(r"<meta http-equiv=.*?content=.*?url=(.*?)>", resp.text.lower())[
                            0].replace('"', ""), cookies=cookies, headers=f_headers, verify=False, timeout=timeout)
                else:
                    resp = session.get(
                        url + "/" + re.findall(r"<meta http-equiv=.*?content=.*?url=(.*?)>", resp.text.lower())[
                            0].replace('"', ""), cookies=cookies, headers=f_headers, verify=False, timeout=timeout)
            except:
                pass
        return resp
    except Exception as e:
        return None


def post(url, data="", cookies="", header=None, timeout=10, session="", files=None):
    f_headers = dict.copy(headers)
    if cookies == "":
        cookies = {}
    else:
        cookies = get_cookies(cookies)
    if header == None:
        header = {}
    if not "Content-Type" in header and not files:
        header = dict(header, **{"Content-Type": "application/x-www-form-urlencoded"})
    if files == None:
        files = {}
    f_headers = dict(f_headers, **header)
    try:
        if session == "":
            resp = requests.post(url, cookies=cookies, data=data, headers=f_headers, verify=False, timeout=timeout,
                                 files=files)
        else:
            resp = session.post(url, cookies=cookies, data=data, headers=f_headers, verify=False, timeout=timeout,
                                files=files)
        return resp
    except Exception as e:
        print(e)
        return None


def get_file_data(filename, filedata, param="file", data=None):  # param: 上传文件的POST参数名
    if not data:
        data = {}
    data[param] = (filename, filedata)  # 名称，文件内容
    encode_data = encode_multipart_formdata(data)
    file_data = {
        "header": {
            'Content-Type': encode_data[1]
        },
        "data": encode_data[0]
    }
    return file_data


def session():
    return requests.session()
