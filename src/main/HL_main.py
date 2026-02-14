# -*- coding: utf-8 -*- 

###########################################################################
## Modern Smart Household Account Book
## 모던 스마트 가계부 v7.0 - Windows 최적화 버전
###########################################################################

import wx
import wx.xrc
import wx.adv
import sqlite3
import os
from datetime import datetime
from collections import defaultdict

###########################################################################
## SQLite 데이터베이스 관리
###########################################################################
class DatabaseManager:
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                amount REAL NOT NULL
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
    
    def get_expense_by_category(self, year_month=None):
        """카테고리별 지출 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if year_month:
            cursor.execute(
                '''SELECT category, SUM(amount) as total 
                   FROM transactions 
                   WHERE type="지출" AND date LIKE ? 
                   GROUP BY category 
                   ORDER BY total DESC''',
                (f'{year_month}%',)
            )
        else:
            cursor.execute(
                '''SELECT category, SUM(amount) as total 
                   FROM transactions 
                   WHERE type="지출" 
                   GROUP BY category 
                   ORDER BY total DESC'''
            )
        
        rows = cursor.fetchall()
        conn.close()
        return rows


###########################################################################
## 색상 테마 설정 - Windows 친화적
###########################################################################
class ColorTheme:
    # 메인 컬러 - 부드러운 블루 계열
    PRIMARY = wx.Colour(41, 128, 185)
    PRIMARY_LIGHT = wx.Colour(52, 152, 219)
    PRIMARY_DARK = wx.Colour(31, 97, 141)
    
    # 배경
    BG_MAIN = wx.Colour(248, 249, 250)
    BG_CARD = wx.WHITE
    BG_HOVER = wx.Colour(240, 242, 245)
    
    # 텍스트
    TEXT_PRIMARY = wx.Colour(33, 37, 41)
    TEXT_SECONDARY = wx.Colour(108, 117, 125)
    TEXT_LIGHT = wx.Colour(173, 181, 189)
    
    # 수입/지출
    INCOME = wx.Colour(40, 167, 69)
    EXPENSE = wx.Colour(220, 53, 69)
    
    # 보더
    BORDER = wx.Colour(222, 226, 230)
    
    # 버튼
    BTN_SUCCESS = wx.Colour(40, 167, 69)
    BTN_DANGER = wx.Colour(220, 53, 69)
    BTN_SECONDARY = wx.Colour(108, 117, 125)


###########################################################################
## 메인 프레임
###########################################################################
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            parent=None,
            title="스마트 가계부",
            size=(1200, 800)
        )
        
        self.db = DatabaseManager()
        self.selected_id = None
        
        # 아이콘 설정 (Windows 기본 아이콘 사용)
        try:
            self.SetIcon(wx.Icon(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_FRAME_ICON)))
        except:
            pass
        
        self.SetBackgroundColour(ColorTheme.BG_MAIN)
        self.init_ui()
        self.Centre()
        
        # 초기 데이터 로드
        self.load_current_month()
    
    def init_ui(self):
        """UI 초기화"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = self.create_header()
        main_sizer.Add(header, 0, wx.EXPAND | wx.ALL, 10)
        
        # 콘텐츠 영역
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 왼쪽: 입력 패널
        left_panel = self.create_input_panel()
        content_sizer.Add(left_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        # 오른쪽: 리스트 패널
        right_panel = self.create_list_panel()
        content_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 10)
        
        main_sizer.Add(content_sizer, 1, wx.EXPAND)
        
        self.SetSizer(main_sizer)
    
    def create_header(self):
        """헤더 패널 생성"""
        panel = wx.Panel(self)
        panel.SetBackgroundColour(ColorTheme.BG_CARD)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 제목
        title = wx.StaticText(panel, label="💰 스마트 가계부")
        font = title.GetFont()
        font.SetPointSize(18)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        title.SetForegroundColour(ColorTheme.PRIMARY)
        sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        
        sizer.AddStretchSpacer()
        
        # 현재 날짜
        today = datetime.now().strftime("%Y년 %m월 %d일")
        date_label = wx.StaticText(panel, label=today)
        date_font = date_label.GetFont()
        date_font.SetPointSize(10)
        date_label.SetFont(date_font)
        date_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        sizer.Add(date_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        
        panel.SetSizer(sizer)
        return panel
    
    def create_input_panel(self):
        """입력 패널 생성"""
        panel = wx.Panel(self)
        panel.SetBackgroundColour(ColorTheme.BG_CARD)
        panel.SetMinSize((380, -1))
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 타이틀
        title = wx.StaticText(panel, label="거래 입력")
        font = title.GetFont()
        font.SetPointSize(12)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        title.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        sizer.Add(title, 0, wx.ALL, 15)
        
        # 구분선
        line = wx.Panel(panel, size=(-1, 1))
        line.SetBackgroundColour(ColorTheme.BORDER)
        sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        
        # 입력 폼
        form_panel = wx.Panel(panel)
        form_panel.SetBackgroundColour(ColorTheme.BG_CARD)
        form_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 날짜
        date_sizer = wx.BoxSizer(wx.HORIZONTAL)
        date_label = wx.StaticText(form_panel, label="날짜", size=(80, -1))
        date_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        self.date_picker = wx.adv.DatePickerCtrl(
            form_panel,
            style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY,
            size=(250, 32)
        )
        date_sizer.Add(date_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        date_sizer.Add(self.date_picker, 1, wx.EXPAND)
        form_sizer.Add(date_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 구분 (수입/지출)
        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_label = wx.StaticText(form_panel, label="구분", size=(80, -1))
        type_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        self.type_choice = wx.Choice(form_panel, choices=["수입", "지출"], size=(250, 32))
        self.type_choice.SetSelection(1)  # 기본값: 지출
        self.type_choice.Bind(wx.EVT_CHOICE, self.on_type_changed)
        type_sizer.Add(type_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        type_sizer.Add(self.type_choice, 1, wx.EXPAND)
        form_sizer.Add(type_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 카테고리
        cat_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cat_label = wx.StaticText(form_panel, label="카테고리", size=(80, -1))
        cat_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        self.category_choice = wx.ComboBox(form_panel, size=(250, 32))
        cat_sizer.Add(cat_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        cat_sizer.Add(self.category_choice, 1, wx.EXPAND)
        form_sizer.Add(cat_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 금액
        amount_sizer = wx.BoxSizer(wx.HORIZONTAL)
        amount_label = wx.StaticText(form_panel, label="금액", size=(80, -1))
        amount_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        self.amount_text = wx.TextCtrl(form_panel, size=(250, 32))
        self.amount_text.Bind(wx.EVT_TEXT, self.on_amount_changed)
        amount_sizer.Add(amount_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        amount_sizer.Add(self.amount_text, 1, wx.EXPAND)
        form_sizer.Add(amount_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 비고
        remark_sizer = wx.BoxSizer(wx.HORIZONTAL)
        remark_label = wx.StaticText(form_panel, label="비고", size=(80, -1))
        remark_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        self.remark_text = wx.TextCtrl(form_panel, size=(250, 32))
        remark_sizer.Add(remark_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        remark_sizer.Add(self.remark_text, 1, wx.EXPAND)
        form_sizer.Add(remark_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        form_panel.SetSizer(form_sizer)
        sizer.Add(form_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        # 버튼 영역
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 추가 버튼
        self.btn_add = wx.Button(panel, label="추가", size=(110, 40))
        self.btn_add.SetBackgroundColour(ColorTheme.PRIMARY)
        self.btn_add.SetForegroundColour(wx.WHITE)
        self.btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        btn_sizer.Add(self.btn_add, 0, wx.ALL, 5)
        
        # 수정 버튼
        self.btn_update = wx.Button(panel, label="수정", size=(110, 40))
        self.btn_update.SetBackgroundColour(ColorTheme.BTN_SUCCESS)
        self.btn_update.SetForegroundColour(wx.WHITE)
        self.btn_update.Bind(wx.EVT_BUTTON, self.on_update)
        btn_sizer.Add(self.btn_update, 0, wx.ALL, 5)
        
        # 삭제 버튼
        self.btn_delete = wx.Button(panel, label="삭제", size=(110, 40))
        self.btn_delete.SetBackgroundColour(ColorTheme.BTN_DANGER)
        self.btn_delete.SetForegroundColour(wx.WHITE)
        self.btn_delete.Bind(wx.EVT_BUTTON, self.on_delete)
        btn_sizer.Add(self.btn_delete, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        
        # 초기화 버튼
        btn_clear = wx.Button(panel, label="입력 초기화", size=(340, 36))
        btn_clear.SetBackgroundColour(ColorTheme.BTN_SECONDARY)
        btn_clear.SetForegroundColour(wx.WHITE)
        btn_clear.Bind(wx.EVT_BUTTON, self.on_clear)
        sizer.Add(btn_clear, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # 월별 요약
        self.summary_panel = self.create_summary_panel(panel)
        sizer.Add(self.summary_panel, 0, wx.EXPAND | wx.ALL, 15)
        
        panel.SetSizer(sizer)
        
        # 카테고리 초기화
        self.update_categories()
        
        return panel
    
    def create_summary_panel(self, parent):
        """월별 요약 패널"""
        panel = wx.Panel(parent)
        panel.SetBackgroundColour(ColorTheme.BG_HOVER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(panel, label="이번 달 요약")
        font = title.GetFont()
        font.SetPointSize(10)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        title.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        sizer.Add(title, 0, wx.ALL, 10)
        
        # 수입
        self.income_label = wx.StaticText(panel, label="수입: ₩0")
        self.income_label.SetForegroundColour(ColorTheme.INCOME)
        income_font = self.income_label.GetFont()
        income_font.SetPointSize(11)
        self.income_label.SetFont(income_font)
        sizer.Add(self.income_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # 지출
        self.expense_label = wx.StaticText(panel, label="지출: ₩0")
        self.expense_label.SetForegroundColour(ColorTheme.EXPENSE)
        expense_font = self.expense_label.GetFont()
        expense_font.SetPointSize(11)
        self.expense_label.SetFont(expense_font)
        sizer.Add(self.expense_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # 잔액
        self.balance_label = wx.StaticText(panel, label="잔액: ₩0")
        self.balance_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        balance_font = self.balance_label.GetFont()
        balance_font.SetPointSize(12)
        balance_font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.balance_label.SetFont(balance_font)
        sizer.Add(self.balance_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        panel.SetSizer(sizer)
        return panel
    
    def create_list_panel(self):
        """리스트 패널 생성"""
        panel = wx.Panel(self)
        panel.SetBackgroundColour(ColorTheme.BG_CARD)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 타이틀 및 컨트롤
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        title = wx.StaticText(panel, label="거래 내역")
        font = title.GetFont()
        font.SetPointSize(12)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        title.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        header_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        
        header_sizer.AddStretchSpacer()
        
        # 월 선택
        month_label = wx.StaticText(panel, label="조회 월:")
        month_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        header_sizer.Add(month_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.month_choice = wx.ComboBox(panel, size=(120, -1), style=wx.CB_READONLY)
        self.populate_months()
        self.month_choice.Bind(wx.EVT_COMBOBOX, self.on_month_changed)
        header_sizer.Add(self.month_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        # 전체 보기 버튼
        btn_all = wx.Button(panel, label="전체 보기", size=(100, 32))
        btn_all.Bind(wx.EVT_BUTTON, self.on_view_all)
        header_sizer.Add(btn_all, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        
        sizer.Add(header_sizer, 0, wx.EXPAND)
        
        # 구분선
        line = wx.Panel(panel, size=(-1, 1))
        line.SetBackgroundColour(ColorTheme.BORDER)
        sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        
        # 리스트 컨트롤
        self.list_ctrl = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES
        )
        
        # 컬럼 설정
        self.list_ctrl.InsertColumn(0, "ID", width=60)
        self.list_ctrl.InsertColumn(1, "날짜", width=100)
        self.list_ctrl.InsertColumn(2, "구분", width=80)
        self.list_ctrl.InsertColumn(3, "카테고리", width=150)
        self.list_ctrl.InsertColumn(4, "금액", width=130)
        self.list_ctrl.InsertColumn(5, "비고", width=280)
        
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
        
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 15)
        
        panel.SetSizer(sizer)
        return panel
    
    def populate_months(self):
        """월 선택 콤보박스 채우기"""
        months = []
        current = datetime.now()
        
        for i in range(12):
            year = current.year if current.month - i > 0 else current.year - 1
            month = current.month - i if current.month - i > 0 else 12 + (current.month - i)
            months.append(f"{year}-{month:02d}")
        
        self.month_choice.Clear()
        self.month_choice.AppendItems(months)
        self.month_choice.SetSelection(0)
    
    def update_categories(self):
        """카테고리 업데이트"""
        trans_type = self.type_choice.GetStringSelection()
        
        if trans_type == "수입":
            categories = ["급여", "보너스", "용돈", "기타수입"]
        else:
            categories = ["식비", "교통비", "통신비", "쇼핑", "의료", "문화", "주거", "기타"]
        
        self.category_choice.Clear()
        self.category_choice.AppendItems(categories)
        if categories:
            self.category_choice.SetSelection(0)
    
    def on_type_changed(self, event):
        """구분 변경 이벤트"""
        self.update_categories()
    
    def on_amount_changed(self, event):
        """금액 입력 시 자동 포맷팅"""
        value = self.amount_text.GetValue().replace(',', '')
        if value and value.isdigit():
            formatted = f"{int(value):,}"
            pos = self.amount_text.GetInsertionPoint()
            self.amount_text.ChangeValue(formatted)
            # 커서 위치 조정
            self.amount_text.SetInsertionPoint(min(pos + (len(formatted) - len(value)), len(formatted)))
    
    def on_add(self, event):
        """거래 추가"""
        date_value = self.date_picker.GetValue()
        date_str = date_value.FormatISODate()
        trans_type = self.type_choice.GetStringSelection()
        category = self.category_choice.GetValue()
        amount_str = self.amount_text.GetValue().replace(',', '')
        remark = self.remark_text.GetValue()
        
        if not category:
            wx.MessageBox("카테고리를 선택하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        if not amount_str or not amount_str.isdigit():
            wx.MessageBox("올바른 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        amount = float(amount_str)
        
        self.db.insert_transaction(date_str, trans_type, category, amount, remark)
        wx.MessageBox("거래가 추가되었습니다.", "완료", wx.OK | wx.ICON_INFORMATION)
        
        self.on_clear(None)
        self.refresh_list()
        self.update_summary()
    
    def on_update(self, event):
        """거래 수정"""
        if not self.selected_id:
            wx.MessageBox("수정할 항목을 선택하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        date_value = self.date_picker.GetValue()
        date_str = date_value.FormatISODate()
        trans_type = self.type_choice.GetStringSelection()
        category = self.category_choice.GetValue()
        amount_str = self.amount_text.GetValue().replace(',', '')
        remark = self.remark_text.GetValue()
        
        if not category or not amount_str or not amount_str.isdigit():
            wx.MessageBox("올바른 정보를 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        amount = float(amount_str)
        
        self.db.update_transaction(self.selected_id, date_str, trans_type, category, amount, remark)
        wx.MessageBox("거래가 수정되었습니다.", "완료", wx.OK | wx.ICON_INFORMATION)
        
        self.on_clear(None)
        self.refresh_list()
        self.update_summary()
    
    def on_delete(self, event):
        """거래 삭제"""
        if not self.selected_id:
            wx.MessageBox("삭제할 항목을 선택하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        dlg = wx.MessageDialog(
            self,
            "선택한 거래를 삭제하시겠습니까?",
            "삭제 확인",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            self.db.delete_transaction(self.selected_id)
            wx.MessageBox("거래가 삭제되었습니다.", "완료", wx.OK | wx.ICON_INFORMATION)
            self.on_clear(None)
            self.refresh_list()
            self.update_summary()
        
        dlg.Destroy()
    
    def on_clear(self, event):
        """입력 초기화"""
        self.date_picker.SetValue(wx.DateTime.Today())
        self.type_choice.SetSelection(1)
        self.update_categories()
        self.amount_text.Clear()
        self.remark_text.Clear()
        self.selected_id = None
    
    def on_item_selected(self, event):
        """리스트 항목 선택"""
        idx = event.GetIndex()
        self.selected_id = int(self.list_ctrl.GetItemText(idx, 0))
        
        # 선택된 항목의 정보를 입력 폼에 채우기
        date_str = self.list_ctrl.GetItemText(idx, 1)
        trans_type = self.list_ctrl.GetItemText(idx, 2)
        category = self.list_ctrl.GetItemText(idx, 3)
        amount = self.list_ctrl.GetItemText(idx, 4).replace('₩', '').replace(',', '').strip()
        remark = self.list_ctrl.GetItemText(idx, 5)
        
        # 날짜 설정
        date_obj = wx.DateTime()
        date_obj.ParseDate(date_str)
        self.date_picker.SetValue(date_obj)
        
        # 구분 설정
        if trans_type == "수입":
            self.type_choice.SetSelection(0)
        else:
            self.type_choice.SetSelection(1)
        
        self.update_categories()
        self.category_choice.SetValue(category)
        self.amount_text.SetValue(amount)
        self.remark_text.SetValue(remark)
    
    def on_month_changed(self, event):
        """월 변경 이벤트"""
        self.refresh_list()
        self.update_summary()
    
    def on_view_all(self, event):
        """전체 보기"""
        self.load_all_transactions()
        self.update_summary()
    
    def load_current_month(self):
        """현재 월 데이터 로드"""
        self.refresh_list()
        self.update_summary()
    
    def load_all_transactions(self):
        """전체 거래 로드"""
        self.list_ctrl.DeleteAllItems()
        rows = self.db.get_all_transactions()
        
        for row in rows:
            trans_id, date_str, trans_type, category, amount, remark = row
            idx = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), str(trans_id))
            self.list_ctrl.SetItem(idx, 1, date_str)
            self.list_ctrl.SetItem(idx, 2, trans_type)
            self.list_ctrl.SetItem(idx, 3, category)
            self.list_ctrl.SetItem(idx, 4, f"₩{amount:,.0f}")
            self.list_ctrl.SetItem(idx, 5, remark or "")
            
            # 색상 설정
            if trans_type == "수입":
                self.list_ctrl.SetItemTextColour(idx, ColorTheme.INCOME)
            else:
                self.list_ctrl.SetItemTextColour(idx, ColorTheme.EXPENSE)
    
    def refresh_list(self):
        """리스트 새로고침"""
        self.list_ctrl.DeleteAllItems()
        
        selected_month = self.month_choice.GetStringSelection()
        if not selected_month:
            return
        
        rows = self.db.get_transactions_by_month(selected_month)
        
        for row in rows:
            trans_id, date_str, trans_type, category, amount, remark = row
            idx = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), str(trans_id))
            self.list_ctrl.SetItem(idx, 1, date_str)
            self.list_ctrl.SetItem(idx, 2, trans_type)
            self.list_ctrl.SetItem(idx, 3, category)
            self.list_ctrl.SetItem(idx, 4, f"₩{amount:,.0f}")
            self.list_ctrl.SetItem(idx, 5, remark or "")
            
            # 색상 설정
            if trans_type == "수입":
                self.list_ctrl.SetItemTextColour(idx, ColorTheme.INCOME)
            else:
                self.list_ctrl.SetItemTextColour(idx, ColorTheme.EXPENSE)
    
    def update_summary(self):
        """요약 정보 업데이트"""
        selected_month = self.month_choice.GetStringSelection()
        if not selected_month:
            current = datetime.now()
            selected_month = f"{current.year}-{current.month:02d}"
        
        income, expense = self.db.get_monthly_summary(selected_month)
        balance = income - expense
        
        self.income_label.SetLabel(f"수입: ₩{income:,.0f}")
        self.expense_label.SetLabel(f"지출: ₩{expense:,.0f}")
        self.balance_label.SetLabel(f"잔액: ₩{balance:,.0f}")
        
        # 잔액 색상 변경
        if balance >= 0:
            self.balance_label.SetForegroundColour(ColorTheme.INCOME)
        else:
            self.balance_label.SetForegroundColour(ColorTheme.EXPENSE)
        
        self.summary_panel.Layout()


###########################################################################
## 메인 실행
###########################################################################
if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
