import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from batch_utils import run_batch
from osint_core import collect_osint, save_json
from report_export import export_docx, export_markdown


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("OSINT Recon Dual Mode - GUI")
        self.root.geometry("1100x760")

        top = tk.Frame(root)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text="Target:").grid(row=0, column=0, sticky="w")
        self.target = tk.Entry(top, width=52)
        self.target.grid(row=0, column=1, sticky="ew", padx=8)
        self.target.insert(0, "example.com")

        tk.Label(top, text="Targets File:").grid(row=1, column=0, sticky="w")
        self.targets_file = tk.Entry(top, width=52)
        self.targets_file.grid(row=1, column=1, sticky="ew", padx=8)
        tk.Button(top, text="选择文件", command=self.pick_targets_file).grid(row=1, column=2, padx=6)

        self.verify_tls = tk.BooleanVar(value=True)
        self.with_subdomains = tk.BooleanVar(value=True)
        tk.Checkbutton(top, text="Verify TLS", variable=self.verify_tls).grid(row=0, column=2, padx=6)
        tk.Checkbutton(top, text="Passive subdomains", variable=self.with_subdomains).grid(row=0, column=3, padx=6)

        tk.Label(top, text="Workers:").grid(row=1, column=3, sticky="e")
        self.workers = tk.Entry(top, width=5)
        self.workers.grid(row=1, column=4, sticky="w")
        self.workers.insert(0, "5")

        tk.Button(top, text="开始收集", command=self.run_collect_async).grid(row=0, column=4, padx=5)
        tk.Button(top, text="保存JSON", command=self.save_json_result).grid(row=0, column=5, padx=5)
        tk.Button(top, text="导出MD", command=self.export_md).grid(row=1, column=5, padx=5)
        tk.Button(top, text="导出DOCX", command=self.export_docx).grid(row=1, column=6, padx=5)

        top.columnconfigure(1, weight=1)

        self.output = scrolledtext.ScrolledText(root, wrap="word")
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.result = None

    def pick_targets_file(self):
        f = filedialog.askopenfilename(title="选择目标列表", filetypes=[("Text", "*.txt"), ("All files", "*.*")])
        if f:
            self.targets_file.delete(0, tk.END)
            self.targets_file.insert(0, f)

    def run_collect_async(self):
        th = threading.Thread(target=self.run_collect, daemon=True)
        th.start()

    def run_collect(self):
        t = self.target.get().strip()
        tf = self.targets_file.get().strip()

        if not t and not tf:
            messagebox.showwarning("提示", "请输入目标或选择目标列表文件")
            return

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "[+] collecting...\n")
        self.root.update_idletasks()

        try:
            if tf:
                with open(tf, "r", encoding="utf-8") as f:
                    targets = [x.strip() for x in f if x.strip() and not x.strip().startswith("#")]
                workers = int(self.workers.get() or "5")
                self.result = run_batch(
                    targets,
                    workers=workers,
                    verify_tls=self.verify_tls.get(),
                    with_subdomains=self.with_subdomains.get(),
                )
            else:
                self.result = collect_osint(
                    t,
                    verify_tls=self.verify_tls.get(),
                    with_subdomains=self.with_subdomains.get(),
                )

            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, json.dumps(self.result, ensure_ascii=False, indent=2))
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def save_json_result(self):
        if self.result is None:
            messagebox.showinfo("提示", "先执行一次收集")
            return
        f = filedialog.asksaveasfilename(title="保存结果", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not f:
            return
        save_json(self.result, f)
        messagebox.showinfo("完成", f"已保存: {f}")

    def export_md(self):
        if self.result is None:
            messagebox.showinfo("提示", "先执行一次收集")
            return
        f = filedialog.asksaveasfilename(title="导出 Markdown", defaultextension=".md", filetypes=[("Markdown", "*.md")])
        if not f:
            return
        export_markdown(self.result, f)
        messagebox.showinfo("完成", f"已导出: {f}")

    def export_docx(self):
        if self.result is None:
            messagebox.showinfo("提示", "先执行一次收集")
            return
        f = filedialog.asksaveasfilename(title="导出 DOCX", defaultextension=".docx", filetypes=[("DOCX", "*.docx")])
        if not f:
            return
        export_docx(self.result, f)
        messagebox.showinfo("完成", f"已导出: {f}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
