#!/usr/bin/env python3
import subprocess
import time
import os
import yaml
import logging
import signal
import psutil
from datetime import datetime, timedelta
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gpu_monitor.log'),
        logging.StreamHandler()
    ]
)

class GPUMonitor:
    def __init__(self, config_path='gpu_monitor_config.json'):
        # 默认配置
        self.config = {
            'temperature_threshold': 85,
            'monitor_interval': 60,  # 监控间隔（秒）
            'overheat_duration': 600,  # 过热持续时间（秒）
            'cooldown_duration': 3600,  # 冷却时间（秒）
            'yaml_path': 'examples/train_lora/qwen2-7b-lora-sft.yaml',
            'checkpoint_dir': 'saves/qwen2-7b/lora/firepower_issues'
        }
        
        # 加载配置文件（如果存在）
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config.update(json.load(f))
        
        self.overheat_start_time = None
        self.current_process = None

    def get_gpu_temperature(self):
        try:
            result = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'])
            # 处理多GPU情况，获取所有温度值
            temperatures = [float(temp.strip()) for temp in result.decode().strip().split('\n')]
            # 返回最高温度
            max_temp = max(temperatures)
            logging.info(f"所有GPU温度: {temperatures}°C")
            return max_temp
        except Exception as e:
            logging.error(f"获取GPU温度失败: {e}")
            return None

    def get_latest_checkpoint(self):
        try:
            checkpoint_dir = self.config['checkpoint_dir']
            if not os.path.exists(checkpoint_dir):
                return None
            
            # 获取所有checkpoint目录
            checkpoints = [d for d in os.listdir(checkpoint_dir) if d.startswith('checkpoint-')]
            if not checkpoints:
                return None
            
            # 按数字排序并获取最新的
            latest = max(checkpoints, key=lambda x: int(x.split('-')[1]))
            return os.path.join(checkpoint_dir, latest)
        except Exception as e:
            logging.error(f"获取最新checkpoint失败: {e}")
            return None

    def update_yaml_checkpoint(self, checkpoint_path):
        try:
            yaml_path = self.config['yaml_path']
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
            
            config['resume_from_checkpoint'] = checkpoint_path
            
            with open(yaml_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            logging.info(f"已更新checkpoint路径: {checkpoint_path}")
        except Exception as e:
            logging.error(f"更新YAML文件失败: {e}")

    def stop_training(self):
        try:
            # 查找并终止训练进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'train.py' in cmdline:
                        os.kill(proc.info['pid'], signal.SIGTERM)
                        logging.info(f"已终止训练进程: {proc.info['pid']}")
                        return True
            return False
        except Exception as e:
            logging.error(f"终止训练进程失败: {e}")
            return False

    def start_training(self):
        try:
            # 启动训练进程
            cmd = ['python', 'src/train.py', '--config', self.config['yaml_path']]
            self.current_process = subprocess.Popen(cmd)
            logging.info("已启动训练进程")
            return True
        except Exception as e:
            logging.error(f"启动训练进程失败: {e}")
            return False

    def monitor(self):
        logging.info("开始监控GPU温度...")
        while True:
            try:
                temp = self.get_gpu_temperature()
                if temp is None:
                    time.sleep(self.config['monitor_interval'])
                    continue

                current_time = datetime.now()
                logging.info(f"当前最高GPU温度: {temp}°C")

                if temp > self.config['temperature_threshold']:
                    if self.overheat_start_time is None:
                        self.overheat_start_time = current_time
                        logging.warning(f"GPU温度超过阈值 {self.config['temperature_threshold']}°C")
                    
                    # 检查是否持续过热
                    if (current_time - self.overheat_start_time).total_seconds() >= self.config['overheat_duration']:
                        logging.warning("GPU持续过热，准备暂停训练...")
                        
                        # 获取最新checkpoint并更新YAML
                        latest_checkpoint = self.get_latest_checkpoint()
                        if latest_checkpoint:
                            self.update_yaml_checkpoint(latest_checkpoint)
                        
                        # 停止训练
                        if self.stop_training():
                            logging.info(f"等待 {self.config['cooldown_duration']} 秒后重新启动训练...")
                            time.sleep(self.config['cooldown_duration'])
                            
                            # 重新启动训练
                            if self.start_training():
                                self.overheat_start_time = None
                                logging.info("训练已重新启动")
                else:
                    self.overheat_start_time = None

                time.sleep(self.config['monitor_interval'])
            
            except KeyboardInterrupt:
                logging.info("监控程序已停止")
                break
            except Exception as e:
                logging.error(f"监控过程中发生错误: {e}")
                time.sleep(self.config['monitor_interval'])

if __name__ == "__main__":
    monitor = GPUMonitor()
    monitor.monitor() 