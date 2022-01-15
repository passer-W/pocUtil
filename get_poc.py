import codecs
import configparser
import os

import requestUtil
import json
import re

file_image_pattern = r'(!\[.*?\]\(images/(.*?)\))'
file_image_pattern_2 = r'(<img src="images/(image-.*?.png)" alt=".*?".*?/>)'
file_image_pattern_3 = r'(<img src="(C.*?)" alt=".*?".*?/>)'
new_image_pattern = "![{name}]({remote})"

parser = configparser.ConfigParser()
parser.readfp(codecs.open('config.ini', "r", "utf-8"))
image_path = parser.get("SETTING", "image_path")
upload_url = parser.get("SETTING", "upload_url")
old_dir = parser.get("SETTING", "old_dir")
new_dir = parser.get("SETTING", "new_dir")
cookies = "Cookie: csrftoken=OntgEVPfP3m6YfduoL2Xpd5hTGerouw6D171qvSa5oK9PNOoMfuOKbtOA7L9Z93K; _ga=GA1.3.195620052.1631982405; sessionid=2ogtfyc4u7359aakeml9vp1cjpz14r6b"


def upload_image(image_name):
    if not "C:" in image_name:
        resp = requestUtil.post(upload_url, cookies=cookies, data={"name": image_name},
                                files={"file": open(image_path + image_name, "rb")})
    else:
        resp = requestUtil.post(upload_url, cookies=cookies, data={"name": "1.jpg"},
                                files={"file": open(image_name, "rb")})
    result = json.loads(resp.content.decode())
    remote_path = (result["url"])
    return remote_path


def get_o_poc(file_name):
    file = open(old_dir + file_name, "rb")
    poc_text = file.read().decode()
    file.close()
    return poc_text


def update_poc(file_name):
    print(f"\033[32m[START UPDATE] {file_name}\033[00m")
    old_poc = get_o_poc(file_name)
    new_file = open(new_dir + file_name, "wb")
    file_image_dict = {i[1]: i[0] for i in re.findall(file_image_pattern, old_poc)}
    file_image_dict_2 = {i[1]: i[0] for i in re.findall(file_image_pattern_2, old_poc)}
    file_image_dict_3 = {i[1]: i[0] for i in re.findall(file_image_pattern_3, old_poc)}
    file_image_dict = dict(file_image_dict, **file_image_dict_2, **file_image_dict_3)
    for k, v in file_image_dict.items():
        remote_path = upload_image(k)
        print(f"[UPLOAD SUCCESS] {k}")
        new_image = new_image_pattern.format(name=k, remote=remote_path)
        old_poc = old_poc.replace(v, new_image)
    while (old_poc.find(" ```") != -1):
        old_poc = old_poc.replace(" ```", "```")
    new_file.write(old_poc.encode())
    print(f"\033[33m[UPDATE SUCCESS] {file_name}\033[00m")


def upload_dir():
    for i in os.listdir(old_dir):
        if os.path.exists(new_dir + i):
            pass
        else:
            update_poc(i)


if __name__ == '__main__':
    upload_dir()
