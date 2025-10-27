#!/usr/bin/env python3
"""
统计指定目录下总像素值大于4096*4096的PNG图片数量
"""

import os
from pathlib import Path
from PIL import Image

def count_large_images(directory_path, pixel_threshold=4096*4096):
    """
    统计目录中总像素值大于指定阈值的PNG图片数量
    
    Args:
        directory_path: 图片目录路径
        pixel_threshold: 总像素值阈值（默认4096*4096 = 16,777,216）
    
    Returns:
        tuple: (大于阈值的图片数量, 总图片数量, 大于阈值的图片列表)
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"错误: 目录不存在 - {directory_path}")
        return 0, 0, []
    
    # 查找所有PNG文件
    png_files = list(directory.glob("*.png"))
    png_files.extend(directory.glob("*.PNG"))  # 包含大写扩展名
    
    total_count = len(png_files)
    over_threshold_count = 0
    over_threshold_files = []
    
    print(f"正在扫描目录: {directory_path}")
    print(f"找到 {total_count} 张PNG图片")
    print(f"像素值阈值设置: {pixel_threshold:,} (4096x4096)")
    print("-" * 60)
    
    for img_path in png_files:
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                total_pixels = width * height
                
                # 检查总像素值是否大于阈值
                if total_pixels > pixel_threshold:
                    over_threshold_count += 1
                    over_threshold_files.append({
                        'path': img_path.name,
                        'size': (width, height),
                        'pixels': total_pixels
                    })
                    print(f"✓ {img_path.name}: {width}x{height} = {total_pixels:,} 像素")
        except Exception as e:
            print(f"✗ 无法读取 {img_path.name}: {e}")
    
    return over_threshold_count, total_count, over_threshold_files


def main():
    # 目标目录
    target_directory = "/wekafs/takisobe/haisenhe/DataPipeline/unsplash1/images/degraded"
    
    # 统计（总像素值大于4096*4096）
    pixel_threshold = 4096 * 4096
    over_count, total_count, large_files = count_large_images(
        target_directory, 
        pixel_threshold=pixel_threshold
    )
    
    # 输出结果
    print("=" * 60)
    print(f"\n统计结果:")
    print(f"  总图片数量: {total_count}")
    print(f"  像素值大于{pixel_threshold:,}的图片数量: {over_count}")
    
    if total_count > 0:
        percentage = (over_count / total_count) * 100
        print(f"  占比: {percentage:.2f}%")
    
    # if large_files:
    #     print(f"\n像素值大于4096x4096的图片详情:")
    #     for file_info in large_files:
    #         print(f"  - {file_info['path']}: {file_info['size'][0]}x{file_info['size'][1]} = {file_info['pixels']:,} 像素")


if __name__ == "__main__":
    main()

