import requests
import json
import re
import os
import time
import random
from urllib.parse import parse_qs, urlparse
import warnings
import urllib3

class Keke7Downloader:
    def __init__(self):
        # 禁用SSL证书验证警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.headers = {
            'User-Agent': self._get_random_user_agent(),
            'Referer': 'https://www.keke7.app',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Priority': 'u=0, i',
            'Cookie': self._generate_cookie()
        }
        self.proxies = self._get_proxies()
        self.save_dir = 'E:\\视频'
        os.makedirs(self.save_dir, exist_ok=True)

    def _get_random_user_agent(self):
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)

    def _generate_bid(self):
        """生成随机bid"""
        return ''.join(random.choice('0123456789abcdef') for _ in range(11))

    def _generate_uuid(self):
        """生成随机uuid"""
        return ''.join(random.choice('0123456789abcdef') for _ in range(32))

    def _generate_cookie(self):
        """生成Cookie"""
        bid = self._generate_bid()
        uuid = self._generate_uuid()
        timestamp = str(int(time.time()))
        return f'bid={bid}; _uuid={uuid}; timestamp={timestamp}'

    def _get_proxies(self):
        """获取代理IP列表（示例）"""
        # 这里可以替换为实际的代理IP获取逻辑
        return [
            None,  # 直连
            {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'},  # 本地代理
        ]

    def _make_request(self, url, method='get', retry_count=0, max_retries=5):
        """统一的请求处理函数"""
        if retry_count >= max_retries:
            return None

        try:
            # 创建新的会话并设置基本请求头
            session = requests.Session()
            session.headers.update(self.headers)
            
            # 首先访问主页以获取必要的会话信息
            if retry_count == 0:
                try:
                    session.get('https://www.keke7.app', verify=False, timeout=15)
                except Exception:
                    pass  # 忽略主页访问的错误

            # 更新请求头
            session.headers.update({
                'User-Agent': self._get_random_user_agent(),
                'Cookie': self._generate_cookie(),
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.keke7.app',
                'Referer': 'https://www.keke7.app/',
                'Pragma': 'no-cache',
                'Sec-Fetch-Site': 'same-origin',
                'Accept': 'application/json, text/plain, */*',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty'
            })

            # 随机选择代理
            current_proxy = random.choice(self.proxies)
            if isinstance(current_proxy, dict) and not any(current_proxy.values()):
                current_proxy = None

            # 增加延迟时间
            delay = (2 ** retry_count) * 5 + random.uniform(2, 5)
            print(f'等待 {delay:.2f} 秒后进行第 {retry_count + 1} 次尝试...')
            time.sleep(delay)

            # 发送请求
            response = session.request(
                method,
                url,
                proxies=current_proxy,
                timeout=15,
                verify=False
            )
            response.raise_for_status()

            return response

        except requests.exceptions.RequestException as e:
            print(f'请求失败 ({retry_count + 1}/{max_retries}): {str(e)}')
            if isinstance(e, requests.exceptions.SSLError):
                print('SSL验证错误，已禁用SSL验证重试')
            elif isinstance(e, requests.exceptions.ProxyError):
                print('代理连接失败，尝试更换代理')
                self.proxies = self._get_proxies()
            elif isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 403:
                print('访问被拒绝，尝试更新请求头和Cookie')
                time.sleep(random.uniform(10, 20))  # 增加等待时间
            return self._make_request(url, method, retry_count + 1, max_retries)

    def get_video_info(self, video_id):
        """获取视频信息"""
        api_url = f'https://www.keke7.app/api/video/detail/{video_id}'
        response = self._make_request(api_url)
        
        if not response:
            return None
            
        try:
            data = response.json()
            if data.get('code') == 0:
                return data.get('data')
                
            print(f'API返回错误代码：{data.get("code")}, 信息：{data.get("msg", "未知错误")}')
            
        except Exception as e:
            print(f'解析响应数据失败: {str(e)}')
            
        return None

    def extract_video_id(self, url):
        """从URL中提取视频ID"""
        try:
            # 匹配URL中的视频ID
            pattern = r'/play/(\d+)-(\d+)-(\d+)\.html'
            match = re.search(pattern, url)
            if match:
                return {
                    'video_id': match.group(1),
                    'episode': match.group(2),
                    'play_id': match.group(3)
                }
            return None
        except Exception as e:
            print(f'提取视频ID失败: {str(e)}')
            return None

    def get_video_url(self, video_id, play_id):
        """获取视频播放地址"""
        api_url = f'https://www.keke7.app/api/video/play/{video_id}/{play_id}'
        response = self._make_request(api_url)
        
        if not response:
            return None
            
        try:
            data = response.json()
            if data.get('code') == 0:
                return data.get('data', {}).get('url')
                
            print(f'API返回错误代码：{data.get("code")}, 信息：{data.get("msg", "未知错误")}')
            
        except Exception as e:
            print(f'解析响应数据失败: {str(e)}')
            
        return None

    def download_video(self, video_url, title):
        """下载视频"""
        try:
            # 规范化文件名
            title = re.sub(r'[<>:"/\\|?*]', '_', title)
            file_path = os.path.join(self.save_dir, f'{title}.mp4')
            
            print(f'开始下载视频: {title}')
            response = self._make_request(video_url, method='get')
            if not response:
                return False
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1KB
            downloaded_size = 0

            with open(file_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    f.write(data)
                    downloaded_size += len(data)
                    progress = (downloaded_size / total_size) * 100
                    print(f'下载进度: {progress:.2f}%', end='\r')
            
            print(f'\n视频下载完成: {file_path}')
            return True
        except Exception as e:
            print(f'下载视频失败: {str(e)}')
            return False

    def download_from_url(self, url):
        """从URL下载视频"""
        try:
            # 提取视频ID
            video_info = self.extract_video_id(url)
            if not video_info:
                print('错误：无法从URL中提取视频ID，请检查URL格式是否正确')
                print('支持的URL格式：https://www.keke7.app/play/视频ID-集数-播放ID.html')
                return False

            # 获取视频信息
            print('正在获取视频信息...')
            video_data = self.get_video_info(video_info['video_id'])
            if not video_data:
                print('错误：获取视频信息失败，可能的原因：')
                print('1. 网络连接不稳定')
                print('2. 视频可能已下架')
                print('3. 当前IP可能被暂时限制')
                return False

            # 获取视频标题
            title = f"{video_data.get('title', '未知标题')}_{video_info['episode']}"

            print(f'视频标题：{title}')
            print('正在获取下载地址...')

            # 获取视频下载地址
            video_url = self.get_video_url(video_info['video_id'], video_info['play_id'])
            if not video_url:
                print('错误：获取视频下载地址失败，可能的原因：')
                print('1. 视频源可能已失效')
                print('2. 当前IP可能被暂时限制')
                return False

            # 下载视频
            return self.download_video(video_url, title)

        except Exception as e:
            print(f'下载过程中发生未知错误：{str(e)}')
            print('请尝试以下解决方案：')
            print('1. 检查网络连接是否稳定')
            print('2. 确认是否有足够的磁盘空间')
            print('3. 稍后重试或更换视频源')
            return False

def main():
    url = 'https://www.keke7.app/play/257537-32-1458534.html'
    downloader = Keke7Downloader()
    downloader.download_from_url(url)

if __name__ == '__main__':
    main()