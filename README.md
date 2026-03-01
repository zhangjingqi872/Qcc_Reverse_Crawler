# Qcc_Reverse_Crawler
关于企查查网站中“查招聘”板块官网的搜索结果爬虫逆向学习记录。
<br> 参考github网站上 **Jmiao11/Qichacha_Reverse_Crawler** 的作品。<br> 
### 文件说明
`test.py` 文件为单页无限制条件的逆向测试文件。<br>
`test-mutipage.py` 文件为多页限定城市、限定每页显示条数、限制抓取页数的逆向测试文件。<br>
*以上两个文件可测试运行，其余文件为  Jmiao11/Qichacha_Reverse_Crawler** 的微调同名文件，意义与原项目文件相同*
### 结果输出
#### `test.py`输出：
<img width="1444" height="584" alt="image" src="https://github.com/user-attachments/assets/c4a6478a-f8ae-46fc-b627-b3a9d3a03d46" />
#### `test-mutipage.py`生成的结果文件：
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
    },
```
