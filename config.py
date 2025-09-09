#!/usr/bin/env python3
"""
配置管理模块
Configuration Management Module
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ClientConfig:
    """客户端配置类"""
    # 服务器配置
    server_url: str = "https://personalaiassistant.my"
    api_key: Optional[str] = None
    
    # 下载配置
    download_dir: str = "./downloads"
    audio_quality: str = "best"  # best, good, fast
    keep_local_files: bool = False
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    
    # 上传配置
    chunk_size: int = 8 * 1024 * 1024  # 8MB chunks
    max_retries: int = 3
    timeout: int = 300  # 5分钟超时
    
    # 用户界面配置
    show_progress: bool = True
    use_colors: bool = True
    verbose: bool = False
    
    # 高级配置
    concurrent_downloads: int = 1
    temp_dir: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod 
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientConfig':
        """从字典创建配置"""
        return cls(**data)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为用户目录下的.ai-transcriber
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # 默认配置目录
            home = Path.home()
            self.config_path = home / ".ai-transcriber" / "config.yaml"
        
        self.config_path.parent.mkdir(exist_ok=True, parents=True)
        self.config = ClientConfig()
        
        # 加载现有配置
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.suffix.lower() == '.json':
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f) or {}
                    
                    self.config = ClientConfig.from_dict(data)
                    print(f"✅ 配置加载成功: {self.config_path}")
                    
            except Exception as e:
                print(f"⚠️ 配置文件加载失败: {e}")
                print("使用默认配置")
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.json':
                    json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
                else:
                    yaml.safe_dump(self.config.to_dict(), f, 
                                 default_flow_style=False, allow_unicode=True)
            
            print(f"✅ 配置保存成功: {self.config_path}")
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            raise ValueError(f"无效的配置项: {key}")
    
    def update(self, **kwargs):
        """批量更新配置"""
        for key, value in kwargs.items():
            self.set(key, value)
    
    def show_config(self):
        """显示当前配置"""
        print("\n📋 当前配置:")
        print("=" * 50)
        
        config_dict = self.config.to_dict()
        for key, value in config_dict.items():
            # 隐藏敏感信息
            if 'key' in key.lower() or 'token' in key.lower():
                display_value = "***" if value else "未设置"
            else:
                display_value = value
            
            print(f"{key:25}: {display_value}")
        print("=" * 50)
    
    def setup_wizard(self):
        """配置向导"""
        print("\n🚀 AI转录器客户端配置向导")
        print("=" * 40)
        
        # 服务器地址
        current_server = self.config.server_url
        server = input(f"服务器地址 [{current_server}]: ").strip()
        if server:
            self.config.server_url = server
        
        # API密钥（可选）
        api_key = input("API密钥（可选）: ").strip()
        if api_key:
            self.config.api_key = api_key
        
        # 下载目录
        current_dir = self.config.download_dir
        download_dir = input(f"下载目录 [{current_dir}]: ").strip()
        if download_dir:
            self.config.download_dir = download_dir
            # 创建目录
            Path(download_dir).mkdir(exist_ok=True, parents=True)
        
        # 音频质量
        print("音频质量选项:")
        print("  1. best  - 最佳质量（较大文件）")
        print("  2. good  - 良好质量（平衡）")
        print("  3. fast  - 快速下载（较小文件）")
        
        quality_choice = input(f"选择质量 [1-3, 当前: {self.config.audio_quality}]: ").strip()
        quality_map = {"1": "best", "2": "good", "3": "fast"}
        if quality_choice in quality_map:
            self.config.audio_quality = quality_map[quality_choice]
        
        # 是否保留本地文件
        keep_local = input("下载后保留本地文件？ [y/N]: ").strip().lower()
        self.config.keep_local_files = keep_local in ('y', 'yes', '是')
        
        # 保存配置
        self.save_config()
        print("\n✅ 配置完成！")
        self.show_config()


# 创建全局配置管理器实例
config_manager = ConfigManager()

def get_config() -> ClientConfig:
    """获取全局配置"""
    return config_manager.config

def update_config(**kwargs):
    """更新全局配置"""
    config_manager.update(**kwargs)
    config_manager.save_config()

if __name__ == "__main__":
    # 测试配置管理器
    print("🧪 测试配置管理器...")
    
    # 运行配置向导
    config_manager.setup_wizard()