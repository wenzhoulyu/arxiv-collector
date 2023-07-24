from datetime import datetime, timedelta


def get_previous_weekdays(start_date, count):
    weekdays = []
    current_date = start_date
    while len(weekdays) < count:
        current_date -= timedelta(days=1)
        if current_date.weekday() < 5:  # Monday(0) to Friday(4) are weekdays
            weekdays.append(current_date.strftime('%Y%m%d'))
    return weekdays


def check_multiple_strings(main_string, substrings):
    main_string_ = main_string.replace('-\n', '-').replace('\n', ' ')
    lower_main_string = main_string_.lower()
    is_all_caps_in_original = all(substring in main_string_ for substring in substrings if substring.isupper())
    is_not_all_caps_in_lower = all(
        substring.lower() in lower_main_string for substring in substrings if not substring.isupper())
    return is_all_caps_in_original and is_not_all_caps_in_lower


import markdown
from bs4 import BeautifulSoup

import markdown
from bs4 import BeautifulSoup


def extract_content_between_h1_li(markdown_text, search_string):
    # 将Markdown文本转换为HTML
    html_text = markdown.markdown(markdown_text)
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_text, 'html.parser')
    # print(html_text)
    # print(search_string)
    target_li = soup.find('li', text='Title: ' + search_string)
    # 提取目标<li>标签前后的<h1>标签内容
    result = []
    if target_li:
        previous_h1 = target_li.find_previous('h1')
        next_h1 = target_li.find_next('h1')
        
        # Loop through siblings of the target <li> and collect the text until reaching an <h1> tag
        current_tag = previous_h1
        while current_tag and current_tag.next_sibling != next_h1:
            current_tag = current_tag.next_sibling
            if current_tag and current_tag.name != 'h1':
                result.append(current_tag.get_text().strip())
    return result


def list_to_markdown(list_items):
    # Convert the list of items to Markdown format
    markdown_list = '\n'.join([f"- {item}" for item in list_items])
    return markdown_list


def is_subsentence(subsentence, sentence):
    subsentence_length = len(subsentence)
    sentence_length = len(sentence)
    i = 0
    j = 0
    
    while i < subsentence_length and j < sentence_length:
        if subsentence[i] == sentence[j]:
            i += 1
        j += 1
    
    return i == subsentence_length

# # 读取Markdown文件内容
# markdown_file_path = 'your_markdown_file.md'
# with open(markdown_file_path, 'r', encoding='utf-8') as file:
#     markdown_text = file.read()
#
# # 设置要搜索的字符串
# search_string = 'Your_Search_String'
#
# # 提取包含搜索字符串的二级标题下的内容
# extracted_contents = extract_content_by_string(markdown_text, search_string)
#
# # 输出提取的内容
# for title, content in extracted_contents.items():
#     print(f"Title: {title}")
#     print(f"Content: {content}")
#     print()
