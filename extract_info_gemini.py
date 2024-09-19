import os
import google.generativeai as genai
from PyPDF2 import PdfReader
import re
import time
import logging
from config import API_KEY

# 设置Google API密钥
genai.configure(api_key=API_KEY)

# 设置代理（如果需要的话）
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_text_from_pdf(pdf_path):
    """从PDF文件中提取文本（仅前两页）"""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages[:2]:  # 读取前两页
            text += page.extract_text()
    return text

def get_title_and_keywords(text):
    """使用Google Gemini AI提取标题和关键词"""
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            prompt = f"""Extract the document title and 5 keywords from the following text. 
            Format the output as follows:
            Title: [Extracted Title]
            Keywords: [Keyword1], [Keyword2], [Keyword3], [Keyword4], [Keyword5]

            Text:
            {text[:2000]}"""
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            if response.text:
                print("API 原始返回结果:", response.text)
                return response.text
            else:
                raise Exception("API 返回了空响应")
        except Exception as e:
            logging.error(f"尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
            if attempt < max_retries - 1:
                logging.info(f"{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
            else:
                logging.warning("达到最大重试次数，切换到备用方法...")
                return fallback_title_and_keywords(text)

def fallback_title_and_keywords(text):
    lines = text.split('\n')
    title = lines[0] if lines else "未知标题"
    keywords = "无法获取关键词"
    return f"Title: {title}\nKeywords: {keywords}"

def process_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    info = get_title_and_keywords(text)
    
    # 解析AI返回的信息
    title_match = re.search(r'Title:\s*(.*)', info)
    keywords_match = re.search(r'Keywords:\s*(.*)', info)
    
    title = title_match.group(1) if title_match else "未知标题"
    if keywords_match:
        keywords = keywords_match.group(1).strip()
        # 移除可能的多余空格和逗号
        keywords = re.sub(r'\s*,\s*', ', ', keywords)
        keywords = re.sub(r'^,\s*|\s*,$', '', keywords)
    else:
        keywords = "未知关键词"
    
    return title, keywords

def rename_pdf(folder_path, filename):
    file_path = os.path.join(folder_path, filename)
    title, keywords = process_pdf(file_path)
    
    # 移除不允许作为文件名的字符
    new_filename = re.sub(r'[<>:"/\\|?*]', '', title) + '.pdf'
    new_file_path = os.path.join(folder_path, new_filename)
    
    # 检查文件是否已存在，如果存在则添加数字后缀
    counter = 1
    while os.path.exists(new_file_path):
        base, ext = os.path.splitext(new_filename)
        new_filename = f"{base}_{counter}{ext}"
        new_file_path = os.path.join(folder_path, new_filename)
        counter += 1
    
    os.rename(file_path, new_file_path)
    logging.info(f'已将 "{filename}" 重命名为 "{new_filename}"')
    logging.info(f'关键词: {keywords}')

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            try:
                logging.info(f"开始处理文件: {filename}")
                rename_pdf(folder_path, filename)
            except Exception as e:
                logging.error(f"处理文件 {filename} 时发生错误: {str(e)}")

if __name__ == "__main__":
    folder_path = os.path.join(os.path.dirname(__file__), 'paper')
    process_folder(folder_path)