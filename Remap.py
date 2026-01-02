#!/usr/bin/env python3
"""
YOLO Remapper — Minimal GUI (Enter to Run)

Simple, no-frills GUI that remaps only the class index (first token) in YOLO .txt
labels by matching class NAMES between old_classes.txt and new_classes.txt.

Behavior:
 - Only replace the very first integer token (class index) on each valid line.
 - Coordinates and other tokens are preserved exactly.
 - If an old index's name is NOT present in new_classes.txt, the original line is
  kept unchanged (safe default). No fallback, no dropping, no extra options.

How to use:
 1. Save as `yolo_remap_minimal_gui.py` and run: python yolo_remap_minimal_gui.py
 2. Select Labels folder, Old classes file, New classes file, Output folder.
 3. Press Enter (or click "Run Remap") to start. Use "Preview" to inspect one file first.

This script binds the Enter key to the Run Remap action to satisfy the "Tick enter GUI" request.
"""

import os
import shutil
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# ---------- Utility ----------

def read_classes(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [ln.rstrip('\n') for ln in f.readlines() if ln.rstrip('\n') != '']

# ---------- Core remapping function ----------

def remap_by_name(labels_dir, out_dir, old_classes_path, new_classes_path, create_backup=True, log_fn=None):
    labels_dir = Path(labels_dir)
    out_dir = Path(out_dir)
    log = log_fn or (lambda s: None)

    if not labels_dir.exists() or not labels_dir.is_dir():
        raise FileNotFoundError('Labels folder not found')
    out_dir.mkdir(parents=True, exist_ok=True)

    if create_backup:
        backup_dir = labels_dir.parent / (labels_dir.name + '_backup')
        if not backup_dir.exists():
            shutil.copytree(labels_dir, backup_dir)
            log(f'Backup created at: {backup_dir}')
        else:
            log(f'Backup already exists at: {backup_dir}')

    old = read_classes(old_classes_path)
    new = read_classes(new_classes_path)
    name_to_new = {name: idx for idx, name in enumerate(new)}

    old_index_to_name = {i: n for i, n in enumerate(old)}

    stats = {'files':0, 'lines':0, 'changed':0, 'unchanged':0}

    for f in sorted(labels_dir.iterdir()):
        if not f.is_file() or f.suffix.lower() != '.txt':
            continue
        stats['files'] += 1
        content = f.read_text(encoding='utf-8')
        out_lines = []
        for raw in content.splitlines():
            ln = raw.rstrip('\n')
            if not ln.strip():
                continue
            stats['lines'] += 1
            parts = ln.split()
            if len(parts) < 5:
                out_lines.append(ln); stats['unchanged'] += 1; continue
            try:
                old_idx = int(parts[0])
            except Exception:
                out_lines.append(ln); stats['unchanged'] += 1; continue
            old_name = old_index_to_name.get(old_idx)
            if old_name is None:
                out_lines.append(ln); stats['unchanged'] += 1; continue
            new_idx = name_to_new.get(old_name)
            if new_idx is None:
                # keep unchanged when name missing in new list
                out_lines.append(ln); stats['unchanged'] += 1
            else:
                new_line = ' '.join([str(new_idx)] + parts[1:])
                out_lines.append(new_line)
                if new_line != ln:
                    stats['changed'] += 1
                else:
                    stats['unchanged'] += 1
        (out_dir / f.name).write_text('\n'.join(out_lines) + ('\n' if out_lines else ''), encoding='utf-8')

    # write new classes reference
    (out_dir / 'classes_mapped.txt').write_text('\n'.join(new) + '\n', encoding='utf-8')
    return stats

# ---------- Minimal GUI ----------

class MinimalApp:
    def __init__(self, root):
        self.root = root
        root.title('YOLO Remapper — Minimal')
        root.geometry('760x520')

        frm = tk.Frame(root)
        frm.pack(fill='x', padx=8, pady=6)

        tk.Label(frm, text='Labels folder:').grid(row=0, column=0, sticky='w')
        self.labels_e = tk.Entry(frm, width=68)
        self.labels_e.grid(row=0, column=1)
        tk.Button(frm, text='Browse', command=self.browse_labels).grid(row=0, column=2)

        tk.Label(frm, text='Old classes file:').grid(row=1, column=0, sticky='w')
        self.old_e = tk.Entry(frm, width=68)
        self.old_e.grid(row=1, column=1)
        tk.Button(frm, text='Browse', command=self.browse_old).grid(row=1, column=2)

        tk.Label(frm, text='New classes file:').grid(row=2, column=0, sticky='w')
        self.new_e = tk.Entry(frm, width=68)
        self.new_e.grid(row=2, column=1)
        tk.Button(frm, text='Browse', command=self.browse_new).grid(row=2, column=2)

        tk.Label(frm, text='Output folder:').grid(row=3, column=0, sticky='w')
        self.out_e = tk.Entry(frm, width=68)
        self.out_e.grid(row=3, column=1)
        tk.Button(frm, text='Browse', command=self.browse_out).grid(row=3, column=2)

        # buttons
        btnf = tk.Frame(root)
        btnf.pack(fill='x', padx=8, pady=6)
        self.run_btn = tk.Button(btnf, text='Run Remap (Enter)', width=18, command=self.start_remap)
        self.run_btn.pack(side='left', padx=6)
        tk.Button(btnf, text='Preview Selected', command=self.preview_selected).pack(side='left')

        # list + preview
        mid = tk.Frame(root)
        mid.pack(fill='both', expand=True, padx=8, pady=6)

        left = tk.Frame(mid)
        left.pack(side='left', fill='both', expand=True)
        tk.Label(left, text='Label files:').pack(anchor='w')
        self.lb = tk.Listbox(left, height=16)
        self.lb.pack(fill='both', expand=True)
        tk.Button(left, text='Refresh', command=self.refresh_list).pack(pady=6)

        right = tk.Frame(mid)
        right.pack(side='left', fill='both', expand=True, padx=(8,0))
        tk.Label(right, text='Original:').pack(anchor='w')
        self.orig_txt = scrolledtext.ScrolledText(right, height=12)
        self.orig_txt.pack(fill='both', expand=True)
        tk.Label(right, text='Remapped preview:').pack(anchor='w')
        self.remap_txt = scrolledtext.ScrolledText(right, height=12)
        self.remap_txt.pack(fill='both', expand=True)

        tk.Label(root, text='Log:').pack(anchor='w', padx=8)
        self.logbox = scrolledtext.ScrolledText(root, height=6)
        self.logbox.pack(fill='both', expand=False, padx=8, pady=(0,8))
        self.logbox.config(state='disabled')

        self.status = tk.StringVar(value='Ready')
        tk.Label(root, textvariable=self.status).pack(fill='x', padx=8, pady=(0,8))

        # bind Enter to run remap (global)
        root.bind('<Return>', lambda e: self.start_remap())

    def browse_labels(self):
        d = filedialog.askdirectory()
        if d:
            self.labels_e.delete(0,'end'); self.labels_e.insert(0,d); self.refresh_list()
    def browse_old(self):
        f = filedialog.askopenfilename(filetypes=[('Text','*.txt')])
        if f: self.old_e.delete(0,'end'); self.old_e.insert(0,f)
    def browse_new(self):
        f = filedialog.askopenfilename(filetypes=[('Text','*.txt')])
        if f: self.new_e.delete(0,'end'); self.new_e.insert(0,f)
    def browse_out(self):
        d = filedialog.askdirectory()
        if d: self.out_e.delete(0,'end'); self.out_e.insert(0,d)

    def log(self, msg):
        self.logbox.config(state='normal'); self.logbox.insert('end', str(msg)+'\n'); self.logbox.see('end'); self.logbox.config(state='disabled')

    def refresh_list(self):
        d = self.labels_e.get().strip()
        if not d: return
        p = Path(d)
        if not p.exists(): messagebox.showwarning('Missing','Labels folder does not exist'); return
        files = sorted([f.name for f in p.iterdir() if f.is_file() and f.suffix.lower()=='.txt'])
        self.lb.delete(0,'end')
        for fn in files: self.lb.insert('end', fn)

    def preview_selected(self):
        sel = self.lb.curselection()
        if not sel: return
        fname = self.lb.get(sel[0])
        p = Path(self.labels_e.get().strip()) / fname
        if not p.exists(): return
        content = p.read_text(encoding='utf-8')
        self.orig_txt.delete('1.0','end'); self.orig_txt.insert('end', content)
        try:
            old = read_classes(self.old_e.get().strip())
            new = read_classes(self.new_e.get().strip())
        except Exception as e:
            messagebox.showerror('Error', str(e)); return
        name_to_new = {n:i for i,n in enumerate(new)}
        old_index_to_name = {i:n for i,n in enumerate(old)}
        out_lines = []
        kept = dropped = changed = 0
        for raw in content.splitlines():
            ln = raw.rstrip('\n')
            if not ln.strip(): continue
            parts = ln.split()
            if len(parts) < 5:
                out_lines.append(ln); kept += 1; continue
            try:
                old_idx = int(parts[0])
            except Exception:
                out_lines.append(ln); kept += 1; continue
            old_name = old_index_to_name.get(old_idx)
            if old_name is None:
                out_lines.append(ln); kept += 1; continue
            new_idx = name_to_new.get(old_name)
            if new_idx is None:
                out_lines.append(ln); kept += 1
            else:
                new_line = ' '.join([str(new_idx)] + parts[1:])
                out_lines.append(new_line)
                if new_line != ln: changed += 1
                else: kept += 1
        self.remap_txt.delete('1.0','end'); self.remap_txt.insert('end', '\n'.join(out_lines) + ('\n' if out_lines else ''))
        self.log(f'Preview: kept={kept} changed={changed} dropped={dropped}')

    def start_remap(self):
        labels = self.labels_e.get().strip(); old = self.old_e.get().strip(); new = self.new_e.get().strip(); out = self.out_e.get().strip()
        if not labels or not old or not new or not out:
            messagebox.showwarning('Missing', 'Please set labels folder, old_classes.txt, new_classes.txt and output folder')
            return
        self.run_btn.config(state='disabled'); self.status.set('Running...'); self.logbox.config(state='normal'); self.logbox.delete('1.0','end'); self.logbox.config(state='disabled')
        t = threading.Thread(target=self._worker, args=(labels,out,old,new))
        t.daemon = True; t.start()

    def _worker(self, labels,out,old,new):
        try:
            def logger(s):
                self.log(s)
            stats = remap_by_name(labels, out, old, new, create_backup=True, log_fn=logger)
            self.log(f"Done. Files={stats['files']} Lines={stats['lines']} Changed={stats['changed']} Unchanged={stats['unchanged']}")
            self.status.set('Done')
        except Exception as e:
            self.log(f'Error: {e}'); messagebox.showerror('Error', str(e))
        finally:
            self.run_btn.config(state='normal')

if __name__ == '__main__':
    root = tk.Tk(); app = MinimalApp(root); root.mainloop()