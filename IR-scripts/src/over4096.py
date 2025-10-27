#!/usr/bin/env python3
"""
统计并处理总像素值大于指定阈值的PNG图片
功能：
1. 统计总像素值大于4096*4096的图片数量
2. 将总像素值大于4096*8192的图片resize到合适尺寸（保持纵横比，最长边为4096）
"""

import os
from pathlib import Path
from PIL import Image

def count_and_find_large_images(directory_path, stat_threshold=4096*4096, resize_threshold=4096*8192):
    """
    统计目录中总像素值大于指定阈值的PNG图片数量，并找出需要resize的图片
    
    Args:
        directory_path: 图片目录路径
        stat_threshold: 统计阈值（默认4096*4096 = 16,777,216）
        resize_threshold: 需要resize的阈值（默认4096*8192 = 33,554,432）
    
    Returns:
        tuple: (统计信息字典, 需要resize的图片列表)
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"错误: 目录不存在 - {directory_path}")
        return None, []
    
    # 查找所有PNG文件
    png_files = list(directory.glob("*.png"))
    png_files.extend(directory.glob("*.PNG"))  # 包含大写扩展名
    
    total_count = len(png_files)
    over_stat_threshold = 0
    over_resize_threshold = 0
    need_resize_files = []
    
    print(f"正在扫描目录: {directory_path}")
    print(f"找到 {total_count} 张PNG图片")
    print(f"统计阈值: {stat_threshold:,} (4096x4096)")
    print(f"Resize阈值: {resize_threshold:,} (4096x8192)")
    print("-" * 70)
    
    for img_path in png_files:
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                total_pixels = width * height
                
                # 统计大于stat_threshold的图片
                if total_pixels > stat_threshold:
                    over_stat_threshold += 1
                    
                # 找出需要resize的图片
                if total_pixels > resize_threshold:
                    over_resize_threshold += 1
                    need_resize_files.append({
                        'path': img_path,
                        'size': (width, height),
                        'pixels': total_pixels
                    })
                    print(f"🔍 需要resize: {img_path.name}: {width}x{height} = {total_pixels:,} 像素")
        except Exception as e:
            print(f"✗ 无法读取 {img_path.name}: {e}")
    
    stats = {
        'total': total_count,
        'over_stat': over_stat_threshold,
        'over_resize': over_resize_threshold
    }
    
    return stats, need_resize_files


def resize_image(img_path, max_size=4096):
    """
    将图片resize到指定尺寸（保持纵横比，最长边为max_size），直接覆盖原文件
    
    Args:
        img_path: 原图片路径（Path对象）
        max_size: 最长边的最大尺寸
    
    Returns:
        bool: 是否成功
    """
    try:
        # 读取原图片
        img = Image.open(img_path)
        width, height = img.size
        
        # 计算缩放比例（保持纵横比）
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        
        # Resize图片（使用高质量的LANCZOS重采样）
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 关闭原图片
        img.close()
        
        # 直接覆盖原文件
        resized_img.save(img_path, 'PNG')
        
        new_pixels = new_width * new_height
        print(f"  ✓ {img_path.name}: {width}x{height} → {new_width}x{new_height} ({new_pixels:,} 像素)")
        return True
            
    except Exception as e:
        print(f"  ✗ 处理失败 {img_path.name}: {e}")
        return False


def main():
    # 配置参数
    source_directory = "/wekafs/takisobe/haisenhe/DataPipeline/unsplash1/images/degraded"
    
    stat_threshold = 4096 * 4096    # 统计阈值：16,777,216像素
    resize_threshold = 4096 * 8192  # Resize阈值：33,554,432像素
    max_size = 4096                 # Resize后最长边的尺寸
    
    print("=" * 70)
    print("图片统计与处理工具")
    print("=" * 70)
    
    # 第一步：扫描并统计
    stats, need_resize_files = count_and_find_large_images(
        source_directory,
        stat_threshold=stat_threshold,
        resize_threshold=resize_threshold
    )
    
    if stats is None:
        return
    
    # 输出统计结果
    print("\n" + "=" * 70)
    print("统计结果:")
    print(f"  总图片数量: {stats['total']}")
    print(f"  像素值大于{stat_threshold:,}的图片数量: {stats['over_stat']}")
    print(f"  像素值大于{resize_threshold:,}的图片数量: {stats['over_resize']} (需要resize)")
    
    if stats['total'] > 0:
        percentage1 = (stats['over_stat'] / stats['total']) * 100
        percentage2 = (stats['over_resize'] / stats['total']) * 100
        print(f"  大于4096x4096占比: {percentage1:.2f}%")
        print(f"  大于4096x8192占比: {percentage2:.2f}%")
    
    # 第二步：Resize处理
    if need_resize_files:
        print("\n" + "=" * 70)
        print(f"⚠️  警告: 即将覆盖 {len(need_resize_files)} 张原始图片文件！")
        print("=" * 70)
        
        # 确认操作
        response = input("确认要覆盖原文件吗? (输入 yes 继续): ")
        if response.lower() != 'yes':
            print("操作已取消。")
            return
        
        print("\n" + "=" * 70)
        print(f"开始处理 {len(need_resize_files)} 张图片...")
        print("-" * 70)
        
        # 处理每张图片
        success_count = 0
        for file_info in need_resize_files:
            if resize_image(file_info['path'], max_size=max_size):
                success_count += 1
        
        # 输出处理结果
        print("\n" + "=" * 70)
        print("处理完成!")
        print(f"  成功处理: {success_count}/{len(need_resize_files)} 张图片")
        print(f"  原文件已被覆盖")
    else:
        print("\n没有需要resize的图片。")
    
    print("=" * 70)


if __name__ == "__main__":
    main()

