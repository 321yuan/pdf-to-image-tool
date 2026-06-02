import os
import sys
import fitz
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tqdm import tqdm


def install_dependencies():
    try:
        import fitz
        from tqdm import tqdm
        from PIL import Image
    except ImportError:
        print("正在安装依赖库...")
        os.system(f"{sys.executable} -m pip install pymupdf tqdm pillow")
        import fitz
        from tqdm import tqdm
        from PIL import Image


def pdf_to_images(pdf_path, output_dir=None, password=None, merge_pages=False, progress_callback=None):
    try:
        from PIL import Image
        
        pdf_path = os.path.normpath(pdf_path)
        doc = fitz.open(pdf_path)
        
        if doc.needs_pass:
            if password:
                if not doc.authenticate(password):
                    return False, "密码错误！"
            else:
                return False, "PDF受密码保护，请提供密码！"
        
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        pdf_name = pdf_name.strip().rstrip('. ')
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(pdf_path), pdf_name)
        
        output_dir = os.path.normpath(output_dir)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        total_pages = doc.page_count
        page_images = []
        
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            
            if merge_pages:
                img_data = pix.tobytes("png")
                page_img = Image.open(io.BytesIO(img_data))
                page_images.append(page_img)
            else:
                image_path = os.path.normpath(os.path.join(output_dir, f"{pdf_name}_page_{page_num + 1:03d}.png"))
                pix.save(image_path)
            
            if progress_callback:
                progress_callback(page_num + 1, total_pages)
        
        doc.close()
        
        if merge_pages and page_images:
            trimmed_images = []
            total_pages = len(page_images)
            
            for index, img in enumerate(page_images):
                img_data = img.convert('RGB')
                width, height = img_data.size
                
                if index == 0:
                    top_crop = 0
                    bottom_crop = int(height * 0.02)
                elif index == total_pages - 1:
                    top_crop = int(height * 0.02)
                    bottom_crop = 0
                else:
                    top_crop = int(height * 0.02)
                    bottom_crop = int(height * 0.02)
                
                left = 0
                upper = top_crop
                right = width
                lower = height - bottom_crop
                
                trimmed_img = img_data.crop((left, upper, right, lower))
                trimmed_images.append(trimmed_img)
            
            widths, heights = zip(*(img.size for img in trimmed_images))
            
            total_width = max(widths)
            total_height = sum(heights)
            
            merged_img = Image.new('RGB', (total_width, total_height), (255, 255, 255))
            
            y_offset = 0
            for img in trimmed_images:
                x_offset = (total_width - img.size[0]) // 2
                merged_img.paste(img, (x_offset, y_offset))
                y_offset += img.size[1]
            
            merged_path = os.path.normpath(os.path.join(output_dir, f"{pdf_name}_merged.png"))
            merged_img.save(merged_path)
            
            return True, f"转换完成！合并后的图片已保存到:\n{merged_path}"
        else:
            return True, f"转换完成！图片已保存到:\n{output_dir}"
    
    except Exception as e:
        return False, f"转换失败: {str(e)}"


class PDFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF转图片工具")
        self.root.geometry("500x750")
        self.root.resizable(False, False)
        
        self.pdf_path = ""
        self.output_dir = ""
        self.password = ""
        self.merge_pages = tk.BooleanVar(value=False)
        
        self.create_widgets()
    
    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", padding=6, font=('微软雅黑', 10))
        style.configure("TLabel", font=('微软雅黑', 10))
        style.configure("TEntry", font=('微软雅黑', 10))
        
        # 选择PDF文件
        self.select_frame = ttk.LabelFrame(self.root, text="选择PDF文件", padding=15)
        self.select_frame.pack(pady=10, padx=10, fill="x")
        
        self.pdf_label = ttk.Label(self.select_frame, text="未选择文件", foreground="#666")
        self.pdf_label.pack(anchor="w", pady=5)
        
        self.select_btn = ttk.Button(self.select_frame, text="浏览选择PDF", command=self.select_pdf)
        self.select_btn.pack(anchor="w")
        
        # 密码输入（可选）
        self.password_frame = ttk.LabelFrame(self.root, text="PDF密码（可选）", padding=15)
        self.password_frame.pack(pady=10, padx=10, fill="x")
        
        self.password_label = ttk.Label(self.password_frame, text="如果PDF有密码，请输入：")
        self.password_label.pack(anchor="w", pady=5)
        
        self.password_entry = ttk.Entry(self.password_frame, show="*", width=40)
        self.password_entry.pack(anchor="w")
        
        # 合并选项
        self.merge_frame = ttk.LabelFrame(self.root, text="合并选项", padding=15)
        self.merge_frame.pack(pady=10, padx=10, fill="x")
        
        self.merge_check = ttk.Checkbutton(self.merge_frame, text="将所有页面合并成一张图片", variable=self.merge_pages)
        self.merge_check.pack(anchor="w")
        
        # 输出目录选择
        self.output_frame = ttk.LabelFrame(self.root, text="输出目录", padding=15)
        self.output_frame.pack(pady=10, padx=10, fill="x")
        
        self.output_label = ttk.Label(self.output_frame, text="默认：与PDF同名的文件夹", foreground="#666")
        self.output_label.pack(anchor="w", pady=5)
        
        self.output_btn = ttk.Button(self.output_frame, text="自定义输出目录", command=self.select_output_dir)
        self.output_btn.pack(anchor="w")
        
        # 进度条
        self.progress_frame = ttk.LabelFrame(self.root, text="转换进度", padding=15)
        self.progress_frame.pack(pady=10, padx=10, fill="x")
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="等待开始...")
        self.progress_label.pack(pady=5)
        
        # 转换按钮
        self.convert_btn = ttk.Button(self.root, text="开始转换", command=self.start_convert)
        self.convert_btn.pack(pady=20)
    
    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_path:
            self.pdf_path = file_path
            self.pdf_label.config(text=os.path.basename(file_path), foreground="#333")
    
    def select_output_dir(self):
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.config(text=dir_path, foreground="#333")
    
    def update_progress(self, current, total):
        progress = (current / total) * 100
        self.progress_bar["value"] = progress
        self.progress_label.config(text=f"正在转换：{current}/{total} 页")
        self.root.update_idletasks()
    
    def start_convert(self):
        if not self.pdf_path:
            messagebox.showwarning("警告", "请先选择PDF文件！")
            return
        
        self.password = self.password_entry.get()
        
        self.progress_bar["value"] = 0
        self.progress_label.config(text="准备转换...")
        self.convert_btn.config(state="disabled")
        self.root.update_idletasks()
        
        success, message = pdf_to_images(
            self.pdf_path,
            self.output_dir if self.output_dir else None,
            self.password if self.password else None,
            self.merge_pages.get(),
            self.update_progress
        )
        
        self.progress_bar["value"] = 100
        self.convert_btn.config(state="normal")
        
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("失败", message)


if __name__ == '__main__':
    install_dependencies()
    import io
    
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()