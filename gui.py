import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time
import string

# -------------------- 公共函数 --------------------
def finish_and_close(root, result):
    root.result = result
    root.destroy()

def random_case_string(s):
    return ''.join(random.choice([c.upper(), c.lower()]) for c in s)

# ==================== 版本1：按钮混淆 ====================
def uninstall_program1(package_name):
    root = tk.Tk()
    root.title(f"{package_name} 卸载程序")
    root.geometry("500x450")
    root.resizable(False, False)
    root.result = False
    step = [0]

    def show_step(idx):
        for w in root.winfo_children():
            w.destroy()
        if idx == 0: step0()
        elif idx == 1: step1()
        elif idx == 2: step2()
        elif idx == 3: step3()
        elif idx == 4: step4()
        elif idx == 5: success()

    def step0():
        tk.Label(root, text=f"您确定要卸载 {package_name} 吗？", font=("Arial", 12)).pack(pady=20)
        tk.Button(root, text="取消卸载", font=("Arial", 14, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)
        tk.Button(root, text="继续卸载", font=("Arial", 8), bg="lightgray", fg="gray",
                  command=lambda: next_step(0)).pack(pady=5)
        tk.Button(root, text="重新安装", command=lambda: messagebox.showinfo("提示", "重新安装需要联网")).pack(pady=5)

    def step1():
        target = random_case_string("UNINSTALL")
        tk.Label(root, text="请输入以下文字（注意大小写）：", font=("Arial", 10)).pack(pady=10)
        tk.Label(root, text=target, font=("Courier", 20, "bold"), fg="red").pack(pady=5)
        entry = ttk.Entry(root)
        entry.pack(pady=5)
        entry.focus()
        def check():
            if entry.get() == target:
                next_step(1)
            else:
                messagebox.showerror("错误", "输入不匹配，请重试")
                entry.delete(0, tk.END)
        ttk.Button(root, text="确认", command=check).pack(pady=10)
        entry.bind('<Return>', lambda e: check())
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)

    def step2():
        tk.Label(root, text="正在扫描文件...", font=("Arial", 12)).pack(pady=10)
        progress = ttk.Progressbar(root, mode='determinate', length=400)
        progress.pack(pady=20)
        status = tk.Label(root, text="0%")
        status.pack()
        def simulate():
            cur = 0
            while cur < 100:
                root.after(0, lambda: progress.config(value=cur))
                root.after(0, lambda: status.config(text=f"{cur}%"))
                time.sleep(0.08)
                cur += random.randint(1, 5)
                if cur >= 100:
                    cur = 100
                    root.after(0, lambda: progress.config(value=100))
                    root.after(0, lambda: status.config(text="100%"))
                    root.after(0, lambda: next_step(2))
                    break
        threading.Thread(target=simulate, daemon=True).start()
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=10)

    def step3():
        tk.Label(root, text="请点击真正的“卸载”按钮", font=("Arial", 12)).pack(pady=10)
        true_idx = random.randint(0, 4)
        for i in range(5):
            if i == true_idx:
                btn = tk.Button(root, text="卸载", bg="lightgray", fg="gray",
                                command=lambda: next_step(3))
            else:
                texts = ["取消", "重新安装", "跳过", "忽略", "返回"]
                text = random.choice(texts)
                btn = tk.Button(root, text=text,
                                command=lambda t=text: messagebox.showinfo("提示", f"您点了“{t}”，这不是卸载"))
            btn.pack(pady=5, fill=tk.X, padx=50)

    def step4():
        tk.Label(root, text="正在处理...", font=("Arial", 12)).pack(pady=10)
        count = [0]
        order = ["要", "不要", "要"]
        random.shuffle(order)
        def popup():
            if count[0] >= 3:
                next_step(4)
                return
            current = order[count[0]]
            count[0] += 1
            if current == "不要":
                ans = messagebox.askquestion("警告", f"确定不要卸载 {package_name} 吗？")
                if ans == 'yes':
                    finish_and_close(root, False)
                else:
                    root.after(100, popup)
            else:
                ans = messagebox.askquestion("确认", f"确定要卸载 {package_name} 吗？({count[0]}/3)")
                if ans == 'yes':
                    root.after(100, popup)
                else:
                    finish_and_close(root, False)
        root.after(500, popup)
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=20)

    def success():
        tk.Label(root, text=f"🎉 {package_name} 卸载成功！", font=("Arial", 14, "bold"), fg="green").pack(pady=30)
        # 两个按钮都失败
        tk.Button(root, text="再见", font=("Arial", 14, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=20)
        tk.Button(root, text="重新安装", command=lambda: finish_and_close(root, False)).pack(pady=5)
        # 关闭窗口算成功
        root.protocol("WM_DELETE_WINDOW", lambda: finish_and_close(root, True))

    def next_step(step_idx):
        step[0] = step_idx + 1
        show_step(step[0])

    # 默认关闭窗口失败（中途取消）
    root.protocol("WM_DELETE_WINDOW", lambda: finish_and_close(root, False))
    show_step(0)
    root.mainloop()
    return root.result

# ==================== 版本2：验证码+多步确认 ====================
def uninstall_program2(package_name):
    root = tk.Tk()
    root.title(f"{package_name} 卸载程序")
    root.geometry("500x450")
    root.resizable(False, False)
    root.result = False
    step = [0]

    def show_step(idx):
        for w in root.winfo_children():
            w.destroy()
        if idx == 0: step0()
        elif idx == 1: step1()
        elif idx == 2: step2()
        elif idx == 3: step3()
        elif idx == 4: step4()
        elif idx == 5: success()

    def step0():
        tk.Label(root, text=f"您确定要卸载 {package_name} 吗？", font=("Arial", 12)).pack(pady=20)
        tk.Button(root, text="取消卸载", font=("Arial", 14, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)
        tk.Button(root, text="继续卸载", font=("Arial", 8), bg="lightgray", fg="gray",
                  command=lambda: next_step(0)).pack(pady=5)
        tk.Button(root, text="确定不要卸载吗", command=lambda: finish_and_close(root, False)).pack(pady=5)

    def step1():
        target = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        tk.Label(root, text="请输入以下验证码（区分大小写）：", font=("Arial", 10)).pack(pady=10)
        tk.Label(root, text=target, font=("Courier", 20, "bold"), fg="blue").pack(pady=5)
        entry = ttk.Entry(root)
        entry.pack(pady=5)
        entry.focus()
        def check():
            if entry.get() == target:
                next_step(1)
            else:
                messagebox.showerror("错误", "验证码错误")
                entry.delete(0, tk.END)
        ttk.Button(root, text="确认", command=check).pack(pady=10)
        entry.bind('<Return>', lambda e: check())
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)

    def step2():
        tk.Label(root, text="正在清理残留...", font=("Arial", 12)).pack(pady=10)
        progress = ttk.Progressbar(root, mode='determinate', length=400)
        progress.pack(pady=20)
        status = tk.Label(root, text="0%")
        status.pack()
        def simulate():
            cur = 0
            while cur < 100:
                root.after(0, lambda: progress.config(value=cur))
                root.after(0, lambda: status.config(text=f"{cur}%"))
                time.sleep(0.1)
                cur += random.randint(1, 5)
                if cur >= 100:
                    cur = 100
                    root.after(0, lambda: progress.config(value=100))
                    root.after(0, lambda: status.config(text="100%"))
                    root.after(0, lambda: next_step(2))
                    break
        threading.Thread(target=simulate, daemon=True).start()
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=10)

    def step3():
        tk.Label(root, text="请点击正确的“卸载”按钮", font=("Arial", 12)).pack(pady=10)
        true_idx = random.randint(0, 5)
        for i in range(6):
            if i == true_idx:
                btn = tk.Button(root, text="卸载", bg="lightgray", fg="gray",
                                command=lambda: next_step(3))
            else:
                texts = ["取消", "重新安装", "不卸载", "忽略", "返回", "确定不要卸载吗", "跳过"]
                text = random.choice(texts)
                btn = tk.Button(root, text=text,
                                command=lambda t=text: messagebox.showinfo("提示", f"这不是卸载按钮"))
            btn.pack(pady=5, fill=tk.X, padx=50)

    def step4():
        tk.Label(root, text="请响应弹窗...", font=("Arial", 12)).pack(pady=10)
        count = [0]
        order = ["要", "不要", "要"]
        random.shuffle(order)
        def popup():
            if count[0] >= 3:
                next_step(4)
                return
            current = order[count[0]]
            count[0] += 1
            if current == "不要":
                ans = messagebox.askquestion("警告", f"确定不要卸载 {package_name} 吗？")
                if ans == 'yes':
                    finish_and_close(root, False)
                else:
                    root.after(100, popup)
            else:
                ans = messagebox.askquestion("确认", f"确定要卸载 {package_name} 吗？({count[0]}/3)")
                if ans == 'yes':
                    root.after(100, popup)
                else:
                    finish_and_close(root, False)
        root.after(500, popup)
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=20)

    def success():
        tk.Label(root, text=f"🎉 {package_name} 卸载成功！", font=("Arial", 14, "bold"), fg="green").pack(pady=30)
        tk.Button(root, text="再见", font=("Arial", 14, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=20)
        tk.Button(root, text="重新安装", command=lambda: finish_and_close(root, False)).pack(pady=5)
        root.protocol("WM_DELETE_WINDOW", lambda: finish_and_close(root, True))

    def next_step(step_idx):
        step[0] = step_idx + 1
        show_step(step[0])

    root.protocol("WM_DELETE_WINDOW", lambda: finish_and_close(root, False))
    show_step(0)
    root.mainloop()
    return root.result

# ==================== 版本3：反转输入+滑块 ====================
def uninstall_program3(package_name):
    root = tk.Tk()
    root.title(f"{package_name} 卸载程序")
    root.geometry("500x450")
    root.resizable(False, False)
    root.result = False
    step = [0]

    def show_step(idx):
        for w in root.winfo_children():
            w.destroy()
        if idx == 0: step0()
        elif idx == 1: step1()
        elif idx == 2: step2()
        elif idx == 3: step3()
        elif idx == 4: step4()
        elif idx == 5: success()

    def step0():
        tk.Label(root, text=f"您确定要卸载 {package_name} 吗？", font=("Arial", 12)).pack(pady=20)
        tk.Button(root, text="取消卸载", font=("Arial", 14, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)
        tk.Button(root, text="继续卸载", font=("Arial", 8), bg="lightgray", fg="gray",
                  command=lambda: next_step(0)).pack(pady=5)
        tk.Button(root, text="重新安装", command=lambda: messagebox.showinfo("提示", "重新安装需要联网")).pack(pady=5)

    def step1():
        tk.Label(root, text="请输入 'NO' 以继续，或 'YES' 取消", font=("Arial", 10)).pack(pady=10)
        entry = ttk.Entry(root)
        entry.pack(pady=5)
        entry.focus()
        def check():
            val = entry.get().strip().upper()
            if val == "NO":
                next_step(1)
            elif val == "YES":
                finish_and_close(root, False)
            else:
                messagebox.showerror("错误", "请输入 NO 或 YES")
                entry.delete(0, tk.END)
        ttk.Button(root, text="确认", command=check).pack(pady=10)
        entry.bind('<Return>', lambda e: check())
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)

    def step2():
        tk.Label(root, text="正在删除文件...", font=("Arial", 12)).pack(pady=10)
        progress = ttk.Progressbar(root, mode='determinate', length=400)
        progress.pack(pady=20)
        status = tk.Label(root, text="0%")
        status.pack()
        def simulate():
            cur = 0
            while cur < 100:
                root.after(0, lambda: progress.config(value=cur))
                root.after(0, lambda: status.config(text=f"{cur}%"))
                time.sleep(0.1)
                cur += random.randint(1, 5)
                if cur >= 100:
                    cur = 100
                    root.after(0, lambda: progress.config(value=100))
                    root.after(0, lambda: status.config(text="100%"))
                    root.after(0, lambda: next_step(2))
                    break
        threading.Thread(target=simulate, daemon=True).start()
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=10)

    def step3():
        tk.Label(root, text="请将滑块拖到最右侧", font=("Arial", 10)).pack(pady=10)
        slider = ttk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, length=300)
        slider.pack(pady=20)
        btn = ttk.Button(root, text="确认", state=tk.DISABLED,
                         command=lambda: next_step(3))
        btn.pack(pady=10)
        def on_move(val):
            if float(val) >= 99:
                btn.config(state=tk.NORMAL)
            else:
                btn.config(state=tk.DISABLED)
        slider.config(command=on_move)
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)

    def step4():
        tk.Label(root, text="正在卸载...", font=("Arial", 12)).pack(pady=10)
        count = [0]
        def popup():
            if count[0] >= 3:
                next_step(4)
                return
            count[0] += 1
            ans = messagebox.askquestion("确认", f"确定要卸载 {package_name} 吗？({count[0]}/3)")
            if ans == 'yes':
                root.after(100, popup)
            else:
                finish_and_close(root, False)
        root.after(500, popup)
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=20)

    def success():
        tk.Label(root, text=f"🎉 {package_name} 卸载成功！", font=("Arial", 14, "bold"), fg="green").pack(pady=30)
        tk.Button(root, text="再见", font=("Arial", 14, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=20)
        tk.Button(root, text="重新安装", command=lambda: finish_and_close(root, False)).pack(pady=5)
        root.protocol("WM_DELETE_WINDOW", lambda: finish_and_close(root, True))

    def next_step(step_idx):
        step[0] = step_idx + 1
        show_step(step[0])

    root.protocol("WM_DELETE_WINDOW", lambda: finish_and_close(root, False))
    show_step(0)
    root.mainloop()
    return root.result

# ==================== 版本4：数学题+随机弹窗 ====================
def uninstall_program4(package_name):
    root = tk.Tk()
    root.title(f"{package_name} 卸载程序")
    root.geometry("500x450")
    root.resizable(False, False)
    root.result = False
    step = [0]

    def show_step(idx):
        for w in root.winfo_children():
            w.destroy()
        if idx == 0: step0()
        elif idx == 1: step1()
        elif idx == 2: step2()
        elif idx == 3: step3()
        elif idx == 4: step4()
        elif idx == 5: success()

    def step0():
        tk.Label(root, text=f"您确定要卸载 {package_name} 吗？", font=("Arial", 12)).pack(pady=20)
        tk.Button(root, text="取消卸载", font=("Arial", 14, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)
        tk.Button(root, text="继续卸载", font=("Arial", 8), bg="lightgray", fg="gray",
                  command=lambda: next_step(0)).pack(pady=5)
        tk.Button(root, text="确定不要卸载吗", command=lambda: finish_and_close(root, False)).pack(pady=5)
        tk.Button(root, text="重新安装", command=lambda: messagebox.showinfo("提示", "重新安装需要联网")).pack(pady=5)

    def step1():
        a = random.randint(10, 20)
        b = random.randint(1, 9)
        answer = a + b
        tk.Label(root, text=f"请计算 {a} + {b} = ?", font=("Arial", 12)).pack(pady=10)
        entry = ttk.Entry(root)
        entry.pack(pady=5)
        entry.focus()
        def check():
            try:
                if int(entry.get()) == answer:
                    next_step(1)
                else:
                    messagebox.showerror("错误", "答案错误")
                    entry.delete(0, tk.END)
            except:
                messagebox.showerror("错误", "请输入数字")
                entry.delete(0, tk.END)
        ttk.Button(root, text="确认", command=check).pack(pady=10)
        entry.bind('<Return>', lambda e: check())
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=5)

    def step2():
        tk.Label(root, text="正在删除注册表项...", font=("Arial", 12)).pack(pady=10)
        progress = ttk.Progressbar(root, mode='determinate', length=400)
        progress.pack(pady=20)
        status = tk.Label(root, text="0%")
        status.pack()
        def simulate():
            cur = 0
            while cur < 100:
                root.after(0, lambda: progress.config(value=cur))
                root.after(0, lambda: status.config(text=f"{cur}%"))
                time.sleep(0.08)
                cur += random.randint(1, 4)
                if cur >= 100:
                    cur = 100
                    root.after(0, lambda: progress.config(value=100))
                    root.after(0, lambda: status.config(text="100%"))
                    root.after(0, lambda: next_step(2))
                    break
                if random.random() < 0.06:
                    root.after(0, lambda: messagebox.showinfo("提示", "正在扫描病毒..."))
        threading.Thread(target=simulate, daemon=True).start()
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=10)

    def step3():
        tk.Label(root, text="请点击真正的卸载按钮", font=("Arial", 10)).pack(pady=10)
        true_idx = random.randint(0, 3)
        for i in range(4):
            if i == true_idx:
                btn = tk.Button(root, text="卸载", bg="lightgreen", fg="black",
                                command=lambda: next_step(3))
            else:
                texts = ["卸载!", "Uninstall", "移除", "删除"]
                text = random.choice(texts)
                btn = tk.Button(root, text=text, bg="white",
                                command=lambda: messagebox.showinfo("提示", "这是假的卸载按钮"))
            btn.pack(pady=5, fill=tk.X, padx=50)

    def step4():
        tk.Label(root, text="正在完成卸载...", font=("Arial", 12)).pack(pady=10)
        count = [0]
        order = ["要", "不要", "要"]
        random.shuffle(order)
        def popup():
            if count[0] >= 3:
                next_step(4)
                return
            current = order[count[0]]
            count[0] += 1
            if current == "不要":
                ans = messagebox.askquestion("警告", f"确定不要卸载 {package_name} 吗？")
                if ans == 'yes':
                    finish_and_close(root, False)
                else:
                    root.after(100, popup)
            else:
                ans = messagebox.askquestion("确认", f"确定要卸载 {package_name} 吗？({count[0]}/3)")
                if ans == 'yes':
                    root.after(100, popup)
                else:
                    finish_and_close(root, False)
        root.after(500, popup)
        tk.Button(root, text="取消卸载", font=("Arial", 12, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=20)

    def success():
        tk.Label(root, text=f"🎉 {package_name} 卸载成功！", font=("Arial", 14, "bold"), fg="green").pack(pady=30)
        tk.Button(root, text="再见", font=("Arial", 14, "bold"), bg="red", fg="white",
                  command=lambda: finish_and_close(root, False)).pack(pady=20)
        tk.Button(root, text="重新安装", command=lambda: finish_and_close(root, False)).pack(pady=5)
        root.protocol("WM_DELETE_WINDOW", lambda: finish_and_close(root, True))

    def next_step(step_idx):
        step[0] = step_idx + 1
        show_step(step[0])

    root.protocol("WM_DELETE_WINDOW", lambda: finish_and_close(root, False))
    show_step(0)
    root.mainloop()
    return root.result

# ==================== 随机选择并运行 ====================
def run(package):
    # 随机选择一个版本（1~4）
    funcs = [uninstall_program1, uninstall_program2, uninstall_program3, uninstall_program4]
    chosen = random.choice(funcs)
    # 传入包名（可自定义）
    pkg = package
    success = chosen(pkg)
    print("卸载成功" if success else "卸载失败或取消")
    return success