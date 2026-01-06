import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# --- تنظیمات پیش‌فرض ---
DEFAULT_IGNORE_LIST = [
    '.git', '.vscode', '__pycache__', 'node_modules', 'vendor',
    '.env', '.DS_Store', 'package-lock.json', 'composer.lock', 'backups', 'assets'
]

TEXT_FILE_EXTENSIONS = [
    '.php', '.js', '.css', '.html', '.sql', '.md', '.txt', '.json', '.xml',
    '.htaccess', '.py', '.sh', '.gitignore', '.ini', '.config', '.yml', '.yaml'
]

IGNORE_EXPLANATIONS = {
    '.git': "پوشه سورس کنترل Git (تاریخچه تغییرات)",
    '.vscode': "تنظیمات ویرایشگر کد VS Code",
    '__pycache__': "فایل‌های کش پایتون",
    'node_modules': "کتابخانه‌های جاوا اسکریپت (بسیار حجیم)",
    'vendor': "کتابخانه‌های PHP (بسیار حجیم)",
    '.env': "فایل متغیرهای محیطی (حاوی اطلاعات حساس)",
    '.DS_Store': "فایل سیستمی macOS",
    'package-lock.json': "فایل قفل نسخه کتابخانه‌های npm",
    'composer.lock': "فایل قفل نسخه کتابخانه‌های Composer",
    'backups': "پوشه فایل‌های پشتیبان تولید شده توسط برنامه"
}

def is_text_file(file_path):
    """بررسی می‌کند که آیا فایل متنی است یا باینری"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, IOError):
        return False

class ProjectPackagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Packager v3.0")
        self.root.geometry("850x700")
        
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X)

        # --- بخش انتخاب مسیرها (چپ) ---
        paths_frame = tk.LabelFrame(top_frame, text="۱. انتخاب مسیرها", padx=10, pady=10)
        paths_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.project_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        
        tk.Label(paths_frame, text="پوشه پروژه:").grid(row=0, column=0, sticky=tk.W, pady=2)
        tk.Entry(paths_frame, textvariable=self.project_path_var, width=60).grid(row=0, column=1, sticky=tk.EW, padx=5)
        tk.Button(paths_frame, text="انتخاب...", command=self.select_project_path).grid(row=0, column=2)

        tk.Label(paths_frame, text="فایل خروجی:").grid(row=1, column=0, sticky=tk.W, pady=2)
        tk.Entry(paths_frame, textvariable=self.output_path_var, width=60).grid(row=1, column=1, sticky=tk.EW, padx=5)
        tk.Button(paths_frame, text="انتخاب...", command=self.select_output_path).grid(row=1, column=2)
        paths_frame.grid_columnconfigure(1, weight=1)
        
        # --- بخش توضیحات (راست) ---
        explanation_frame = tk.LabelFrame(top_frame, text="توضیحات لیست Ignore", padx=10, pady=10)
        explanation_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        explanation_text = scrolledtext.ScrolledText(explanation_frame, wrap=tk.WORD, height=4, width=35, relief=tk.FLAT, bg=root.cget('bg'))
        for item, desc in IGNORE_EXPLANATIONS.items():
            explanation_text.insert(tk.END, f"{item}: {desc}\n")
        explanation_text.config(state=tk.DISABLED)
        explanation_text.pack(fill=tk.BOTH, expand=True)

        # --- بخش مدیریت لیست Ignore ---
        ignore_frame = tk.LabelFrame(main_frame, text="۲. مدیریت لیست نادیده‌گرفته‌شده‌ها (Ignore List)", padx=10, pady=10)
        ignore_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.ignore_listbox = tk.Listbox(ignore_frame, height=8)
        for item in DEFAULT_IGNORE_LIST:
            self.ignore_listbox.insert(tk.END, item)
        self.ignore_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ignore_controls_frame = tk.Frame(ignore_frame)
        ignore_controls_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.ignore_entry_var = tk.StringVar()
        tk.Entry(ignore_controls_frame, textvariable=self.ignore_entry_var).pack(fill=tk.X, pady=2)
        tk.Button(ignore_controls_frame, text="افزودن", command=self.add_to_ignore_list).pack(fill=tk.X, pady=2)
        tk.Button(ignore_controls_frame, text="حذف انتخاب شده", command=self.remove_from_ignore_list).pack(fill=tk.X, pady=2)
        
        # --- بخش گزارش و اجرا ---
        self.start_button = tk.Button(main_frame, text="شروع تجمیع پروژه", bg="#28a745", fg="white", font=('Arial', 12, 'bold'), command=self.run_packaging)
        self.start_button.pack(fill=tk.X, ipady=5, pady=5)

        log_frame = tk.LabelFrame(main_frame, text="گزارش عملیات", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def select_project_path(self):
        path = filedialog.askdirectory(title="پوشه پروژه را انتخاب کنید")
        if path:
            self.project_path_var.set(path)
            # Suggest a default output file name based on the project folder
            project_name = os.path.basename(path)
            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            self.output_path_var.set(os.path.join(desktop_path, f"{project_name}_bundle.txt"))

    def select_output_path(self):
        path = filedialog.asksaveasfilename(title="محل ذخیره فایل خروجی", defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            self.output_path_var.set(path)
            
    def add_to_ignore_list(self):
        item = self.ignore_entry_var.get().strip()
        if item and item not in self.ignore_listbox.get(0, tk.END):
            self.ignore_listbox.insert(tk.END, item)
            self.ignore_entry_var.set("")
            
    def remove_from_ignore_list(self):
        selected_indices = self.ignore_listbox.curselection()
        for i in reversed(selected_indices):
            self.ignore_listbox.delete(i)
            
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
            
    def run_packaging(self):
        project_path = self.project_path_var.get()
        output_file = self.output_path_var.get()
        ignore_list = list(self.ignore_listbox.get(0, tk.END))

        if not project_path or not output_file:
            messagebox.showerror("خطا", "لطفاً مسیر پروژه و فایل خروجی را مشخص کنید.")
            return

        self.start_button.config(state=tk.DISABLED, text="در حال پردازش...")
        self.log_text.delete('1.0', tk.END)
        
        files_processed = 0
        ignored_files_log = []

        try:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                header = f"شروع تجمیع پروژه از مسیر: {os.path.abspath(project_path)}"
                self.log(header)
                outfile.write("=" * 80 + "\n" + header + "\n" + "=" * 80 + "\n\n")

                for root, dirs, files in os.walk(project_path):
                    dirs[:] = [d for d in dirs if d not in ignore_list]

                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, project_path)
                        
                        reason_to_ignore = ""
                        if file in ignore_list or any(part in ignore_list for part in relative_path.split(os.sep)):
                            reason_to_ignore = "در لیست Ignore"
                        elif os.path.splitext(file)[1].lower() not in TEXT_FILE_EXTENSIONS:
                             reason_to_ignore = "پسوند غیرمتنی"
                        elif not is_text_file(file_path):
                             reason_to_ignore = "فایل باینری"

                        if reason_to_ignore:
                            ignored_files_log.append(f"- {relative_path} ({reason_to_ignore})")
                            continue
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                
                                file_header = f"FILE: {relative_path.replace(os.sep, '/')}"
                                self.log(f"Processing: {relative_path}")
                                outfile.write("-" * 80 + "\n" + file_header + "\n" + "-" * 80 + "\n\n")
                                outfile.write(content)
                                outfile.write("\n\n")
                                files_processed += 1
                        except Exception as e:
                            ignored_files_log.append(f"- {relative_path} (خطا در خواندن: {e})")
                            self.log(f"ERROR reading {relative_path}: {e}")

                footer = f"پایان تجمیع. فایل‌های پردازش شده: {files_processed}, فایل‌های نادیده گرفته شده: {len(ignored_files_log)}"
                self.log("\n" + "=" * 30)
                self.log(footer)
                outfile.write("=" * 80 + "\n" + footer + "\n" + "=" * 80 + "\n")

                if ignored_files_log:
                    self.log("\nلیست فایل‌های نادیده گرفته شده:")
                    for log_entry in ignored_files_log:
                        self.log(log_entry)

            messagebox.showinfo("عملیات موفق", f"پروژه با موفقیت در فایل '{output_file}' تجمیع شد.")

        except IOError as e:
            messagebox.showerror("خطا", f"خطا در نوشتن فایل خروجی: {e}")
        finally:
            self.start_button.config(state=tk.NORMAL, text="شروع تجمیع پروژه")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectPackagerApp(root)
    root.mainloop()