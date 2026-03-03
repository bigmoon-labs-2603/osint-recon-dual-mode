import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from osint_core import collect_osint, save_json


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("OSINT Recon Dual Mode - GUI")
        self.root.geometry("920x640")

        top = tk.Frame(root)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text="Target:").pack(side="left")
        self.target = tk.Entry(top)
        self.target.pack(side="left", fill="x", expand=True, padx=8)
        self.target.insert(0, "example.com")

        tk.Button(top, text="开始收集", command=self.run_collect).pack(side="left", padx=5)
        tk.Button(top, text="保存JSON", command=self.save_result).pack(side="left")

        self.output = scrolledtext.ScrolledText(root, wrap="word")
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.result = None

    def run_collect(self):
        t = self.target.get().strip()
        if not t:
            messagebox.showwarning("提示", "请输入目标")
            return
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "[+] collecting...\n")
        self.root.update_idletasks()

        try:
            self.result = collect_osint(t)
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, json.dumps(self.result, ensure_ascii=False, indent=2))
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def save_result(self):
        if not self.result:
            messagebox.showinfo("提示", "先执行一次收集")
            return
        f = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not f:
            return
        save_json(self.result, f)
        messagebox.showinfo("完成", f"已保存: {f}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
