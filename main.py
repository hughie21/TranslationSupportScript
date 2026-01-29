import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile
from fetch import fetch_original_text, clear_empty_text
from format import get_all_chaters_from_zip, get_trans_from_zip, format_translated_text, get_single_chapter
import pandas as pd
import threading
import time
from tqdm import tqdm

class TranslationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("翻译工具 - 原文获取与译文整合")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # 创建笔记本（选项卡）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 选项卡1：获取原文
        self.fetch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fetch_frame, text="获取原文")
        self.setup_fetch_tab()
        
        # 选项卡2：整合译文
        self.format_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.format_frame, text="整合译文")
        self.setup_format_tab()
        
    def setup_fetch_tab(self):
        """设置获取原文选项卡"""
        main_frame = ttk.LabelFrame(self.fetch_frame, text="原文获取设置", padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 开始章节
        ttk.Label(main_frame, text="开始章节:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_chapter = ttk.Entry(main_frame, width=10)
        self.start_chapter.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.start_chapter.insert(0, "1")
        
        # 结束章节
        ttk.Label(main_frame, text="结束章节:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_chapter = ttk.Entry(main_frame, width=10)
        self.end_chapter.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.end_chapter.insert(0, "2")
        
        # 是否包含机翻复选框
        self.include_trans = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="包含机翻译文", variable=self.include_trans).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=10
        )
        
        # 输出路径
        ttk.Label(main_frame, text="输出路径:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.output_path = ttk.Entry(main_frame, width=40)
        self.output_path.grid(row=3, column=1, sticky=tk.EW, padx=5)
        self.output_path.insert(0, "./chapter")
        
        ttk.Button(main_frame, text="浏览...", command=self.browse_output_path).grid(
            row=3, column=2, padx=5
        )
        
        # 进度条
        ttk.Label(main_frame, text="进度:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.fetch_progress = ttk.Progressbar(main_frame, mode='determinate')
        self.fetch_progress.grid(row=4, column=1, columnspan=2, sticky=tk.EW, padx=5)
        
        # 状态标签
        self.fetch_status = ttk.Label(main_frame, text="就绪", foreground="green")
        self.fetch_status.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 获取按钮
        ttk.Button(main_frame, text="开始获取", command=self.fetch_chapters).grid(
            row=6, column=0, columnspan=3, pady=20
        )
        
    def setup_format_tab(self):
        """设置整合译文选项卡"""
        main_frame = ttk.LabelFrame(self.format_frame, text="译文整合设置", padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 选择ZIP文件
        ttk.Label(main_frame, text="ZIP文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.zip_path = ttk.Entry(main_frame, width=40)
        self.zip_path.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        ttk.Button(main_frame, text="浏览...", command=self.browse_zip_file).grid(
            row=0, column=2, padx=5
        )
        
        ttk.Button(main_frame, text="加载章节", command=self.load_chapters).grid(
            row=0, column=3, padx=5
        )
        
        # 章节树状图
        ttk.Label(main_frame, text="章节列表:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=4, sticky=tk.NSEW, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chapter_tree = ttk.Treeview(list_frame, show="tree", selectmode="browse", yscrollcommand=scrollbar.set)
        self.chapter_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chapter_tree.yview)
        
        # 输出文件
        ttk.Label(main_frame, text="输出文件:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.format_output_path = ttk.Entry(main_frame, width=40)
        self.format_output_path.grid(row=3, column=1, sticky=tk.EW, padx=5)
        self.format_output_path.insert(0, "formatted_translated_text.md")
        
        ttk.Button(main_frame, text="浏览...", command=self.browse_output_file).grid(
            row=3, column=2, padx=5
        )
        
        # 状态标签
        self.format_status = ttk.Label(main_frame, text="就绪", foreground="green")
        self.format_status.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # 整合按钮
        ttk.Button(main_frame, text="整合选中章节/单节", command=self.format_translation).grid(
            row=5, column=0, columnspan=4, pady=20
        )
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def browse_output_path(self):
        path = filedialog.askdirectory(title="选择输出文件夹")
        if path:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, path)
    
    def browse_zip_file(self):
        path = filedialog.askopenfilename(
            title="选择ZIP文件",
            filetypes=[("ZIP文件", "*.zip"), ("所有文件", "*.*")]
        )
        if path:
            self.zip_path.delete(0, tk.END)
            self.zip_path.insert(0, path)
    
    def browse_output_file(self):
        path = filedialog.asksaveasfilename(
            title="保存整合文件",
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if path:
            self.format_output_path.delete(0, tk.END)
            self.format_output_path.insert(0, path)
    
    def _list_chapter_csvs(self, zip_path, data_dir):
        """列出某个大章节下的所有CSV文件（相对路径）"""
        csvs = []
        target_prefix = f"utf8/{data_dir}/"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for name in zf.namelist():
                if name.startswith(target_prefix) and name.endswith(".csv"):
                    csvs.append(name)
        return sorted(csvs)
    
    def fetch_chapters(self):
        """在后台线程中获取原文"""
        try:
            start = int(self.start_chapter.get())
            end = int(self.end_chapter.get())
            output_path = self.output_path.get()
            include_trans = self.include_trans.get()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的章节号")
            return
        
        # 在后台线程运行
        thread = threading.Thread(
            target=self._fetch_chapters_thread,
            args=(start, end, output_path, include_trans)
        )
        thread.daemon = True
        thread.start()
    
    def _fetch_chapters_thread(self, start, end, output_path, include_trans):
        """获取章节的后台线程"""
        try:
            self.fetch_status.config(text="正在获取中...", foreground="blue")
            self.root.update()
            
            total = end - start + 1
            self.fetch_progress['maximum'] = total
            
            for i, chapter in enumerate(range(start, end + 1)):
                original_text, translated_text, title = fetch_original_text(
                    chapter, include_trans=include_trans
                )
                
                original_text = clear_empty_text(original_text)
                
                df = pd.DataFrame({
                    "original_text": original_text,
                    "translated_text": translated_text if include_trans else [""] * len(original_text)
                })
                
                df.to_csv(
                    f"{output_path}/chapter_{chapter}_{title}.csv",
                    index=True, header=False
                )
                
                self.fetch_progress['value'] = i + 1
                self.fetch_status.config(
                    text=f"已获取 {i+1}/{total} 章节",
                    foreground="blue"
                )
                self.root.update()
                
                time.sleep(1)
            
            self.fetch_status.config(text="获取完成！", foreground="green")
            messagebox.showinfo("成功", f"已获取 {total} 个章节到 {output_path}")
            
        except Exception as e:
            self.fetch_status.config(text=f"错误: {str(e)}", foreground="red")
            messagebox.showerror("错误", f"获取失败: {str(e)}")
    
    def load_chapters(self):
        """加载ZIP文件中的章节"""
        zip_path = self.zip_path.get()
        if not zip_path:
            messagebox.showwarning("警告", "请先选择ZIP文件")
            return
        
        try:
            chapters = get_all_chaters_from_zip(zip_path)
            self.chapter_tree.delete(*self.chapter_tree.get_children())
            
            for chapter in chapters:
                chapter_id = self.chapter_tree.insert(
                    "", tk.END, text=chapter, values=("chapter", chapter, "")
                )
                csvs = self._list_chapter_csvs(zip_path, chapter)
                for csv_file in csvs:
                    # 只显示文件名
                    display_name = csv_file.split("/")[-1]
                    self.chapter_tree.insert(
                        chapter_id, tk.END, text=display_name,
                        values=("section", chapter, csv_file)
                    )
            
            self.format_status.config(
                text=f"已加载 {len(chapters)} 个章节",
                foreground="green"
            )
        except Exception as e:
            self.format_status.config(text=f"错误: {str(e)}", foreground="red")
            messagebox.showerror("错误", f"加载失败: {str(e)}")
    
    def format_translation(self):
        """整合选中的章节"""
        zip_path = self.zip_path.get()
        output_file = self.format_output_path.get()
        
        selection = self.chapter_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择章节或单节")
            return
        
        if not zip_path or not output_file:
            messagebox.showwarning("警告", "请指定ZIP文件和输出文件")
            return
        
        try:
            self.format_status.config(text="正在整合...", foreground="blue")
            self.root.update()
            
            item = selection[0]
            kind, chapter, csv_file = self.chapter_tree.item(item, "values")
            
            if kind == "chapter":
                translated_text = get_trans_from_zip(zip_path, chapter)
                if len(translated_text) == 0:
                    messagebox.showwarning("警告", "所选章节没有译文可整合")
                    self.format_status.config(text="就绪", foreground="green")
                    return
                format_translated_text(translated_text, output_file)
                msg = f"已整合整章 {chapter} 到 {output_file}"
            else:
                translated_text = get_single_chapter(zip_path, chapter, csv_file)
                if len(translated_text) == 0:
                    messagebox.showwarning("警告", "所选单节没有译文可整合")
                    self.format_status.config(text="就绪", foreground="green")
                    return
                format_translated_text(translated_text, output_file)
                msg = f"已整合单节 {csv_file} 到 {output_file}"
            
            self.format_status.config(text="整合完成！", foreground="green")
            messagebox.showinfo("成功", msg)
            
        except Exception as e:
            self.format_status.config(text=f"错误: {str(e)}", foreground="red")
            messagebox.showerror("错误", f"整合失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationGUI(root)
    root.mainloop()