import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import shutil
import json
import re
import time
import sys

# =============================================================================
# 包管理器定义（与原来一致）
# =============================================================================
PACKAGE_MANAGERS = {
    'apt': {
        'cmd': 'dpkg-query',
        'list_cmd': ['dpkg-query', '-W', '-f=${Package} ${Version}\n'],
        'parse': lambda output: [line.split(maxsplit=1) for line in output.splitlines() if line.strip()],
        'uninstall_cmd': lambda pkg: ['sudo', 'apt', 'remove', '-y', pkg],
    },
    'yum': {
        'cmd': 'rpm',
        'list_cmd': ['rpm', '-qa', '--queryformat', '%{NAME} %{VERSION}\n'],
        'parse': lambda output: [line.split(maxsplit=1) for line in output.splitlines() if line.strip()],
        'uninstall_cmd': lambda pkg: ['sudo', 'yum', 'remove', '-y', pkg],
    },
    'dnf': {
        'cmd': 'rpm',
        'list_cmd': ['rpm', '-qa', '--queryformat', '%{NAME} %{VERSION}\n'],
        'parse': lambda output: [line.split(maxsplit=1) for line in output.splitlines() if line.strip()],
        'uninstall_cmd': lambda pkg: ['sudo', 'dnf', 'remove', '-y', pkg],
    },
    'pacman': {
        'cmd': 'pacman',
        'list_cmd': ['pacman', '-Q'],
        'parse': lambda output: [line.split(maxsplit=1) for line in output.splitlines() if line.strip()],
        'uninstall_cmd': lambda pkg: ['sudo', 'pacman', '-R', '--noconfirm', pkg],
    },
    'yay': {
        'cmd': 'yay',
        'list_cmd': ['yay', '-Q'],
        'parse': lambda output: [line.split(maxsplit=1) for line in output.splitlines() if line.strip()],
        'uninstall_cmd': lambda pkg: ['yay', '-R', '--noconfirm', pkg],
    },
    'paru': {
        'cmd': 'paru',
        'list_cmd': ['paru', '-Q'],
        'parse': lambda output: [line.split(maxsplit=1) for line in output.splitlines() if line.strip()],
        'uninstall_cmd': lambda pkg: ['paru', '-R', '--noconfirm', pkg],
    },
    'trizen': {
        'cmd': 'trizen',
        'list_cmd': ['trizen', '-Q'],
        'parse': lambda output: [line.split(maxsplit=1) for line in output.splitlines() if line.strip()],
        'uninstall_cmd': lambda pkg: ['trizen', '-R', '--no-confirm', pkg],
    },
    'brew': {
        'cmd': 'brew',
        'list_cmd': ['brew', 'list', '--versions'],
        'parse': lambda output: [line.split(maxsplit=1) for line in output.splitlines() if line.strip()],
        'uninstall_cmd': lambda pkg: ['brew', 'uninstall', pkg],
    },
    'pip': {
        'cmd': 'pip',
        'list_cmd': ['pip', 'list', '--format=freeze'],
        'parse': lambda output: [line.split('==', maxsplit=1) for line in output.splitlines() if '==' in line],
        'uninstall_cmd': lambda pkg: ['pip', 'uninstall', '-y', pkg],
    },
    'pip3': {
        'cmd': 'pip3',
        'list_cmd': ['pip3', 'list', '--format=freeze'],
        'parse': lambda output: [line.split('==', maxsplit=1) for line in output.splitlines() if '==' in line],
        'uninstall_cmd': lambda pkg: ['pip3', 'uninstall', '-y', pkg],
    },
    'npm': {
        'cmd': 'npm',
        'list_cmd': ['npm', 'list', '-g', '--depth=0', '--json'],
        'parse': lambda output: parse_npm(output),
        'uninstall_cmd': lambda pkg: ['npm', 'uninstall', '-g', pkg],
    },
    'gem': {
        'cmd': 'gem',
        'list_cmd': ['gem', 'list'],
        'parse': lambda output: parse_gem(output),
        'uninstall_cmd': lambda pkg: ['gem', 'uninstall', pkg],
    },
    'cargo': {
        'cmd': 'cargo',
        'list_cmd': ['cargo', 'install', '--list'],
        'parse': lambda output: parse_cargo(output),
        'uninstall_cmd': lambda pkg: ['cargo', 'uninstall', pkg],
    },
}

def parse_npm(output):
    try:
        data = json.loads(output)
        packages = data.get('dependencies', {})
        return [[name, info.get('version', 'unknown')] for name, info in packages.items()]
    except json.JSONDecodeError:
        return []

def parse_gem(output):
    result = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r'^(\S+)\s+\((.+)\)$', line)
        if match:
            name = match.group(1)
            versions = match.group(2).split(',')
            result.append([name, versions[0].strip()])
    return result

def parse_cargo(output):
    result = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            ver = parts[1] if parts[1].startswith('v') else parts[1]
            result.append([name, ver])
    return result

def detect_available_managers():
    available = {}
    for name, info in PACKAGE_MANAGERS.items():
        if shutil.which(info['cmd']):
            available[name] = info
    return available

class PackageViewerApp:
    def __init__(self, root):
        self.root = root
        root.title("全部软件包管理器查看器")
        root.geometry("1000x700")

        style = ttk.Style()
        style.configure('Treeview', rowheight=28)

        self.managers = detect_available_managers()
        if not self.managers:
            messagebox.showerror("错误", "未检测到任何可用的包管理器。")
            root.destroy()
            return

        self.all_data = {}
        self.manager_nodes = {}
        self.is_uninstalling = False

        self.create_widgets()
        self.load_all_packages()

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(fill=tk.X)

        refresh_btn = ttk.Button(top_frame, text="刷新全部", command=self.refresh_all)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        self.uninstall_btn = ttk.Button(top_frame, text="卸载", command=self.on_uninstall_click, state=tk.DISABLED)
        self.uninstall_btn.pack(side=tk.LEFT, padx=5)

        ttk.Label(top_frame, text="搜索 (包名):").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.apply_filter())

        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)

        tree_frame = ttk.Frame(self.root, padding="5")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=('version',), show='tree headings')
        self.tree.heading('#0', text='软件包 (按管理器分组)')
        self.tree.heading('version', text='版本号')
        self.tree.column('#0', width=500, minwidth=200, stretch=True)
        self.tree.column('version', width=200, minwidth=100, stretch=True)

        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.toggle_node)
        self.tree.bind('<Button-3>', self.on_right_click)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="卸载", command=self.on_uninstall_click)
        self.context_menu.bind('<FocusOut>', lambda e: self.context_menu.unpost())

    def toggle_node(self, event):
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item and self.tree.parent(item) == '':
            if self.tree.item(item, 'open'):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            parent = self.tree.parent(item)
            if parent:
                self.uninstall_btn.config(state=tk.NORMAL)
                return
        self.uninstall_btn.config(state=tk.DISABLED)

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            if self.tree.parent(item):
                self.context_menu.unpost()
                self.context_menu.post(event.x_root, event.y_root)
                self.context_menu.focus_set()

    # ---------- 执行真实卸载命令 ----------
    def _execute_uninstall(self, manager, package):
        uninstall_cmd_func = self.managers[manager].get('uninstall_cmd')
        if not uninstall_cmd_func:
            return False, f"管理器 '{manager}' 未配置卸载命令"
        cmd = uninstall_cmd_func(package)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return True, "卸载成功"
            else:
                return False, f"命令执行失败 (返回码 {result.returncode}): {result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "卸载超时"
        except Exception as e:
            return False, f"发生异常: {str(e)}"

    # ---------- 卸载入口：使用子进程调用 gui.run，并增强结果解析 ----------
    def on_uninstall_click(self):
        if self.is_uninstalling:
            messagebox.showwarning("卸载进行中", "当前有卸载任务正在运行，请等待完成后再试。")
            return

        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        parent = self.tree.parent(item)
        if not parent:
            return

        manager = self.tree.item(parent, 'text')
        manager = manager.split(' (')[0].strip()
        package = self.tree.item(item, 'text')

        self.is_uninstalling = True
        self.uninstall_btn.config(state=tk.DISABLED)
        self.status_var.set(f"正在启动防卸载验证...")

        def do_verify():
            try:
                # 使用子进程运行 gui.run，并捕获输出
                cmd = [sys.executable, '-c', f'import gui; result = gui.run("{package}"); print(result)']
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                output = proc.stdout.strip()
                # 更健壮的解析：查找独立的 True/False 字符串
                match = re.search(r'\b(True|False)\b', output, re.IGNORECASE)
                if match:
                    passed = match.group(1).lower() == 'true'
                    error_msg = None
                else:
                    # 如果没有找到，则视为失败，并记录输出
                    passed = False
                    error_msg = f"防卸载验证返回异常，无法解析结果。输出内容: '{output}'"
            except subprocess.TimeoutExpired:
                passed = False
                error_msg = "防卸载验证超时"
            except Exception as e:
                passed = False
                error_msg = f"防卸载模块异常: {str(e)}"
            # 回到主线程处理结果
            self.root.after(0, lambda: self._handle_verify_result(passed, manager, package, error_msg))

        threading.Thread(target=do_verify, daemon=True).start()

    def _handle_verify_result(self, passed, manager, package, error_msg):
        """在主线程中处理防卸载验证结果"""
        if error_msg:
            self.status_var.set(f"防卸载验证出错: {error_msg}")
            messagebox.showerror("错误", error_msg)
            self._uninstall_done()
            return

        if passed:
            self.status_var.set(f"正在卸载 {manager} - {package} ...")
            success, msg = self._execute_uninstall(manager, package)
            if success:
                self.status_var.set(f"卸载完成: {manager} - {package}")
                messagebox.showinfo("卸载成功", f"{package} 已成功卸载")
            else:
                self.status_var.set(f"卸载失败: {msg}")
                messagebox.showerror("卸载失败", msg)
        else:
            self.status_var.set(f"用户取消卸载 {package}")
            messagebox.showinfo("已取消", f"已取消卸载 {package}")

        self._uninstall_done()

    def _uninstall_done(self):
        self.is_uninstalling = False
        self.uninstall_btn.config(state=tk.NORMAL)  # 将在 on_tree_select 中根据选中项自动调整
        self.refresh_all()  # 刷新列表

    # ---------- 加载包列表（保持不变） ----------
    def load_all_packages(self):
        self.status_var.set("正在加载所有包管理器...")
        self.tree.delete(*self.tree.get_children())
        self.all_data.clear()
        self.manager_nodes.clear()
        self.uninstall_btn.config(state=tk.DISABLED)

        for mgr in self.managers:
            threading.Thread(target=self._fetch_manager_packages, args=(mgr,), daemon=True).start()

    def _fetch_manager_packages(self, manager_name):
        info = self.managers[manager_name]
        cmd = info['list_cmd']
        parse_func = info['parse']
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            packages = parse_func(result.stdout)
            self.all_data[manager_name] = packages
            self.root.after(0, lambda: self._add_manager_node(manager_name, packages))
        except Exception as e:
            self.root.after(0, lambda: self._show_manager_error(manager_name, str(e)))

    def _add_manager_node(self, manager_name, packages):
        if manager_name in self.manager_nodes:
            return
        parent_id = self.tree.insert('', tk.END, text=f"{manager_name}  ({len(packages)} 个包)", open=True)
        self.manager_nodes[manager_name] = parent_id
        for pkg, ver in packages:
            self.tree.insert(parent_id, tk.END, text=pkg, values=(ver,))
        self._update_status()

    def _show_manager_error(self, manager_name, error_msg):
        parent_id = self.tree.insert('', tk.END, text=f"{manager_name}  (加载失败)", open=False)
        self.manager_nodes[manager_name] = parent_id
        self.tree.insert(parent_id, tk.END, text=f"错误: {error_msg}", values=('',))
        self._update_status()

    def _update_status(self):
        loaded = len(self.manager_nodes)
        total = len(self.managers)
        total_pkgs = sum(len(pkgs) for pkgs in self.all_data.values())
        self.status_var.set(f"已加载 {loaded}/{total} 个管理器, 共 {total_pkgs} 个软件包")

    def refresh_all(self):
        self.search_var.set('')
        self.load_all_packages()

    def apply_filter(self):
        keyword = self.search_var.get().strip().lower()
        for mgr, parent_id in self.manager_nodes.items():
            children = self.tree.get_children(parent_id)
            for child in children:
                self.tree.delete(child)
            if keyword:
                pkgs = self.all_data.get(mgr, [])
                filtered = [(p, v) for p, v in pkgs if keyword in p.lower()]
                for pkg, ver in filtered:
                    self.tree.insert(parent_id, tk.END, text=pkg, values=(ver,))
                self.tree.item(parent_id, text=f"{mgr}  ({len(filtered)} 个匹配)")
            else:
                pkgs = self.all_data.get(mgr, [])
                for pkg, ver in pkgs:
                    self.tree.insert(parent_id, tk.END, text=pkg, values=(ver,))
                self.tree.item(parent_id, text=f"{mgr}  ({len(pkgs)} 个包)")

def main():
    root = tk.Tk()
    app = PackageViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()