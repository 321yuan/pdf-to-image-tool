# PDF转图片工具

Python 工具，用于将PDF转换为图片，支持图形化界面操作。

## 功能特性

- 📄 支持选择PDF文件进行转换
- 🖼️ 将PDF每页转换为PNG图片
- 🔗 支持合并多页PDF为单张图片
- 🔐 支持密码保护的PDF文件
- 📊 实时显示转换进度
- 🎨 简洁美观的图形化界面

## 安装依赖

```bash
pip install pymupdf pillow
```

## 使用方法

### 方法一：直接运行

```bash
python pdf-to-image-tool.py
```

### 方法二：使用虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装依赖
pip install pymupdf pillow

# 运行
python pdf-to-image-tool.py
```

## 界面说明

1. **选择PDF文件** - 点击按钮选择要转换的PDF文件
2. **PDF密码（可选）** - 如果PDF有密码保护，请输入密码
3. **输出目录** - 设置图片保存位置（默认自动创建同名文件夹）
4. **合并选项** - 勾选后将所有页面合并为一张图片
5. **开始转换** - 点击开始转换

## 项目结构

```
pdf-to-image-tool/
├── pdf-to-image-tool.py   # 主程序文件
├── README.md              # 项目说明
├── requirements.txt       # 依赖列表
```

## 技术栈

- Python 3.x
- Tkinter (GUI)
- PyMuPDF (PDF处理)
- Pillow (图片处理)

## 许可证

MIT License
