# -*- coding: utf-8 -*-
"""
测试版：企查查 bigsearch/recruit 招聘接口
- 用浏览器 Cookie + window.pid + window.tid
- 调用 02_企查查_header加密逻辑.js 里的 main 生成 i/u
- 发送 GET https://www.qcc.com/api/bigsearch/recruit

关键：GET 请求的 path 必须包含完整 query 并整体小写，data 传空对象 {}
"""
﻿# author：人生如寄
# date：2026/02/28
# description：企查查“查招聘”网站关键词搜索结果显示
# note：需要填写自己的账号cookie

import execjs
import requests
from lxml import etree
import re
from urllib.parse import urlencode
from encode_url import encode_url_chinese


# 读取并编译精简版加密 JS
with open("02_企查查_header加密逻辑.js", "r", encoding="utf-8") as f:
    js_code = f.read()
js_exec = execjs.compile(js_code)

session = requests.Session()


def get_window_pid(cookie: str, key_word: str) -> tuple[str, str]:
    """访问 recruit 页面，获取 encode 后的 URL 和 window.pid"""
    base_page_url = "https://www.qcc.com/web/bigsearch/recruit?searchKey="
    page_url = base_page_url + key_word
    encode_page_url = encode_url_chinese(page_url)
    print("页面 URL 编码后：", encode_page_url)

    main_header = {
        "cookie": cookie,
        "referer": encode_page_url,
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"
        ),
    }

    resp = session.get(page_url, headers=main_header, timeout=10)
    tree = etree.HTML(resp.text)
    script_text = tree.xpath("/html/body/script[1]/text()")[0]
    script_text = script_text.split(";")[0]
    print("正则准备提取：", script_text)

    result = re.search(r"window\.pid='(.*?)'", script_text)
    window_pid = result.group(1)
    print("提取成功 window.pid =", window_pid)
    return encode_page_url, window_pid


def gen_i_u(path: str, params: dict, tid: str, is_get: bool = True) -> dict:
    """
    调用 JS 的 main 生成 {i, u}
    GET 请求：path 必须带完整 query 并小写，data 传 {}
    """
    if is_get and params:
        # 与 new_qichacha 433912 一致：params 按 key 排序后拼到 path 上，整体小写
        qs = urlencode(sorted(params.items()))
        full_path = f"{path}?{qs}".lower()
        data = {}
    else:
        full_path = path.lower()
        data = params

    e = {
        "url": full_path,
        "baseURL": "https://www.qcc.com",
        "data": data,
        "tid": tid,
        "headers": {}
    }
    return js_exec.call("main", e)


def main():
    # 1. 粘贴当前浏览器 recruit 页面的 Cookie
    cookie = input("请粘贴当前浏览器页面的 Cookie: ").strip()

    # 2. 粘贴浏览器控制台 window.tid 的值
    tid = input("请在浏览器控制台执行 window.tid 并粘贴结果: ").strip()

    # 3. 输入搜索关键字
    key_word = input("搜索关键字: ").strip()

    # 4. 静态页面获取 window.pid
    encode_page_url, window_pid = get_window_pid(cookie, key_word)

    # 5. 组装 bigsearch/recruit 查询参数（可按需要修改）
    params = {
        "city": "",
        "companyscale": "",
        "education": "",
        "experience": "",
        "fromTime": "",
        "industry": "",
        "isExcludeList": "false",
        "isFromDetail": "false",
        "isFromSingleApp": "true",
        "isSortAsc": "false",
        "pageSize": 20,
        "salary": "",
        "searchKey": key_word,
        "sortField": "publishtime",
        "toTime": "",
    }

    # 6. 先打印一份 JS 生成的 i/u，方便和浏览器对比
    print("------------- 生成签名 i/u -------------")
    sign = gen_i_u("/api/bigsearch/recruit", params, tid)
    print(sign)  # {'i': '...', 'u': '...'}

    # 7. 组装请求头（按你抓包的头来）
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "cookie": cookie,
        "origin": "https://www.qcc.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": encode_page_url,
        "sec-ch-ua": '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"
        ),
        "x-pid": window_pid,
        "x-requested-with": "XMLHttpRequest",
    }

    # 把 i/u 放进 headers
    headers[sign["i"]] = sign["u"]

    # 8. 发送 GET 请求
    print("------------- 发送 bigsearch/recruit 请求 -------------")
    try:
        resp = session.get(
            "https://www.qcc.com/api/bigsearch/recruit",
            headers=headers,
            params=params,
            timeout=15,
        )
        print("状态码:", resp.status_code)
        print("响应头:", resp.headers)
        print("响应内容:", resp.text)
    except Exception as e:
        print("请求失败:", str(e))


if __name__ == "__main__":

    main()
