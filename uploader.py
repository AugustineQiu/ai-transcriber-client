#!/usr/bin/env python3
"""
服务器上传模块
Server Upload Module
"""

import os
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from tqdm import tqdm

from config import get_config

@dataclass
class UploadResult:
    """上传结果"""
    success: bool
    task_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    server_response: Optional[Dict[str, Any]] = None


class ServerUploader:
    """服务器上传器"""
    
    def __init__(self):
        """初始化上传器"""
        self.config = get_config()
        self.session = requests.Session()
        
        # 设置默认头部
        self.session.headers.update({
            'User-Agent': 'AI-Transcriber-Client/1.0.0',
            'Accept': 'application/json'
        })
        
        # API密钥
        if self.config.api_key:
            self.session.headers['Authorization'] = f'Bearer {self.config.api_key}'
        
        self.progress_callback: Optional[Callable] = None
        
        print(f"🌐 服务器: {self.config.server_url}")
    
    def set_progress_callback(self, callback: Callable):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def _get_upload_url(self) -> str:
        """获取文件上传API地址"""
        base_url = self.config.server_url.rstrip('/')
        return f"{base_url}/api/transcribe/file"
    
    def _get_task_status_url(self, task_id: str) -> str:
        """获取任务状态API地址"""
        base_url = self.config.server_url.rstrip('/')
        return f"{base_url}/api/task/{task_id}"
    
    def auto_detect_server(self) -> Optional[str]:
        """自动检测可用的本地服务器端口"""
        print("🔍 自动检测本地服务器...")
        
        # 常见的本地服务器端口列表
        local_ports = [8000, 8001, 8002, 8003, 8888, 8889, 5000, 3000]
        
        for port in local_ports:
            test_url = f"http://localhost:{port}"
            try:
                health_urls = [
                    f"{test_url}/health",
                    f"{test_url}/api/health", 
                    f"{test_url}/",
                    f"{test_url}"
                ]
                
                for url in health_urls:
                    try:
                        response = self.session.get(url, timeout=3)
                        if response.status_code in [200, 404]:
                            print(f"✅ 发现可用服务器: {test_url}")
                            return test_url
                    except requests.exceptions.RequestException:
                        continue
                        
            except Exception:
                continue
                
        print("❌ 未找到可用的本地服务器")
        return None
        
    def test_connection(self) -> bool:
        """测试服务器连接（支持自动端口检测）"""
        try:
            print("🔍 测试服务器连接...")
            
            # 首先尝试配置的服务器地址
            base_url = self.config.server_url.rstrip('/')
            health_urls = [
                f"{base_url}/health",
                f"{base_url}/api/health", 
                f"{base_url}/",
                f"{base_url}"
            ]
            
            for url in health_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code in [200, 404]:  # 404也说明服务器在线
                        print(f"✅ 服务器连接正常: {response.status_code}")
                        return True
                except requests.exceptions.RequestException:
                    continue
            
            # 如果配置的服务器无法连接，尝试自动检测本地服务器
            if 'localhost' in self.config.server_url or '127.0.0.1' in self.config.server_url:
                print("🔄 尝试自动检测本地服务器端口...")
                detected_url = self.auto_detect_server()
                
                if detected_url:
                    # 更新配置中的服务器地址
                    self.config.server_url = detected_url
                    print(f"🔄 已切换到检测到的服务器: {detected_url}")
                    return True
            
            print("❌ 服务器连接失败")
            return False
            
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False
    
    def upload_file(self, file_path: str, **kwargs) -> UploadResult:
        """
        上传文件到服务器进行转录
        
        Args:
            file_path: 文件路径
            **kwargs: 其他转录参数
        
        Returns:
            UploadResult: 上传结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return UploadResult(
                success=False,
                error=f"文件不存在: {file_path}"
            )
        
        file_size = file_path.stat().st_size
        print(f"📤 开始上传: {file_path.name} ({file_size / 1024 / 1024:.1f}MB)")
        
        try:
            upload_url = self._get_upload_url()
            
            # 准备文件和表单数据
            files = {
                'file': (file_path.name, open(file_path, 'rb'), 'audio/mpeg')
            }
            
            # 转录参数
            data = {
                'provider': kwargs.get('provider', 'openai'),
                'model': kwargs.get('model', 'whisper-1'),
                'language': kwargs.get('language', 'auto'),
                'chunking_strategy': kwargs.get('chunking_strategy', 'auto'),
                'concurrent_chunks': kwargs.get('concurrent_chunks', 5),
            }
            
            # 创建进度条
            progress_bar = None
            if self.config.show_progress:
                progress_bar = tqdm(
                    total=file_size,
                    unit='B',
                    unit_scale=True,
                    desc="上传中"
                )
            
            # 自定义上传函数，支持进度显示
            def upload_callback(monitor):
                if progress_bar:
                    progress_bar.update(monitor.bytes_read - progress_bar.n)
                if self.progress_callback:
                    percent = (monitor.bytes_read / file_size) * 100
                    self.progress_callback({
                        'status': 'uploading',
                        'percent': percent,
                        'uploaded': monitor.bytes_read,
                        'total': file_size
                    })
            
            # 发送请求
            print(f"🚀 上传到: {upload_url}")
            
            response = self.session.post(
                upload_url,
                files=files,
                data=data,
                timeout=self.config.timeout
            )
            
            # 关闭文件
            files['file'][1].close()
            
            if progress_bar:
                progress_bar.close()
            
            # 处理响应
            if response.status_code == 200:
                result_data = response.json()
                task_id = result_data.get('task_id')
                
                print(f"✅ 上传成功!")
                print(f"📋 任务ID: {task_id}")
                
                return UploadResult(
                    success=True,
                    task_id=task_id,
                    message="文件上传并开始转录",
                    server_response=result_data
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ 上传失败: {error_msg}")
                
                return UploadResult(
                    success=False,
                    error=error_msg,
                    server_response=response.text
                )
                
        except requests.exceptions.Timeout:
            error_msg = "上传超时"
            print(f"❌ {error_msg}")
            return UploadResult(success=False, error=error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = "无法连接到服务器"
            print(f"❌ {error_msg}")
            return UploadResult(success=False, error=error_msg)
            
        except Exception as e:
            error_msg = f"上传异常: {str(e)}"
            print(f"❌ {error_msg}")
            return UploadResult(success=False, error=error_msg)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        try:
            status_url = self._get_task_status_url(task_id)
            response = self.session.get(status_url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'error': f'获取任务状态异常: {str(e)}'
            }
    
    def wait_for_completion(self, task_id: str, 
                          poll_interval: int = 5, 
                          max_wait_time: int = 600) -> Dict[str, Any]:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            poll_interval: 轮询间隔（秒）
            max_wait_time: 最大等待时间（秒）
        
        Returns:
            Dict: 最终任务状态
        """
        print(f"⏳ 等待转录完成 (任务ID: {task_id})")
        
        start_time = time.time()
        last_status = None
        
        with tqdm(desc="转录中", unit="s") as pbar:
            while time.time() - start_time < max_wait_time:
                status_data = self.get_task_status(task_id)
                
                if 'error' in status_data:
                    print(f"❌ 获取状态失败: {status_data['error']}")
                    return status_data
                
                current_status = status_data.get('status', 'unknown')
                progress = status_data.get('progress', 0)
                
                # 更新进度条
                if current_status != last_status:
                    pbar.set_description(f"转录中 ({current_status})")
                    last_status = current_status
                
                pbar.set_postfix(progress=f"{progress:.1f}%")
                
                # 检查是否完成
                if current_status == 'completed':
                    pbar.set_description("转录完成")
                    pbar.set_postfix(progress="100%")
                    print(f"\n✅ 转录完成!")
                    return status_data
                elif current_status == 'failed':
                    error_msg = status_data.get('error', '未知错误')
                    print(f"\n❌ 转录失败: {error_msg}")
                    return status_data
                
                # 等待下次轮询
                time.sleep(poll_interval)
                pbar.update(poll_interval)
        
        # 超时
        print(f"\n⏰ 等待超时 ({max_wait_time}秒)")
        return {
            'error': f'等待超时，任务可能仍在进行中。任务ID: {task_id}',
            'task_id': task_id,
            'timeout': True
        }
    
    def download_result(self, task_id: str, output_dir: str = "./results") -> Optional[str]:
        """下载转录结果"""
        try:
            # 获取任务状态，包含结果链接
            status_data = self.get_task_status(task_id)
            
            if status_data.get('status') != 'completed':
                print("❌ 任务尚未完成，无法下载结果")
                return None
            
            # 这里需要根据服务器API实现下载逻辑
            # 目前先返回状态信息
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True, parents=True)
            
            result_file = output_path / f"transcription_{task_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 转录结果已保存: {result_file}")
            return str(result_file)
            
        except Exception as e:
            print(f"❌ 下载结果失败: {e}")
            return None


def test_uploader():
    """测试上传器"""
    print("🧪 测试服务器上传器...")
    
    uploader = ServerUploader()
    
    # 测试连接
    if uploader.test_connection():
        print("✅ 服务器连接测试通过")
    else:
        print("❌ 服务器连接测试失败")


if __name__ == "__main__":
    test_uploader()