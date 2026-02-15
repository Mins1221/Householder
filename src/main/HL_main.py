# -*- coding: utf-8 -*-

"""
스마트 가계부 v8.0
Windows 최적화 - Tkinter 버전
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime, timedelta
from collections import defaultdict


class ColorTheme:
    """색상 테마"""
    PRIMARY = "#2980b9"
    PRIMARY_LIGHT = "#3498db"
    PRIMARY_DARK = "#1f6191"
    
    BG_MAIN = "#f8f9fa"
    BG_CARD = "#ffffff"
    BG_HOVER = "#f0f2f5"
    
    TEXT_PRIMARY = "#212529"
    TEXT_SECONDARY = "#6c757d"
    TEXT_LIGHT = "#adb5bd"
    
    INCOME = "#28a745"
    EXPENSE = "#dc3545"
    
    BORDER = "#dee2e6"
    BTN_SUCCESS = "#28a745"
    BTN_DANGER = "#dc3545"
    BTN_SECONDARY = "#6c757d"


class DatabaseManager:
    """데이터베이스 관리"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.expanduser("~"), "household_account.db")
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                remark TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_transaction(self, date, trans_type, category, amount, remark):
        """거래 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO transactions (date, type, category, amount, remark) VALUES (?, ?, ?, ?, ?)',
            (date, trans_type, category, amount, remark)
        )
        conn.commit()
        conn.close()
    
    def get_all_transactions(self):
        """모든 거래 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC, id DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_transactions_by_month(self, year_month):
        """월별 거래 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM transactions WHERE date LIKE ? ORDER BY date DESC',
            (f'{year_month}%',)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_transaction(self, trans_id, date, trans_type, category, amount, remark):
        """거래 수정"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE transactions SET date=?, type=?, category=?, amount=?, remark=? WHERE id=?',
            (date, trans_type, category, amount, remark, trans_id)
        )
        conn.commit()
        conn.close()
    
    def delete_transaction(self, trans_id):
        """거래 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id=?', (trans_id,))
        conn.commit()
        conn.close()
    
    def get_monthly_summary(self, year_month):
        """월별 합계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT SUM(amount) FROM transactions WHERE date LIKE ? AND type="수입"',
            (f'{year_month}%',)
        )
        income = cursor.fetchone()[0] or 0
        
        cursor.execute(
            'SELECT SUM(amount) FROM transactions WHERE date LIKE ? AND type="지출"',
            (f'{year_month}%',)
        )
        expense = cursor.fetchone()[0] or 0
        
        conn.close()
        return income, expense
    
    def get_expense_by_category(self, year_month):
        """카테고리별 지출 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''SELECT category, SUM(amount) as total 
               FROM transactions 
               WHERE type="지출" AND date LIKE ? 
               GROUP BY category 
               ORDER BY total DESC''',
            (f'{year_month}%',)
        )
        
        rows = cursor.fetchall()
        conn.close()
        return rows


class SmartHouseholdApp:
    """스마트 가계부 메인 애플리케이션"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("💰 스마트 가계부")
        self.root.geometry("1200x700")
        self.root.configure(bg=ColorTheme.BG_MAIN)
        
        self.db = DatabaseManager()
        self.selected_id = None
        
        # 스타일 설정
        self.setup_styles()
        
        # UI 구성
        self.create_widgets()
        
        # 초기 데이터 로드
        self.load_current_month()
    
    def setup_styles(self):
        """스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 버튼 스타일
        style.configure('Primary.TButton', 
                       background=ColorTheme.PRIMARY,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        
        style.configure('Success.TButton',
                       background=ColorTheme.BTN_SUCCESS,
                       foreground='white',
                       borderwidth=0,
                       padding=10)
        
        style.configure('Danger.TButton',
                       background=ColorTheme.BTN_DANGER,
                       foreground='white',
                       borderwidth=0,
                       padding=10)
        
        # Treeview 스타일
        style.configure('Treeview',
                       background='white',
                       fieldbackground='white',
                       rowheight=30,
                       borderwidth=0)
        
        style.configure('Treeview.Heading',
                       background=ColorTheme.PRIMARY,
                       foreground='white',
                       borderwidth=0,
                       relief='flat')
    
    def create_widgets(self):
        """위젯 생성"""
        # 메인 컨테이너
        main_container = tk.Frame(self.root, bg=ColorTheme.BG_MAIN)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 헤더
        self.create_header(main_container)
        
        # 컨텐츠 영역
        content_frame = tk.Frame(main_container, bg=ColorTheme.BG_MAIN)
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # 왼쪽 패널 (입력 폼)
        left_panel = self.create_input_panel(content_frame)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # 오른쪽 패널 (거래 내역)
        right_panel = self.create_list_panel(content_frame)
        right_panel.pack(side='left', fill='both', expand=True, padx=(10, 0))
    
    def create_header(self, parent):
        """헤더 생성"""
        header = tk.Frame(parent, bg='white', relief='flat')
        header.pack(fill='x', pady=(0, 20))
        
        # 제목
        title_label = tk.Label(header, 
                              text="💰 스마트 가계부",
                              font=('맑은 고딕', 24, 'bold'),
                              bg='white',
                              fg=ColorTheme.TEXT_PRIMARY)
        title_label.pack(side='left', padx=20, pady=15)
        
        # 요약 정보
        summary_frame = tk.Frame(header, bg='white')
        summary_frame.pack(side='right', padx=20, pady=15)
        
        self.income_label = tk.Label(summary_frame,
                                     text="수입: ₩0",
                                     font=('맑은 고딕', 12, 'bold'),
                                     bg='white',
                                     fg=ColorTheme.INCOME)
        self.income_label.pack(side='left', padx=10)
        
        self.expense_label = tk.Label(summary_frame,
                                      text="지출: ₩0",
                                      font=('맑은 고딕', 12, 'bold'),
                                      bg='white',
                                      fg=ColorTheme.EXPENSE)
        self.expense_label.pack(side='left', padx=10)
        
        self.balance_label = tk.Label(summary_frame,
                                      text="잔액: ₩0",
                                      font=('맑은 고딕', 12, 'bold'),
                                      bg='white',
                                      fg=ColorTheme.PRIMARY)
        self.balance_label.pack(side='left', padx=10)
    
    def create_input_panel(self, parent):
        """입력 패널 생성"""
        panel = tk.Frame(parent, bg='white', relief='flat', width=350)
        panel.pack_propagate(False)
        
        # 패널 제목
        title = tk.Label(panel,
                        text="거래 입력",
                        font=('맑은 고딕', 16, 'bold'),
                        bg='white',
                        fg=ColorTheme.TEXT_PRIMARY)
        title.pack(pady=(20, 20), padx=20, anchor='w')
        
        # 입력 폼
        form_frame = tk.Frame(panel, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # 날짜
        self.create_form_field(form_frame, "날짜", 0)
        date_frame = tk.Frame(form_frame, bg='white')
        date_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        today = datetime.now()
        self.year_var = tk.StringVar(value=str(today.year))
        self.month_var = tk.StringVar(value=str(today.month))
        self.day_var = tk.StringVar(value=str(today.day))
        
        year_spin = ttk.Spinbox(date_frame, from_=2020, to=2030, 
                               textvariable=self.year_var, width=8)
        year_spin.pack(side='left', padx=(0, 5))
        
        tk.Label(date_frame, text="년", bg='white').pack(side='left', padx=(0, 10))
        
        month_spin = ttk.Spinbox(date_frame, from_=1, to=12,
                                textvariable=self.month_var, width=5)
        month_spin.pack(side='left', padx=(0, 5))
        
        tk.Label(date_frame, text="월", bg='white').pack(side='left', padx=(0, 10))
        
        day_spin = ttk.Spinbox(date_frame, from_=1, to=31,
                              textvariable=self.day_var, width=5)
        day_spin.pack(side='left', padx=(0, 5))
        
        tk.Label(date_frame, text="일", bg='white').pack(side='left')
        
        # 구분
        self.create_form_field(form_frame, "구분", 2)
        self.type_var = tk.StringVar(value="지출")
        type_frame = tk.Frame(form_frame, bg='white')
        type_frame.grid(row=3, column=0, sticky='ew', pady=(0, 15))
        
        tk.Radiobutton(type_frame, text="수입", variable=self.type_var, 
                      value="수입", bg='white', 
                      command=self.on_type_changed,
                      font=('맑은 고딕', 10)).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(type_frame, text="지출", variable=self.type_var,
                      value="지출", bg='white',
                      command=self.on_type_changed,
                      font=('맑은 고딕', 10)).pack(side='left')
        
        # 카테고리
        self.create_form_field(form_frame, "카테고리", 4)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, 
                                          textvariable=self.category_var,
                                          state='readonly',
                                          font=('맑은 고딕', 10))
        self.category_combo.grid(row=5, column=0, sticky='ew', pady=(0, 15))
        self.update_categories()
        
        # 금액
        self.create_form_field(form_frame, "금액", 6)
        self.amount_var = tk.StringVar()
        self.amount_var.trace('w', self.format_amount)
        amount_entry = ttk.Entry(form_frame, 
                                textvariable=self.amount_var,
                                font=('맑은 고딕', 10))
        amount_entry.grid(row=7, column=0, sticky='ew', pady=(0, 15))
        
        # 비고
        self.create_form_field(form_frame, "비고", 8)
        self.remark_var = tk.StringVar()
        remark_entry = ttk.Entry(form_frame,
                                textvariable=self.remark_var,
                                font=('맑은 고딕', 10))
        remark_entry.grid(row=9, column=0, sticky='ew', pady=(0, 20))
        
        form_frame.columnconfigure(0, weight=1)
        
        # 버튼 영역
        button_frame = tk.Frame(panel, bg='white')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        add_btn = tk.Button(button_frame, text="추가", 
                           command=self.on_add,
                           bg=ColorTheme.BTN_SUCCESS,
                           fg='white',
                           font=('맑은 고딕', 10, 'bold'),
                           relief='flat',
                           cursor='hand2',
                           padx=20, pady=8)
        add_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        update_btn = tk.Button(button_frame, text="수정",
                              command=self.on_update,
                              bg=ColorTheme.PRIMARY,
                              fg='white',
                              font=('맑은 고딕', 10, 'bold'),
                              relief='flat',
                              cursor='hand2',
                              padx=20, pady=8)
        update_btn.pack(side='left', expand=True, fill='x', padx=5)
        
        delete_btn = tk.Button(button_frame, text="삭제",
                              command=self.on_delete,
                              bg=ColorTheme.BTN_DANGER,
                              fg='white',
                              font=('맑은 고딕', 10, 'bold'),
                              relief='flat',
                              cursor='hand2',
                              padx=20, pady=8)
        delete_btn.pack(side='left', expand=True, fill='x', padx=(5, 0))
        
        clear_btn = tk.Button(panel, text="초기화",
                             command=self.on_clear,
                             bg=ColorTheme.BTN_SECONDARY,
                             fg='white',
                             font=('맑은 고딕', 10),
                             relief='flat',
                             cursor='hand2',
                             padx=20, pady=8)
        clear_btn.pack(fill='x', padx=20, pady=(0, 20))
        
        return panel
    
    def create_form_field(self, parent, label_text, row):
        """폼 필드 레이블 생성"""
        label = tk.Label(parent,
                        text=label_text,
                        font=('맑은 고딕', 10, 'bold'),
                        bg='white',
                        fg=ColorTheme.TEXT_SECONDARY)
        label.grid(row=row, column=0, sticky='w', pady=(0, 5))
    
    def create_list_panel(self, parent):
        """리스트 패널 생성"""
        panel = tk.Frame(parent, bg='white', relief='flat')
        
        # 상단 컨트롤
        control_frame = tk.Frame(panel, bg='white')
        control_frame.pack(fill='x', padx=20, pady=20)
        
        # 월 선택
        tk.Label(control_frame, text="조회 월:",
                font=('맑은 고딕', 10, 'bold'),
                bg='white').pack(side='left', padx=(0, 10))
        
        self.month_var_filter = tk.StringVar()
        self.month_combo = ttk.Combobox(control_frame,
                                       textvariable=self.month_var_filter,
                                       state='readonly',
                                       width=15,
                                       font=('맑은 고딕', 10))
        self.month_combo.pack(side='left', padx=(0, 10))
        self.month_combo.bind('<<ComboboxSelected>>', self.on_month_changed)
        
        # 전체보기 버튼
        view_all_btn = tk.Button(control_frame, text="전체보기",
                                command=self.on_view_all,
                                bg=ColorTheme.PRIMARY,
                                fg='white',
                                font=('맑은 고딕', 9),
                                relief='flat',
                                cursor='hand2',
                                padx=15, pady=5)
        view_all_btn.pack(side='left')
        
        # 카테고리 통계 버튼
        stats_btn = tk.Button(control_frame, text="📊 통계",
                             command=self.show_statistics,
                             bg=ColorTheme.PRIMARY_LIGHT,
                             fg='white',
                             font=('맑은 고딕', 9),
                             relief='flat',
                             cursor='hand2',
                             padx=15, pady=5)
        stats_btn.pack(side='right')
        
        # 리스트 프레임
        list_frame = tk.Frame(panel, bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Treeview (표)
        columns = ('ID', '날짜', '구분', '카테고리', '금액', '비고')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        # 컬럼 설정
        self.tree.heading('ID', text='ID')
        self.tree.heading('날짜', text='날짜')
        self.tree.heading('구분', text='구분')
        self.tree.heading('카테고리', text='카테고리')
        self.tree.heading('금액', text='금액')
        self.tree.heading('비고', text='비고')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('날짜', width=100, anchor='center')
        self.tree.column('구분', width=80, anchor='center')
        self.tree.column('카테고리', width=100, anchor='center')
        self.tree.column('금액', width=120, anchor='e')
        self.tree.column('비고', width=200, anchor='w')
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 항목 선택 이벤트
        self.tree.bind('<<TreeviewSelect>>', self.on_item_selected)
        
        # 월 목록 초기화
        self.populate_months()
        
        return panel
    
    def populate_months(self):
        """월 목록 채우기"""
        months = []
        current = datetime.now()
        
        for i in range(12):
            year = current.year if current.month - i > 0 else current.year - 1
            month = current.month - i if current.month - i > 0 else 12 + (current.month - i)
            months.append(f"{year}-{month:02d}")
        
        self.month_combo['values'] = months
        self.month_combo.current(0)
    
    def update_categories(self):
        """카테고리 업데이트"""
        trans_type = self.type_var.get()
        
        if trans_type == "수입":
            categories = ["급여", "보너스", "용돈", "기타수입"]
        else:
            categories = ["식비", "교통비", "통신비", "쇼핑", "의료", "문화", "주거", "기타"]
        
        self.category_combo['values'] = categories
        if categories:
            self.category_combo.current(0)
    
    def format_amount(self, *args):
        """금액 자동 포맷팅"""
        value = self.amount_var.get().replace(',', '')
        if value and value.isdigit():
            formatted = f"{int(value):,}"
            # 무한 루프 방지
            if formatted != self.amount_var.get():
                self.amount_var.set(formatted)
    
    def on_type_changed(self):
        """구분 변경 이벤트"""
        self.update_categories()
    
    def on_add(self):
        """거래 추가"""
        try:
            date_str = f"{self.year_var.get()}-{int(self.month_var.get()):02d}-{int(self.day_var.get()):02d}"
            trans_type = self.type_var.get()
            category = self.category_var.get()
            amount_str = self.amount_var.get().replace(',', '')
            remark = self.remark_var.get()
            
            if not category:
                messagebox.showwarning("입력 오류", "카테고리를 선택하세요.")
                return
            
            if not amount_str or not amount_str.isdigit():
                messagebox.showwarning("입력 오류", "올바른 금액을 입력하세요.")
                return
            
            amount = float(amount_str)
            
            self.db.insert_transaction(date_str, trans_type, category, amount, remark)
            messagebox.showinfo("완료", "거래가 추가되었습니다.")
            
            self.on_clear()
            self.refresh_list()
            self.update_summary()
            
        except Exception as e:
            messagebox.showerror("오류", f"거래 추가 중 오류가 발생했습니다:\n{str(e)}")
    
    def on_update(self):
        """거래 수정"""
        if not self.selected_id:
            messagebox.showwarning("알림", "수정할 항목을 선택하세요.")
            return
        
        try:
            date_str = f"{self.year_var.get()}-{int(self.month_var.get()):02d}-{int(self.day_var.get()):02d}"
            trans_type = self.type_var.get()
            category = self.category_var.get()
            amount_str = self.amount_var.get().replace(',', '')
            remark = self.remark_var.get()
            
            if not category or not amount_str or not amount_str.isdigit():
                messagebox.showwarning("입력 오류", "올바른 정보를 입력하세요.")
                return
            
            amount = float(amount_str)
            
            self.db.update_transaction(self.selected_id, date_str, trans_type, category, amount, remark)
            messagebox.showinfo("완료", "거래가 수정되었습니다.")
            
            self.on_clear()
            self.refresh_list()
            self.update_summary()
            
        except Exception as e:
            messagebox.showerror("오류", f"거래 수정 중 오류가 발생했습니다:\n{str(e)}")
    
    def on_delete(self):
        """거래 삭제"""
        if not self.selected_id:
            messagebox.showwarning("알림", "삭제할 항목을 선택하세요.")
            return
        
        if messagebox.askyesno("삭제 확인", "선택한 거래를 삭제하시겠습니까?"):
            self.db.delete_transaction(self.selected_id)
            messagebox.showinfo("완료", "거래가 삭제되었습니다.")
            
            self.on_clear()
            self.refresh_list()
            self.update_summary()
    
    def on_clear(self):
        """입력 초기화"""
        today = datetime.now()
        self.year_var.set(str(today.year))
        self.month_var.set(str(today.month))
        self.day_var.set(str(today.day))
        self.type_var.set("지출")
        self.update_categories()
        self.amount_var.set("")
        self.remark_var.set("")
        self.selected_id = None
    
    def on_item_selected(self, event):
        """리스트 항목 선택"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.selected_id = values[0]
        
        # 날짜 파싱
        date_str = values[1]
        year, month, day = date_str.split('-')
        self.year_var.set(year)
        self.month_var.set(str(int(month)))
        self.day_var.set(str(int(day)))
        
        # 구분
        self.type_var.set(values[2])
        self.update_categories()
        
        # 카테고리
        self.category_var.set(values[3])
        
        # 금액
        amount = values[4].replace('₩', '').replace(',', '').strip()
        self.amount_var.set(amount)
        
        # 비고
        self.remark_var.set(values[5])
    
    def on_month_changed(self, event):
        """월 변경 이벤트"""
        self.refresh_list()
        self.update_summary()
    
    def on_view_all(self):
        """전체 보기"""
        self.load_all_transactions()
        self.update_summary()
    
    def load_current_month(self):
        """현재 월 데이터 로드"""
        self.refresh_list()
        self.update_summary()
    
    def load_all_transactions(self):
        """전체 거래 로드"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rows = self.db.get_all_transactions()
        
        for row in rows:
            trans_id, date_str, trans_type, category, amount, remark = row
            
            # 색상 태그
            tag = 'income' if trans_type == "수입" else 'expense'
            
            self.tree.insert('', 'end', 
                           values=(trans_id, date_str, trans_type, category, 
                                  f"₩{amount:,.0f}", remark or ""),
                           tags=(tag,))
        
        # 태그 색상 설정
        self.tree.tag_configure('income', foreground=ColorTheme.INCOME)
        self.tree.tag_configure('expense', foreground=ColorTheme.EXPENSE)
    
    def refresh_list(self):
        """리스트 새로고침"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        selected_month = self.month_var_filter.get()
        if not selected_month:
            return
        
        rows = self.db.get_transactions_by_month(selected_month)
        
        for row in rows:
            trans_id, date_str, trans_type, category, amount, remark = row
            
            tag = 'income' if trans_type == "수입" else 'expense'
            
            self.tree.insert('', 'end',
                           values=(trans_id, date_str, trans_type, category,
                                  f"₩{amount:,.0f}", remark or ""),
                           tags=(tag,))
        
        self.tree.tag_configure('income', foreground=ColorTheme.INCOME)
        self.tree.tag_configure('expense', foreground=ColorTheme.EXPENSE)
    
    def update_summary(self):
        """요약 정보 업데이트"""
        selected_month = self.month_var_filter.get()
        if not selected_month:
            current = datetime.now()
            selected_month = f"{current.year}-{current.month:02d}"
        
        income, expense = self.db.get_monthly_summary(selected_month)
        balance = income - expense
        
        self.income_label.config(text=f"수입: ₩{income:,.0f}")
        self.expense_label.config(text=f"지출: ₩{expense:,.0f}")
        self.balance_label.config(text=f"잔액: ₩{balance:,.0f}")
        
        # 잔액 색상 변경
        if balance >= 0:
            self.balance_label.config(fg=ColorTheme.INCOME)
        else:
            self.balance_label.config(fg=ColorTheme.EXPENSE)
    
    def show_statistics(self):
        """통계 창 표시"""
        selected_month = self.month_var_filter.get()
        if not selected_month:
            current = datetime.now()
            selected_month = f"{current.year}-{current.month:02d}"
        
        stats = self.db.get_expense_by_category(selected_month)
        
        if not stats:
            messagebox.showinfo("통계", f"{selected_month}에 지출 내역이 없습니다.")
            return
        
        # 통계 창 생성
        stats_window = tk.Toplevel(self.root)
        stats_window.title(f"📊 지출 통계 - {selected_month}")
        stats_window.geometry("500x400")
        stats_window.configure(bg='white')
        
        # 제목
        title = tk.Label(stats_window,
                        text=f"{selected_month} 카테고리별 지출",
                        font=('맑은 고딕', 14, 'bold'),
                        bg='white',
                        fg=ColorTheme.TEXT_PRIMARY)
        title.pack(pady=20)
        
        # 통계 리스트
        frame = tk.Frame(stats_window, bg='white')
        frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        total_expense = sum(amount for _, amount in stats)
        
        for category, amount in stats:
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            
            item_frame = tk.Frame(frame, bg='white')
            item_frame.pack(fill='x', pady=5)
            
            # 카테고리명
            cat_label = tk.Label(item_frame,
                                text=category,
                                font=('맑은 고딕', 11, 'bold'),
                                bg='white',
                                fg=ColorTheme.TEXT_PRIMARY)
            cat_label.pack(side='left')
            
            # 금액
            amount_label = tk.Label(item_frame,
                                   text=f"₩{amount:,.0f} ({percentage:.1f}%)",
                                   font=('맑은 고딕', 11),
                                   bg='white',
                                   fg=ColorTheme.EXPENSE)
            amount_label.pack(side='right')
            
            # 프로그레스 바
            progress_frame = tk.Frame(frame, bg=ColorTheme.BG_HOVER, height=10)
            progress_frame.pack(fill='x', pady=(0, 10))
            
            progress_bar = tk.Frame(progress_frame, 
                                   bg=ColorTheme.EXPENSE,
                                   height=10)
            progress_bar.place(x=0, y=0, relwidth=percentage/100, height=10)
        
        # 총합
        total_frame = tk.Frame(stats_window, bg=ColorTheme.BG_HOVER)
        total_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        total_label = tk.Label(total_frame,
                              text=f"총 지출: ₩{total_expense:,.0f}",
                              font=('맑은 고딕', 12, 'bold'),
                              bg=ColorTheme.BG_HOVER,
                              fg=ColorTheme.TEXT_PRIMARY)
        total_label.pack(pady=15)


def main():
    """메인 실행"""
    root = tk.Tk()
    app = SmartHouseholdApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
