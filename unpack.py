import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re

class ProjectUnpackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Unpacker v1.0")
        self.root.geometry("800x500")
        
        # --- فریم اصلی ---
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- بخش انتخاب مسیرها ---
        paths_frame = tk.LabelFrame(main_frame, text="۱. انتخاب فایل ورودی و پوشه مقصد", padx=10, pady=10)
        paths_frame.pack(fill=tk.X, pady=5)
        
        self.input_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        
        tk.Label(paths_frame, text="فایل تجمیع‌شده (.txt):").grid(row=0, column=0, sticky=tk.W, pady=2)
        tk.Entry(paths_frame, textvariable=self.input_file_var, width=70).grid(row=0, column=1, sticky=tk.EW, padx=5)
        tk.Button(paths_frame, text="انتخاب فایل...", command=self.select_input_file).grid(row=0, column=2)

        tk.Label(paths_frame, text="پوشه مقصد برای بازسازی:").grid(row=1, column=0, sticky=tk.W, pady=2)
        tk.Entry(paths_frame, textvariable=self.output_dir_var, width=70).grid(row=1, column=1, sticky=tk.EW, padx=5)
        tk.Button(paths_frame, text="انتخاب پوشه...", command=self.select_output_dir).grid(row=1, column=2)
        
        paths_frame.grid_columnconfigure(1, weight=1)
        
        # --- بخش گزارش و اجرا ---
        action_frame = tk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = tk.Button(action_frame, text="شروع بازسازی پروژه", bg="#0d6efd", fg="white", font=('Arial', 12, 'bold'), command=self.run_unpacking)
        self.start_button.pack(fill=tk.X, ipady=5)

        log_frame = tk.LabelFrame(main_frame, text="گزارش عملیات", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def select_input_file(self):
        path = filedialog.askopenfilename(
            title="فایل تجمیع‌شده را انتخاب کنید",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            self.input_file_var.set(path)

    def select_output_dir(self):
        path = filedialog.askdirectory(title="پوشه‌ای که پروژه در آن بازسازی می‌شود را انتخاب کنید")
        if path:
            self.output_dir_var.set(path)
            
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
            
    def run_unpacking(self):
        input_file = self.input_file_var.get()
        output_dir = self.output_dir_var.get()

        if not input_file or not output_dir:
            messagebox.showerror("خطا", "لطفاً فایل ورودی و پوشه مقصد را مشخص کنید.")
            return

        if not os.path.isfile(input_file):
            messagebox.showerror("خطا", f"فایل ورودی یافت نشد:\n{input_file}")
            return
            
        if os.listdir(output_dir):
            if not messagebox.askyesno("تایید", f"پوشه مقصد '{os.path.basename(output_dir)}' خالی نیست.\nممکن است فایل‌های موجود بازنویسی شوند.\n\nآیا ادامه می‌دهید؟"):
                return

        self.start_button.config(state=tk.DISABLED, text="در حال بازسازی...")
        self.log_text.delete('1.0', tk.END)
        
        files_created = 0
        current_file_path = None
        current_content = []

        try:
            with open(input_file, 'r', encoding='utf-8') as infile:
                for line in infile:
                    # Regex to find the file header, e.g., "FILE: path/to/file.js"
                    match = re.match(r'^-*FILE: (.*)-*$', line.strip())

                    if match:
                        # If we were processing a file, save it first
                        if current_file_path and current_content:
                            full_path = os.path.join(output_dir, current_file_path)
                            os.makedirs(os.path.dirname(full_path), exist_ok=True)
                            with open(full_path, 'w', encoding='utf-8') as outfile:
                                # Join content, stripping the last two newlines added during packaging
                                outfile.write("".join(current_content).rstrip('\n'))
                            self.log(f"فایل ایجاد شد: {current_file_path}")
                            files_created += 1
                        
                        # Start processing the new file
                        current_file_path = match.group(1).strip().replace('/', os.sep)
                        current_content = []
                    elif current_file_path and "--------------------------------------------------------------------------------" not in line:
                        # Append content to the current file buffer
                        current_content.append(line)

            # Save the very last file in the bundle
            if current_file_path and current_content:
                full_path = os.path.join(output_dir, current_file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as outfile:
                    outfile.write("".join(current_content).rstrip('\n'))
                self.log(f"فایل ایجاد شد: {current_file_path}")
                files_created += 1

            self.log("\n" + "=" * 30)
            self.log(f"عملیات بازسازی با موفقیت به پایان رسید.")
            self.log(f"تعداد فایل‌های ایجاد شده: {files_created}")
            messagebox.showinfo("عملیات موفق", f"{files_created} فایل با موفقیت در پوشه مقصد بازسازی شد.")

        except Exception as e:
            messagebox.showerror("خطا", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
        finally:
            self.start_button.config(state=tk.NORMAL, text="شروع بازسازی پروژه")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectUnpackerApp(root)
    root.mainloop()