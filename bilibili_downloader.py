import requests
import json
import re
import os
import time
from urllib.parse import parse_qs, urlparse

class BilibiliDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cookie': 'buvid3=A883B31B-5105-E133-0FBF-4836F83F2A8516311infoc; b_nut=1732877716; _uuid=1E32C17F-ADC10-18BC-6BB2-56B741014C2B416803infoc; buvid4=71E0464E-E4AF-F347-BC79-3FAE53AE7BC817103-024112910-eS68iHDBpPE2y%2BoZWZQirbMJ1IZ%2FDRXswIQYjyPaRjhyrkkfMpINB9fBbhXIExaO; buvid_fp_plain=undefined; rpdid=0zbfVG4j4R|TmHpWSMh|hcp|3w1TgYEX; DedeUserID=322377953; DedeUserID__ckMd5=9eaa717b344c86f7; LIVE_BUVID=AUTO8917329727457654; header_theme_version=CLOSE; enable_web_push=DISABLE; home_feed_column=5; CURRENT_QUALITY=80; bp_t_offset_322377953=1032623559454752768; fingerprint=f6f13da7c1f168b426c1579a3879bdc4; PVID=1; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDE0ODE5ODQsImlhdCI6MTc0MTIyMjcyNCwicGx0IjotMX0.K5AUNdUXrsFFasyEFn3iGZVZhIkVJjRq-wW2YcE2rt4; bili_ticket_expires=1741481924; b_lsid=1F473984_19568F7297D; SESSDATA=00a81100%2C1756774785%2Cf6403%2A32CjCC8VTikYwRrc4Ki5xz94KGeIznu77m9_JL_z2tJGO9WoVDqgpT2AnSuN7jNK9DtdYSVjJQM2RLTHRHUXZWd3pZdjVTTHpKRzduZFdEOGtoQVhpRFRSdEZYWWxlMjNoLTFZVm5fdTRIT2k0TU9fNGhNWmN5QXM1MjRseGNac0xnbmQxZ0M0bXVnIIEC; bili_jct=22e1fc85f6f276c3ae36ea130066c7b2; enable_feed_channel=DISABLE; browser_resolution=1528-738; sid=8kdnzl43; buvid_fp=f6f13da7c1f168b426c1579a3879bdc4; CURRENT_FNVAL=4048'
        }
        self.save_dir = 'E:\\视频'
        os.makedirs(self.save_dir, exist_ok=True)

    def set_cookie(self):
        """设置必要的Cookie信息"""
        print('请输入您的B站Cookie信息：')
        print('提示：请在B站登录后，按F12打开开发者工具，在Network标签页中找到任意请求，复制其Cookie值')
        cookie = input('请输入Cookie: ').strip()
        if cookie:
            self.headers['Cookie'] = cookie
            print('Cookie设置成功！')
        else:
            print('警告：未设置Cookie，某些视频可能无法下载')

    def extract_video_id(self, url):
        """从URL中提取视频BV号或番剧epid"""
        # 解析URL参数
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # 检查是否是番剧链接
        if 'bangumi/play' in url and 'ep' in parsed_url.path:
            ep_match = re.search(r'ep(\d+)', parsed_url.path)
            if ep_match:
                return {'type': 'bangumi', 'ep_id': ep_match.group(1)}
        
        # 普通视频链接
        bv_match = re.search(r'BV[a-zA-Z0-9]+', url)
        if bv_match:
            return {'type': 'video', 'bv_id': bv_match.group()}
            
        return None

    def get_video_info(self, video_id, max_retries=3):
        """获取视频信息，支持普通视频和番剧"""
        for retry in range(max_retries):
            try:
                if isinstance(video_id, dict) and video_id['type'] == 'bangumi':
                    # 番剧API
                    api_url = f'https://api.bilibili.com/pgc/view/web/season?ep_id={video_id["ep_id"]}'
                    response = requests.get(api_url, headers=self.headers)
                    response.raise_for_status()
                    data = response.json()
                    if data['code'] == 0:
                        # 找到指定集数的信息
                        for episode in data['result']['episodes']:
                            if str(episode['id']) == video_id['ep_id']:
                                return {
                                    'title': episode['share_copy'],
                                    'cid': episode['cid'],
                                    'bvid': episode.get('bvid', ''),
                                    'aid': episode['aid']
                                }
                else:
                    # 普通视频API
                    api_url = f'https://api.bilibili.com/x/web-interface/view?bvid={video_id["bv_id"]}'
                    response = requests.get(api_url, headers=self.headers)
                    response.raise_for_status()
                    data = response.json()
                    if data['code'] == 0:
                        return data['data']
                return None
            except requests.exceptions.RequestException as e:
                if retry < max_retries - 1:
                    print(f'获取视频信息失败，正在重试 ({retry + 1}/{max_retries}): {str(e)}')
                    time.sleep(2 ** retry)  # 指数退避
                    continue
                print(f'获取视频信息失败，已达到最大重试次数: {str(e)}')
                return None
            except Exception as e:
                print(f'获取视频信息时发生未知错误: {str(e)}')
                return None

    def get_video_url(self, bvid, cid):
        """获取视频下载地址"""
        # 设置qn=116以获取1080P60画质，如果不可用则自动降级
        api_url = f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=116&fnval=4048&fourk=1'
        max_retries = 3
        retry_delay = 1

        for retry in range(max_retries):
            try:
                response = requests.get(api_url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                if data['code'] == 0:
                    # 获取支持的最高画质URL
                    if 'dash' in data['data']:
                        # 优先使用DASH格式
                        video_info = max(data['data']['dash']['video'], key=lambda x: x['bandwidth'])
                        return video_info['baseUrl']
                    elif 'durl' in data['data']:
                        # 降级使用普通格式
                        return data['data']['durl'][0]['url']
                    
                if retry < max_retries - 1:
                    time.sleep(retry_delay * (retry + 1))
                    continue
                    
                return None
            except Exception as e:
                if retry < max_retries - 1:
                    print(f'获取视频下载地址失败，正在重试 ({retry + 1}/{max_retries}): {str(e)}')
                    time.sleep(retry_delay * (retry + 1))
                    continue
                print(f'获取视频下载地址失败: {str(e)}')
                return None

    def download_video(self, video_url, title):
        """下载视频"""
        try:
            # 规范化文件名
            title = re.sub(r'[<>:"/\\|?*]', '_', title)
            file_path = os.path.join(self.save_dir, f'{title}.mp4')
            
            print(f'开始下载视频: {title}')
            response = requests.get(video_url, headers=self.headers, stream=True)
            response.raise_for_status()
            
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
        """从URL下载视频，支持普通视频和番剧"""
        try:
            # 提取视频ID
            video_id = self.extract_video_id(url)
            if not video_id:
                print('错误：无法从URL中提取视频ID，请检查URL格式是否正确')
                print('支持的URL格式：')
                print('- 普通视频：https://www.bilibili.com/video/BVxxxxxx')
                print('- 番剧：https://www.bilibili.com/bangumi/play/epxxxxx')
                return False

            # 获取视频信息
            print('正在获取视频信息...')
            video_info = self.get_video_info(video_id)
            if not video_info:
                print('错误：获取视频信息失败，可能的原因：')
                print('1. 网络连接不稳定')
                print('2. 视频可能已下架或需要大会员权限')
                print('3. 当前IP可能被B站暂时限制')
                return False

            # 获取视频标题和cid
            title = video_info['title']
            cid = video_info['cid']
            bvid = video_info.get('bvid') or video_id.get('bv_id')

            print(f'视频标题：{title}')
            print('正在获取下载地址...')

            # 获取视频下载地址
            video_url = self.get_video_url(bvid, cid)
            if not video_url:
                print('错误：获取视频下载地址失败，可能的原因：')
                print('1. 视频清晰度可能受限制')
                print('2. 视频可能需要大会员权限')
                print('3. 当前IP可能被B站暂时限制')
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
    url = 'https://www.bilibili.com/bangumi/play/ep1403521?from_spmid=666.25.episode.0'
    downloader = BilibiliDownloader()
    downloader.download_from_url(url)

if __name__ == '__main__':
    main()