# -*- coding: utf-8 -*-
"""
测试版：企查查 bigsearch/recruit 招聘接口
- 支持城市筛选（如上海 city=3101）、每页条数（如 pageSize=40）、翻页（pageIndex）
- 用浏览器 Cookie + window.pid + window.tid 调用 02_企查查_header加密逻辑.js 生成 i/u
- 关键：GET 的 path 必须包含完整 query 并整体小写，data 传空对象 {}
"""

import execjs
import requests
from lxml import etree
import re
import json
import time
from urllib.parse import urlencode
from encode_url import encode_url_chinese

# 常用城市 code（可按需补充）
CITY_CODES = {
    "上海": "3101",
    "北京": "1101",
    "广州": "4401",
    "深圳": "4403",
    "杭州": "3301",
    "": "",  # 不限
}


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


def build_params(key_word: str, city_code: str = "3101", page_size: int = 40, page_index: int = 1) -> dict:
    """组装 bigsearch/recruit 查询参数。第一页不传 pageIndex（与浏览器一致），从第 2 页起传 pageIndex。"""
    params = {
        "city": city_code,
        "companyscale": "",
        "education": "",
        "experience": "",
        "fromTime": "",
        "industry": "",
        "isExcludeList": "false",
        "isFromDetail": "false",
        "isFromSingleApp": "true",
        "isSortAsc": "false",
        "pageSize": page_size,
        "salary": "",
        "searchKey": key_word,
        "sortField": "publishtime",
        "toTime": "",
    }
    if page_index > 1:
        params["pageIndex"] = page_index  # 与前端一致，数字即可，urlencode 会转成字符串
    return params


def fetch_one_page(
    session: requests.Session,
    params: dict,
    cookie: str,
    tid: str,
    window_pid: str,
    encode_page_url: str,
    page_index: int = 1,
) -> dict:
    """
    请求一页数据。每页的 params 不同（含 pageIndex），故每页都重新计算 i/u 再请求。
    翻页时 referer 带 &p=页码，与浏览器一致，避免 435。
    """
    referer = encode_page_url if page_index <= 1 else f"{encode_page_url}&p={page_index}"
    # 签名与请求 URL 必须用同一套参数顺序（字母序），否则服务端校验失败返回 435
    params_sorted = dict(sorted(params.items()))
    sign = gen_i_u("/api/bigsearch/recruit", params_sorted, tid)
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "cookie": cookie,
        "origin": "https://www.qcc.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": referer,
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
        sign["i"]: sign["u"],
    }
    resp = session.get(
        "https://www.qcc.com/api/bigsearch/recruit",
        headers=headers,
        params=params_sorted,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    # 1. Cookie / tid / 关键字
    cookie = input("请粘贴当前浏览器页面的 Cookie: ").strip()
    tid = input("请在浏览器控制台执行 window.tid 并粘贴结果: ").strip()
    key_word = input("搜索关键字（默认：体育）: ").strip() or "体育"

    # 2. 城市与每页条数（上海=3101，每页40）
    city_name = input("城市（默认上海，可选：北京/广州/深圳/杭州/留空不限）: ").strip() or "上海"
    city_code = CITY_CODES.get(city_name, "3101")
    try:
        page_size = int(input("每页条数（默认40）: ").strip() or "40")
    except ValueError:
        page_size = 40

    # 3. 静态页面获取 window.pid
    encode_page_url, window_pid = get_window_pid(cookie, key_word)

    # 4. 翻页：最多抓取页数
    max_pages_input = input("最多抓取几页（默认5，直接回车即 5）: ").strip() or "5"
    try:
        max_pages = int(max_pages_input)
    except ValueError:
        max_pages = 5

    all_results = []
    total_records = None

    for page_index in range(1, max_pages + 1):
        params = build_params(key_word, city_code=city_code, page_size=page_size, page_index=page_index)
        print(f"------------- 第 {page_index}/{max_pages} 页（pageIndex={page_index}）-------------")
        try:
            data = fetch_one_page(
                session, params, cookie, tid, window_pid, encode_page_url, page_index
            )
        except requests.HTTPError as e:
            print(f"请求失败: {e}")
            if e.response is not None and e.response.status_code == 435:
                print("可能 Cookie/tid 过期或签名异常，请重新获取后再试。")
            break
        except Exception as e:
            print(f"请求异常: {e}")
            break

        # 接口成功为 Status=200（大写）；失败时可能为 status=435（小写）
        status = data.get("Status") or data.get("status")
        if status != 200:
            print(f"接口返回 status={status}，message={data.get('message', '')}，停止翻页")
            if status == 435:
                print("提示：请重新从浏览器复制 Cookie 和 window.tid 后再试。")
            break

        paging = data.get("Paging") or {}
        total_records = paging.get("TotalRecords")
        items = data.get("Result") or []

        if not items:
            print("本页无数据，停止翻页")
            break

        all_results.extend(items)
        print(f"本页 {len(items)} 条，累计 {len(all_results)} 条（总记录数: {total_records}）")

        if page_index < max_pages:
            time.sleep(0.5)

    # 5. 保存结果
    if all_results:
        out_file = "recruit_result.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(
                {"total": len(all_results), "totalRecords": total_records, "list": all_results},
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"已保存 {len(all_results)} 条到 {out_file}")
    else:
        print("未获取到任何数据")


if __name__ == "__main__":
    main()