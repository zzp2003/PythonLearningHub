import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import pandas as pd
import random
import re

class WebCrawler:
    def __init__(self, save_dir='E:\\download\\豆瓣电影'):
        self.base_url = 'https://movie.douban.com/top250'
        self.save_dir = save_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'bid=' + ''.join(random.choice('0123456789abcdef') for _ in range(11))
        }
        self.movies_data = []
        os.makedirs(save_dir, exist_ok=True)

    def download_page(self, url):
        try:
            time.sleep(random.uniform(2, 4))  # 增加随机延时
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f'下载页面出错 {url}: {str(e)}')
            return None

    def parse_movie_info(self, item):
        try:
            # 提取标题
            title_element = item.find('span', class_='title')
            if not title_element:
                return None
            title = title_element.get_text(strip=True)
            
            # 提取评分
            rating_element = item.find('span', class_='rating_num')
            rating = rating_element.get_text(strip=True) if rating_element else '暂无评分'
            
            # 提取评价人数（优化获取方式）
            votes = '暂无评价'
            star_div = item.find('div', class_='star')
            if star_div:
                votes_text = star_div.find_all('span')[-1].get_text(strip=True) if star_div.find_all('span') else ''
                votes_match = re.search(r'(\d+)人评价', votes_text)
                if votes_match:
                    votes = votes_match.group(1)
            
            # 提取基本信息（年份/地区/类型）和导演主演信息
            info_element = item.find('div', class_='bd')
            if not info_element:
                return None

            # 获取所有p标签
            info_paragraphs = info_element.find_all('p')
            if not info_paragraphs or len(info_paragraphs) < 2:
                return None

            # 处理第一个p标签（导演、主演等信息）
            info_text = info_paragraphs[0].get_text(strip=True).split('\n')
            director_actor = info_text[0].strip() if info_text else ''
            if not director_actor:
                director_actor = '暂无导演/主演信息'

            # 处理第二个p标签（年份、地区等信息）
            year_info = info_paragraphs[1].get_text(strip=True).split('/')
            year = year_info[0].strip() if year_info else '未知年份'
            
            # 提取简介（优化获取方式）
            quote = '暂无简介'
            quote_element = item.find('span', class_='inq')
            if quote_element:
                quote_text = quote_element.get_text(strip=True)
                if quote_text:
                    quote = quote_text
            
            return {
                '电影名': title,
                '评分': rating,
                '评价人数': votes,
                '年份': year,
                '导演/主演': director_actor,
                '简介': quote
            }
        except Exception as e:
            print(f'解析电影信息出错: {str(e)}')
            return None

    def crawl(self):
        start_time = time.time()
        
        for page in range(0, 250, 25):
            url = f'{self.base_url}?start={page}'
            content = self.download_page(url)
            if not content:
                continue

            soup = BeautifulSoup(content, 'html.parser')
            movie_list = soup.find_all('div', class_='item')
            
            for movie in movie_list:
                movie_info = self.parse_movie_info(movie)
                if movie_info:
                    self.movies_data.append(movie_info)
            
            print(f'已完成第{page//25 + 1}页的爬取，当前已获取{len(self.movies_data)}部电影信息')

        end_time = time.time()
        
        if self.movies_data:
            # 将爬取的数据保存为Excel文件
            df = pd.DataFrame(self.movies_data)
            excel_path = os.path.join(self.save_dir, 'douban_top250.xlsx')
            df.to_excel(excel_path, index=False, engine='openpyxl')
            
            print(f'\n爬虫完成!')
            print(f'总共获取了 {len(self.movies_data)} 部电影信息')
            print(f'数据已保存到: {excel_path}')
            print(f'耗时: {end_time - start_time:.2f} 秒')
        else:
            print('\n未能获取到任何电影信息，请检查网络连接或者网站是否有反爬虫机制。')

def main():
    crawler = WebCrawler()
    crawler.crawl()

if __name__ == '__main__':
    main()