# Qcc_Reverse_Crawler

关于企查查网站中「查招聘」板块官网的搜索结果爬虫逆向学习记录。<br />

参考 GitHub 项目 [Jmiao11/Qichacha_Reverse_Crawler](https://github.com/Jmiao11/Qichacha_Reverse_Crawler)。

---

## 项目概述

本项目对企查查 **查招聘**（`/web/bigsearch/recruit`）的接口进行逆向分析，复现其请求头中的动态签名（`i` / `u`），使用 Python + execjs 调用本地 JS 生成签名，通过 `GET /api/bigsearch/recruit` 获取招聘列表 JSON。支持**城市筛选**（如上海 city=3101）、**每页条数**（如 40 条）、**多页翻页**；签名逻辑与浏览器一致（path 含完整 query 并小写、参数字母序、第一页不传 pageIndex、翻页 referer 带 `&p=页码`），结果可保存为 JSON 文件。

---
## 网站预览

<img width="1858" height="910" alt="image" src="https://github.com/user-attachments/assets/96923f22-8c34-451c-9253-6a834a86fc7f" />

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `test.py` | 单页、无城市/条数限制的逆向测试脚本，便于验证签名与单次请求。 |
| `test-mutipage.py` | 多页爬取：支持限定城市、每页显示条数、最多抓取页数，按页重新计算 i/u 并请求，结果写入 `recruit_result.json`。 |
| `02_企查查_header加密逻辑.js` | 签名算法（dd/bb/r_default/aa/main），供 Python 通过 execjs 调用生成动态请求头 `i`、`u`。 |
| `encode_url.py` | URL 中文编码工具，用于构造 recruit 页面 URL 与 referer。 |
| `企查查招聘接口逆向说明.md` | 逆向过程文档：问题与解决方案、加解密逻辑、使用步骤、功能改进总结。 |
| `new_qichacha.js` | 原始前端打包 JS，用于对照分析签名逻辑。 |

*以上两个测试脚本可直接运行；其余文件为对参考项目的微调或补充，用途与原项目对应文件一致。*

---

## 结果输出

###  `test-mutipage.py` 生成的结果文件(部分数据）：

结果保存在 **recruit_result.json**，结构如下：

```json
{
  "total": 200,
  "totalRecords": 12244,
  "list": [
    {
      "Id": "c61349ff5cbd9cc7c7be54efd1826443",
      "CompanyName": "中乔<em>体育</em>股份有限公司",
      "CompanyKeyNo": "8c977787694d5a833d29786ea56a4e16",
      "PublishTime": 1772257519,
      "Salary": "12-13k·15薪",
      "Province": "上海",
      "City": "上海",
      "Education": "本科",
      "Experience": "3-5年",
      "PositionName": "HRBP-薪酬绩效主管",
      "Companyscale": "6000-6999人",
      "Financing": "",
      "EducationCode": 4,
      "ExperienceCode": 3,
      "SalaryCode": 3
    }
  ]
}
```

- **total**：本次抓取条数  
- **totalRecords**：接口返回的总记录数  
- **list**：招聘列表，字段含义与官网一致（公司名、职位、薪资、城市等）

---

###  `test.py` 输出：
  
<img width="1444" height="584" alt="image" src="https://github.com/user-attachments/assets/c4a6478a-f8ae-46fc-b627-b3a9d3a03d46" />

---

## 使用步骤

1. 浏览器打开 `https://www.qcc.com/web/bigsearch/recruit?searchKey=体育`，确保能正常看到列表。
2. F12 → Network → 任选一个 `www.qcc.com` 请求，复制 Request Headers 中的 **Cookie**。
3. F12 → Console → 输入 `window.tid`，复制返回值。
4. 运行 `python test-mutipage.py`（或 `python test.py`），按提示输入 Cookie、tid、关键字、城市、每页条数、最多抓取页数等。
5. 多页结果将写入当前目录下的 **recruit_result.json**。

⚠️更多细节（如 435 错误排查、第一页不传 pageIndex、参数顺序与 referer 等）见 **企查查招聘接口逆向说明.md**。
