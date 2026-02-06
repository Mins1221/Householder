# -*- coding: utf-8 -*- 

###########################################################################
## Modern Smart Household Account Book
## 모던 스마트 가계부 v6.0 - macOS Style UI
###########################################################################

import wx
import wx.xrc
import wx.adv
import re
import csv
from datetime import datetime
from collections import defaultdict

# 모듈 import (실제 환경에 맞게 수정)
try:
    from main import HL_CRUD
    from main.barChart import Barchart
except ImportError:
    # 개발 환경용 더미 클래스
    class HL_CRUD:
        @staticmethod
        def selectMonthList():
            return ['2025-01', '2025-02', '2025-03']
        
        @staticmethod
        def selectAll():
            return []
        
        @staticmethod
        def selectMonthlySum(month):
            return [('', month, '합계', '', '0', '0', '')]
        
        @staticmethod
        def insert(data):
            pass
        
        @staticmethod
        def update(data):
            pass
        
        @staticmethod
        def delete(key):
            pass
    
    class Barchart(wx.Panel):
        def __init__(self, parent):
            super().__init__(parent)
            
        def SetData(self, data):
            pass


###########################################################################
## 색상 테마 설정 - macOS Style
###########################################################################
class ColorTheme:
    # 아이보리 스타일 배경
    BG_PRIMARY = wx.Colour(255, 253, 240)  # Ivory background
    BG_SECONDARY = wx.Colour(255, 255, 250)  # Light ivory
    BG_TERTIARY = wx.Colour(252, 250, 242)  # Warm ivory
    
    # 카드 & 패널
    CARD_BG = wx.Colour(255, 255, 250)
    CARD_SHADOW = wx.Colour(0, 0, 0, 8)  # Subtle shadow
    PANEL_BG = wx.Colour(252, 250, 242)
    
    # 텍스트 컬러
    TEXT_PRIMARY = wx.Colour(28, 28, 30)  # Near black
    TEXT_SECONDARY = wx.Colour(99, 99, 102)  # Gray
    TEXT_TERTIARY = wx.Colour(142, 142, 147)  # Light gray
    
    # macOS 액센트 컬러 (블루)
    ACCENT_BLUE = wx.Colour(0, 122, 255)
    ACCENT_BLUE_HOVER = wx.Colour(10, 132, 255)
    ACCENT_BLUE_PRESSED = wx.Colour(0, 112, 245)
    
    # 시스템 컬러
    SUCCESS = wx.Colour(52, 199, 89)  # Green
    WARNING = wx.Colour(255, 159, 10)  # Orange
    DANGER = wx.Colour(255, 59, 48)  # Red
    INFO = wx.Colour(90, 200, 250)  # Light Blue
    
    # 수입/지출 색상
    INCOME_COLOR = wx.Colour(52, 199, 89)
    EXPENSE_COLOR = wx.Colour(255, 69, 58)
    
    # Border
    BORDER_LIGHT = wx.Colour(220, 220, 225)
    BORDER_MEDIUM = wx.Colour(200, 200, 205)
    
    # Sidebar
    SIDEBAR_BG = wx.Colour(248, 246, 238)
    SIDEBAR_SELECTED = wx.Colour(0, 122, 255, 15)


###########################################################################
## 커스텀 버튼 (macOS 스타일)
###########################################################################
class ModernButton(wx.Button):
    def __init__(self, parent, label="", size=wx.DefaultSize, primary=False, danger=False):
        super().__init__(parent, label=label, size=size, style=wx.BORDER_NONE)
        
        self.primary = primary
        self.danger = danger
        self.is_hovered = False
        self.is_pressed = False
        
        # 기본 스타일 설정
        self.SetupStyle()
        
        # 이벤트 바인딩
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnPress)
        self.Bind(wx.EVT_LEFT_UP, self.OnRelease)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
    
    def SetupStyle(self):
        font = self.GetFont()
        font.SetPointSize(11)
        font.SetWeight(wx.FONTWEIGHT_MEDIUM)
        self.SetFont(font)
        
        if self.primary:
            self.bg_color = ColorTheme.ACCENT_BLUE
            self.fg_color = wx.WHITE
        elif self.danger:
            self.bg_color = ColorTheme.DANGER
            self.fg_color = wx.WHITE
        else:
            self.bg_color = ColorTheme.CARD_BG
            self.fg_color = ColorTheme.TEXT_PRIMARY
        
        self.SetMinSize((100, 36))
    
    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        
        if gc:
            width, height = self.GetSize()
            
            # 배경색 결정
            if self.is_pressed:
                if self.primary:
                    color = ColorTheme.ACCENT_BLUE_PRESSED
                elif self.danger:
                    color = wx.Colour(245, 49, 38)
                else:
                    color = ColorTheme.PANEL_BG
            elif self.is_hovered:
                if self.primary:
                    color = ColorTheme.ACCENT_BLUE_HOVER
                elif self.danger:
                    color = wx.Colour(255, 79, 68)
                else:
                    color = wx.Colour(245, 245, 247)
            else:
                color = self.bg_color
            
            # 둥근 사각형 그리기
            gc.SetBrush(wx.Brush(color))
            if not self.primary and not self.danger:
                gc.SetPen(wx.Pen(ColorTheme.BORDER_LIGHT, 1))
            else:
                gc.SetPen(wx.TRANSPARENT_PEN)
            
            gc.DrawRoundedRectangle(0, 0, width, height, 18)
            
            # 텍스트 그리기
            gc.SetFont(self.GetFont(), self.fg_color)
            text = self.GetLabel()
            text_width, text_height = gc.GetTextExtent(text)
            text_x = (width - text_width) / 2
            text_y = (height - text_height) / 2
            gc.DrawText(text, text_x, text_y)
    
    def OnEnter(self, event):
        self.is_hovered = True
        self.Refresh()
    
    def OnLeave(self, event):
        self.is_hovered = False
        self.Refresh()
    
    def OnPress(self, event):
        self.is_pressed = True
        self.Refresh()
        event.Skip()
    
    def OnRelease(self, event):
        self.is_pressed = False
        self.Refresh()
        event.Skip()


###########################################################################
## 카드 패널 (macOS 스타일)
###########################################################################
class CardPanel(wx.Panel):
    def __init__(self, parent, title="", show_shadow=True):
        super().__init__(parent, style=wx.BORDER_NONE)
        
        self.show_shadow = show_shadow
        self.SetBackgroundColour(ColorTheme.CARD_BG)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        if title:
            title_text = wx.StaticText(self, label=title)
            font = title_text.GetFont()
            font.SetPointSize(16)
            font.SetWeight(wx.FONTWEIGHT_SEMIBOLD)
            title_text.SetFont(font)
            title_text.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
            
            self.main_sizer.Add(title_text, 0, wx.ALL, 20)
            
            # 구분선
            line = wx.Panel(self, size=(-1, 1))
            line.SetBackgroundColour(ColorTheme.BORDER_LIGHT)
            self.main_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        self.SetSizer(self.main_sizer)
        
        # 둥근 모서리 효과를 위한 페인트 이벤트
        self.Bind(wx.EVT_PAINT, self.OnPaint)
    
    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        
        if gc:
            width, height = self.GetSize()
            
            # 그림자 효과 (선택적)
            if self.show_shadow:
                gc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 5)))
                gc.SetPen(wx.TRANSPARENT_PEN)
                gc.DrawRoundedRectangle(2, 2, width-4, height-4, 18)
            
            # 배경
            gc.SetBrush(wx.Brush(ColorTheme.CARD_BG))
            gc.SetPen(wx.Pen(ColorTheme.BORDER_LIGHT, 1))
            gc.DrawRoundedRectangle(0, 0, width, height, 18)


###########################################################################
## 즐겨찾기 관리 다이얼로그 (macOS 스타일)
###########################################################################
class FavoritesDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="즐겨찾기 관리", size=(680, 550), 
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = wx.StaticText(panel, label="⭐ 즐겨찾기 목록")
        font = header.GetFont()
        font.SetPointSize(20)
        font.SetWeight(wx.FONTWEIGHT_SEMIBOLD)
        header.SetFont(font)
        header.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        sizer.Add(header, 0, wx.ALL, 25)
        
        # 즐겨찾기 목록 (카드 스타일)
        list_card = CardPanel(panel, show_shadow=False)
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.favoritesList = wx.ListCtrl(list_card, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_NONE)
        self.favoritesList.InsertColumn(0, "구분", width=110)
        self.favoritesList.InsertColumn(1, "항목", width=200)
        self.favoritesList.InsertColumn(2, "금액", width=140)
        self.favoritesList.InsertColumn(3, "비고", width=190)
        
        self.favoritesList.SetBackgroundColour(ColorTheme.CARD_BG)
        self.favoritesList.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        
        list_sizer.Add(self.favoritesList, 1, wx.EXPAND | wx.ALL, 20)
        list_card.main_sizer.Add(list_sizer, 1, wx.EXPAND)
        
        sizer.Add(list_card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.AddStretchSpacer()
        
        self.btnDelete = ModernButton(panel, "삭제", size=(100, 36), danger=True)
        self.btnApply = ModernButton(panel, "적용", size=(100, 36), primary=True)
        self.btnClose = ModernButton(panel, "닫기", size=(100, 36))
        
        btnSizer.Add(self.btnDelete, 0, wx.RIGHT, 10)
        btnSizer.Add(self.btnApply, 0, wx.RIGHT, 10)
        btnSizer.Add(self.btnClose, 0)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        panel.SetSizer(sizer)
        
        # 이벤트 바인딩
        self.btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        self.btnApply.Bind(wx.EVT_BUTTON, self.OnApply)
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnClose)
        
        self.LoadFavorites()
        
        self.selected_favorite = None
    
    def LoadFavorites(self):
        self.favoritesList.DeleteAllItems()
        try:
            with open('favorites.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 4:
                        idx = self.favoritesList.InsertItem(self.favoritesList.GetItemCount(), row[0])
                        self.favoritesList.SetItem(idx, 1, row[1])
                        self.favoritesList.SetItem(idx, 2, row[2])
                        self.favoritesList.SetItem(idx, 3, row[3])
        except FileNotFoundError:
            pass
    
    def OnDelete(self, event):
        idx = self.favoritesList.GetFirstSelected()
        if idx == -1:
            wx.MessageBox("삭제할 항목을 선택하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        if wx.MessageBox("선택한 즐겨찾기를 삭제하시겠습니까?", "확인", 
                        wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            self.favoritesList.DeleteItem(idx)
            self.SaveFavorites()
    
    def OnApply(self, event):
        idx = self.favoritesList.GetFirstSelected()
        if idx == -1:
            wx.MessageBox("적용할 항목을 선택하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        section = self.favoritesList.GetItemText(idx, 0)
        title = self.favoritesList.GetItemText(idx, 1)
        amount = self.favoritesList.GetItemText(idx, 2)
        remark = self.favoritesList.GetItemText(idx, 3)
        
        self.selected_favorite = (section, title, amount, remark)
        self.EndModal(wx.ID_OK)
    
    def OnClose(self, event):
        self.EndModal(wx.ID_CANCEL)
    
    def SaveFavorites(self):
        try:
            with open('favorites.csv', 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for i in range(self.favoritesList.GetItemCount()):
                    row = [
                        self.favoritesList.GetItemText(i, 0),
                        self.favoritesList.GetItemText(i, 1),
                        self.favoritesList.GetItemText(i, 2),
                        self.favoritesList.GetItemText(i, 3)
                    ]
                    writer.writerow(row)
        except Exception as e:
            wx.MessageBox(f"저장 실패: {str(e)}", "오류", wx.OK | wx.ICON_ERROR)
    
    def GetSelectedFavorite(self):
        return self.selected_favorite


###########################################################################
## 검색 다이얼로그 (macOS 스타일)
###########################################################################
class SearchDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="고급 검색", size=(550, 480),
                        style=wx.DEFAULT_DIALOG_STYLE)
        
        self.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = wx.StaticText(panel, label="🔍 고급 검색")
        font = header.GetFont()
        font.SetPointSize(20)
        font.SetWeight(wx.FONTWEIGHT_SEMIBOLD)
        header.SetFont(font)
        header.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        sizer.Add(header, 0, wx.ALL, 25)
        
        # 검색 옵션 카드
        card = CardPanel(panel, show_shadow=False)
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 날짜 범위
        date_sizer = wx.FlexGridSizer(2, 2, 15, 20)
        date_sizer.AddGrowableCol(1, 1)
        
        start_label = wx.StaticText(card, label="시작 날짜")
        start_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.startDate = wx.adv.DatePickerCtrl(card, style=wx.adv.DP_DROPDOWN)
        
        end_label = wx.StaticText(card, label="종료 날짜")
        end_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.endDate = wx.adv.DatePickerCtrl(card, style=wx.adv.DP_DROPDOWN)
        
        date_sizer.Add(start_label, 0, wx.ALIGN_CENTER_VERTICAL)
        date_sizer.Add(self.startDate, 1, wx.EXPAND)
        date_sizer.Add(end_label, 0, wx.ALIGN_CENTER_VERTICAL)
        date_sizer.Add(self.endDate, 1, wx.EXPAND)
        
        card_sizer.Add(date_sizer, 0, wx.EXPAND | wx.ALL, 20)
        
        # 구분선
        line = wx.Panel(card, size=(-1, 1))
        line.SetBackgroundColour(ColorTheme.BORDER_LIGHT)
        card_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        # 타입 선택
        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_label = wx.StaticText(card, label="구분")
        type_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        
        self.chkIncome = wx.CheckBox(card, label="수입")
        self.chkExpense = wx.CheckBox(card, label="지출")
        self.chkIncome.SetValue(True)
        self.chkExpense.SetValue(True)
        
        type_sizer.Add(type_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
        type_sizer.Add(self.chkIncome, 0, wx.RIGHT, 20)
        type_sizer.Add(self.chkExpense, 0)
        
        card_sizer.Add(type_sizer, 0, wx.ALL, 20)
        
        # 구분선
        line2 = wx.Panel(card, size=(-1, 1))
        line2.SetBackgroundColour(ColorTheme.BORDER_LIGHT)
        card_sizer.Add(line2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        # 금액 범위
        amount_sizer = wx.FlexGridSizer(2, 2, 15, 20)
        amount_sizer.AddGrowableCol(1, 1)
        
        min_label = wx.StaticText(card, label="최소 금액")
        min_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.txtMinAmount = wx.TextCtrl(card)
        
        max_label = wx.StaticText(card, label="최대 금액")
        max_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.txtMaxAmount = wx.TextCtrl(card)
        
        amount_sizer.Add(min_label, 0, wx.ALIGN_CENTER_VERTICAL)
        amount_sizer.Add(self.txtMinAmount, 1, wx.EXPAND)
        amount_sizer.Add(max_label, 0, wx.ALIGN_CENTER_VERTICAL)
        amount_sizer.Add(self.txtMaxAmount, 1, wx.EXPAND)
        
        card_sizer.Add(amount_sizer, 0, wx.EXPAND | wx.ALL, 20)
        
        # 구분선
        line3 = wx.Panel(card, size=(-1, 1))
        line3.SetBackgroundColour(ColorTheme.BORDER_LIGHT)
        card_sizer.Add(line3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        # 키워드
        keyword_sizer = wx.BoxSizer(wx.HORIZONTAL)
        keyword_label = wx.StaticText(card, label="키워드")
        keyword_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.txtKeyword = wx.TextCtrl(card, size=(300, -1))
        
        keyword_sizer.Add(keyword_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
        keyword_sizer.Add(self.txtKeyword, 1, wx.EXPAND)
        
        card_sizer.Add(keyword_sizer, 0, wx.EXPAND | wx.ALL, 20)
        
        card.main_sizer.Add(card_sizer, 1, wx.EXPAND)
        sizer.Add(card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.AddStretchSpacer()
        
        self.btnSearch = ModernButton(panel, "검색", size=(120, 40), primary=True)
        self.btnCancel = ModernButton(panel, "취소", size=(120, 40))
        
        btnSizer.Add(self.btnSearch, 0, wx.RIGHT, 10)
        btnSizer.Add(self.btnCancel, 0)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        panel.SetSizer(sizer)
        
        # 이벤트 바인딩
        self.btnSearch.Bind(wx.EVT_BUTTON, self.OnSearch)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
    
    def OnSearch(self, event):
        self.EndModal(wx.ID_OK)
    
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
    
    def GetSearchCriteria(self):
        start = self.startDate.GetValue()
        end = self.endDate.GetValue()
        
        return {
            'start_date': start.FormatISODate(),
            'end_date': end.FormatISODate(),
            'include_income': self.chkIncome.GetValue(),
            'include_expense': self.chkExpense.GetValue(),
            'min_amount': self.txtMinAmount.GetValue(),
            'max_amount': self.txtMaxAmount.GetValue(),
            'keyword': self.txtKeyword.GetValue()
        }


###########################################################################
## 통계 다이얼로그 (macOS 스타일)
###########################################################################
class StatisticsDialog(wx.Dialog):
    def __init__(self, parent, data):
        super().__init__(parent, title="통계 분석", size=(750, 600),
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = wx.StaticText(panel, label="📊 통계 분석")
        font = header.GetFont()
        font.SetPointSize(20)
        font.SetWeight(wx.FONTWEIGHT_SEMIBOLD)
        header.SetFont(font)
        header.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        sizer.Add(header, 0, wx.ALL, 25)
        
        # 통계 정보 계산
        total_income = 0
        total_expense = 0
        income_count = 0
        expense_count = 0
        
        for row in data:
            if row[2] == '수입':
                total_income += float(row[4]) if row[4] else 0
                income_count += 1
            else:
                total_expense += float(row[5]) if row[5] else 0
                expense_count += 1
        
        balance = total_income - total_expense
        
        # 통계 카드들
        stats_grid = wx.GridSizer(2, 2, 20, 20)
        
        # 총 수입 카드
        income_card = self.CreateStatCard(panel, "총 수입", f"{total_income:,.0f}원", 
                                         f"거래 {income_count}건", ColorTheme.INCOME_COLOR)
        stats_grid.Add(income_card, 1, wx.EXPAND)
        
        # 총 지출 카드
        expense_card = self.CreateStatCard(panel, "총 지출", f"{total_expense:,.0f}원",
                                          f"거래 {expense_count}건", ColorTheme.EXPENSE_COLOR)
        stats_grid.Add(expense_card, 1, wx.EXPAND)
        
        # 잔액 카드
        balance_color = ColorTheme.INCOME_COLOR if balance >= 0 else ColorTheme.EXPENSE_COLOR
        balance_card = self.CreateStatCard(panel, "잔액", f"{balance:,.0f}원",
                                          "수입 - 지출", balance_color)
        stats_grid.Add(balance_card, 1, wx.EXPAND)
        
        # 평균 지출 카드
        avg_expense = total_expense / expense_count if expense_count > 0 else 0
        avg_card = self.CreateStatCard(panel, "평균 지출", f"{avg_expense:,.0f}원",
                                      "거래당 평균", ColorTheme.INFO)
        stats_grid.Add(avg_card, 1, wx.EXPAND)
        
        sizer.Add(stats_grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        # 카테고리별 분석
        category_card = CardPanel(panel, "카테고리별 지출", show_shadow=False)
        category_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 카테고리별 집계
        category_data = defaultdict(float)
        for row in data:
            if row[2] == '지출':
                category = row[3].split('.')[0] if '.' in row[3] else row[3]
                amount = float(row[5]) if row[5] else 0
                category_data[category] += amount
        
        # 상위 5개 카테고리
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for category, amount in sorted_categories:
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            
            item_sizer = wx.BoxSizer(wx.HORIZONTAL)
            
            cat_label = wx.StaticText(category_card, label=category)
            cat_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
            
            amount_label = wx.StaticText(category_card, label=f"{amount:,.0f}원 ({percentage:.1f}%)")
            amount_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
            
            item_sizer.Add(cat_label, 1)
            item_sizer.Add(amount_label, 0)
            
            category_sizer.Add(item_sizer, 0, wx.EXPAND | wx.ALL, 15)
            
            # 진행바
            progress = wx.Gauge(category_card, range=100, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
            progress.SetValue(int(percentage))
            category_sizer.Add(progress, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        
        category_card.main_sizer.Add(category_sizer, 1, wx.EXPAND)
        sizer.Add(category_card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        # 닫기 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.AddStretchSpacer()
        
        btn_close = ModernButton(panel, "닫기", size=(120, 40), primary=True)
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        btnSizer.Add(btn_close, 0)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        panel.SetSizer(sizer)
    
    def CreateStatCard(self, parent, title, value, subtitle, color):
        card = CardPanel(parent, show_shadow=False)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(card, label=title)
        title_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        font = title_label.GetFont()
        font.SetPointSize(11)
        title_label.SetFont(font)
        sizer.Add(title_label, 0, wx.ALL, 15)
        
        value_label = wx.StaticText(card, label=value)
        value_label.SetForegroundColour(color)
        font = value_label.GetFont()
        font.SetPointSize(24)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        value_label.SetFont(font)
        sizer.Add(value_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        
        subtitle_label = wx.StaticText(card, label=subtitle)
        subtitle_label.SetForegroundColour(ColorTheme.TEXT_TERTIARY)
        font = subtitle_label.GetFont()
        font.SetPointSize(10)
        subtitle_label.SetFont(font)
        sizer.Add(subtitle_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        
        card.main_sizer.Add(sizer, 1, wx.EXPAND)
        return card


###########################################################################
## 예산 관리 다이얼로그 (macOS 스타일)
###########################################################################
class BudgetDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="예산 관리", size=(550, 400),
                        style=wx.DEFAULT_DIALOG_STYLE)
        
        self.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = wx.StaticText(panel, label="💰 예산 관리")
        font = header.GetFont()
        font.SetPointSize(20)
        font.SetWeight(wx.FONTWEIGHT_SEMIBOLD)
        header.SetFont(font)
        header.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        sizer.Add(header, 0, wx.ALL, 25)
        
        # 예산 설정 카드
        card = CardPanel(panel, show_shadow=False)
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 월별 예산
        budget_sizer = wx.BoxSizer(wx.HORIZONTAL)
        budget_label = wx.StaticText(card, label="월 예산")
        budget_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        font = budget_label.GetFont()
        font.SetPointSize(12)
        budget_label.SetFont(font)
        
        self.txtBudget = wx.TextCtrl(card, size=(250, 36))
        won_label = wx.StaticText(card, label="원")
        won_label.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        
        budget_sizer.Add(budget_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
        budget_sizer.Add(self.txtBudget, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        budget_sizer.Add(won_label, 0, wx.ALIGN_CENTER_VERTICAL)
        
        card_sizer.Add(budget_sizer, 0, wx.ALL, 20)
        
        # 구분선
        line = wx.Panel(card, size=(-1, 1))
        line.SetBackgroundColour(ColorTheme.BORDER_LIGHT)
        card_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        # 알림 설정
        alert_sizer = wx.BoxSizer(wx.VERTICAL)
        
        alert_label = wx.StaticText(card, label="알림 설정")
        alert_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        font = alert_label.GetFont()
        font.SetPointSize(12)
        alert_label.SetFont(font)
        alert_sizer.Add(alert_label, 0, wx.BOTTOM, 15)
        
        self.chk80 = wx.CheckBox(card, label="예산의 80% 도달 시 알림")
        self.chk100 = wx.CheckBox(card, label="예산 초과 시 알림")
        self.chkDaily = wx.CheckBox(card, label="일일 지출 요약 알림")
        
        alert_sizer.Add(self.chk80, 0, wx.BOTTOM, 10)
        alert_sizer.Add(self.chk100, 0, wx.BOTTOM, 10)
        alert_sizer.Add(self.chkDaily, 0)
        
        card_sizer.Add(alert_sizer, 0, wx.ALL, 20)
        
        card.main_sizer.Add(card_sizer, 1, wx.EXPAND)
        sizer.Add(card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.AddStretchSpacer()
        
        btn_save = ModernButton(panel, "저장", size=(120, 40), primary=True)
        btn_cancel = ModernButton(panel, "취소", size=(120, 40))
        
        btn_save.Bind(wx.EVT_BUTTON, self.OnSave)
        btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        
        btnSizer.Add(btn_save, 0, wx.RIGHT, 10)
        btnSizer.Add(btn_cancel, 0)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 25)
        
        panel.SetSizer(sizer)
        
        self.LoadBudget()
    
    def LoadBudget(self):
        try:
            with open('budget.txt', 'r', encoding='utf-8') as f:
                data = f.read().split(',')
                if len(data) >= 4:
                    self.txtBudget.SetValue(data[0])
                    self.chk80.SetValue(data[1] == '1')
                    self.chk100.SetValue(data[2] == '1')
                    self.chkDaily.SetValue(data[3] == '1')
        except FileNotFoundError:
            pass
    
    def OnSave(self, event):
        budget = self.txtBudget.GetValue()
        if not budget:
            wx.MessageBox("예산을 입력하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            float(budget.replace(',', ''))
        except ValueError:
            wx.MessageBox("올바른 금액을 입력하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            with open('budget.txt', 'w', encoding='utf-8') as f:
                data = [
                    budget,
                    '1' if self.chk80.GetValue() else '0',
                    '1' if self.chk100.GetValue() else '0',
                    '1' if self.chkDaily.GetValue() else '0'
                ]
                f.write(','.join(data))
            
            wx.MessageBox("예산이 저장되었습니다.", "저장 완료", wx.OK | wx.ICON_INFORMATION)
            self.EndModal(wx.ID_OK)
        except Exception as e:
            wx.MessageBox(f"저장 실패: {str(e)}", "오류", wx.OK | wx.ICON_ERROR)


###########################################################################
## 메인 프레임 (macOS 스타일)
###########################################################################
class MyFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="💰 스마트 가계부", size=(1280, 820))
        
        self.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        # 메뉴바
        self.CreateMenuBar()
        
        # 메인 패널
        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour(ColorTheme.BG_PRIMARY)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 상단 헤더
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        title = wx.StaticText(main_panel, label="스마트 가계부")
        font = title.GetFont()
        font.SetPointSize(24)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        title.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        
        header_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
        header_sizer.AddStretchSpacer()
        
        # 상단 버튼들
        btn_stats = ModernButton(main_panel, "📊 통계", size=(100, 36))
        btn_budget = ModernButton(main_panel, "💰 예산", size=(100, 36))
        btn_export = ModernButton(main_panel, "📤 내보내기", size=(120, 36))
        
        btn_stats.Bind(wx.EVT_BUTTON, self.OnStatistics)
        btn_budget.Bind(wx.EVT_BUTTON, self.OnBudget)
        btn_export.Bind(wx.EVT_BUTTON, self.OnExport)
        
        header_sizer.Add(btn_stats, 0, wx.RIGHT, 10)
        header_sizer.Add(btn_budget, 0, wx.RIGHT, 10)
        header_sizer.Add(btn_export, 0)
        
        main_sizer.Add(header_sizer, 0, wx.EXPAND | wx.ALL, 25)
        
        # 컨텐츠 영역 (2열 레이아웃)
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 왼쪽: 입력 영역
        left_panel = self.CreateInputPanel(main_panel)
        content_sizer.Add(left_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        
        # 오른쪽: 목록 영역
        right_panel = self.CreateListPanel(main_panel)
        content_sizer.Add(right_panel, 2, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        
        main_sizer.Add(content_sizer, 1, wx.EXPAND)
        
        # 하단 그래프 영역
        graph_panel = self.CreateGraphPanel(main_panel)
        main_sizer.Add(graph_panel, 0, wx.EXPAND | wx.ALL, 25)
        
        main_panel.SetSizer(main_sizer)
        
        # 초기 데이터 로드
        self.OnSelectAll(None)
        
        self.Centre()
    
    def CreateMenuBar(self):
        menubar = wx.MenuBar()
        
        # 파일 메뉴
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_ANY, "📥 가져오기\tCtrl+I")
        file_menu.Append(wx.ID_ANY, "📤 내보내기\tCtrl+E")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "종료\tCtrl+Q")
        
        # 편집 메뉴
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_ANY, "✏️ 수정\tCtrl+M")
        edit_menu.Append(wx.ID_ANY, "🗑️ 삭제\tCtrl+D")
        edit_menu.AppendSeparator()
        edit_menu.Append(wx.ID_ANY, "🔍 검색\tCtrl+F")
        
        # 도구 메뉴
        tools_menu = wx.Menu()
        tools_menu.Append(wx.ID_ANY, "📊 통계\tCtrl+T")
        tools_menu.Append(wx.ID_ANY, "💰 예산\tCtrl+B")
        tools_menu.Append(wx.ID_ANY, "⭐ 즐겨찾기\tCtrl+K")
        tools_menu.Append(wx.ID_ANY, "📈 그래프\tCtrl+G")
        
        menubar.Append(file_menu, "파일")
        menubar.Append(edit_menu, "편집")
        menubar.Append(tools_menu, "도구")
        
        self.SetMenuBar(menubar)
        
        # 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.OnImport, id=file_menu.FindItem("📥 가져오기\tCtrl+I"))
        self.Bind(wx.EVT_MENU, self.OnExport, id=file_menu.FindItem("📤 내보내기\tCtrl+E"))
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnUpdate, id=edit_menu.FindItem("✏️ 수정\tCtrl+M"))
        self.Bind(wx.EVT_MENU, self.OnDelete, id=edit_menu.FindItem("🗑️ 삭제\tCtrl+D"))
        self.Bind(wx.EVT_MENU, self.OnSearch, id=edit_menu.FindItem("🔍 검색\tCtrl+F"))
        self.Bind(wx.EVT_MENU, self.OnStatistics, id=tools_menu.FindItem("📊 통계\tCtrl+T"))
        self.Bind(wx.EVT_MENU, self.OnBudget, id=tools_menu.FindItem("💰 예산\tCtrl+B"))
        self.Bind(wx.EVT_MENU, self.OnFavorites, id=tools_menu.FindItem("⭐ 즐겨찾기\tCtrl+K"))
        self.Bind(wx.EVT_MENU, self.OnMakeGraph, id=tools_menu.FindItem("📈 그래프\tCtrl+G"))
    
    def CreateInputPanel(self, parent):
        card = CardPanel(parent, "거래 입력", show_shadow=True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 날짜 선택
        date_sizer = wx.BoxSizer(wx.HORIZONTAL)
        date_label = wx.StaticText(card, label="날짜")
        date_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.dateCtrl = wx.adv.DatePickerCtrl(card, style=wx.adv.DP_DROPDOWN)
        self.dateCtrl.SetValue(wx.DateTime.Today())
        
        date_sizer.Add(date_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        date_sizer.Add(self.dateCtrl, 1, wx.EXPAND)
        
        sizer.Add(date_sizer, 0, wx.EXPAND | wx.ALL, 20)
        
        # 탭 (수입/지출)
        self.notebook = wx.Notebook(card)
        
        # 수입 탭
        income_panel = wx.Panel(self.notebook)
        income_panel.SetBackgroundColour(ColorTheme.CARD_BG)
        income_sizer = wx.BoxSizer(wx.VERTICAL)
        
        income_category_sizer = wx.BoxSizer(wx.HORIZONTAL)
        income_cat_label = wx.StaticText(income_panel, label="항목")
        income_cat_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.comboRevenue = wx.ComboBox(income_panel, choices=['급여', '보너스', '부수입', '이자', '기타'])
        income_category_sizer.Add(income_cat_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        income_category_sizer.Add(self.comboRevenue, 1, wx.EXPAND)
        income_sizer.Add(income_category_sizer, 0, wx.EXPAND | wx.ALL, 15)
        
        income_amount_sizer = wx.BoxSizer(wx.HORIZONTAL)
        income_amt_label = wx.StaticText(income_panel, label="금액")
        income_amt_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.txtRevenue = wx.TextCtrl(income_panel, size=(200, -1))
        income_won = wx.StaticText(income_panel, label="원")
        income_won.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        income_amount_sizer.Add(income_amt_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        income_amount_sizer.Add(self.txtRevenue, 1, wx.EXPAND | wx.RIGHT, 10)
        income_amount_sizer.Add(income_won, 0, wx.ALIGN_CENTER_VERTICAL)
        income_sizer.Add(income_amount_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        
        income_panel.SetSizer(income_sizer)
        
        # 지출 탭
        expense_panel = wx.Panel(self.notebook)
        expense_panel.SetBackgroundColour(ColorTheme.CARD_BG)
        expense_sizer = wx.BoxSizer(wx.VERTICAL)
        
        expense_category_sizer = wx.BoxSizer(wx.HORIZONTAL)
        expense_cat_label = wx.StaticText(expense_panel, label="항목")
        expense_cat_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.comboExpense = wx.ComboBox(expense_panel, choices=['식비', '교통비', '주거비', '통신비', '의료비', '교육비', '문화생활', '쇼핑', '기타'])
        expense_category_sizer.Add(expense_cat_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        expense_category_sizer.Add(self.comboExpense, 1, wx.EXPAND)
        expense_sizer.Add(expense_category_sizer, 0, wx.EXPAND | wx.ALL, 15)
        
        expense_amount_sizer = wx.BoxSizer(wx.HORIZONTAL)
        expense_amt_label = wx.StaticText(expense_panel, label="금액")
        expense_amt_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.txtExpense = wx.TextCtrl(expense_panel, size=(200, -1))
        expense_won = wx.StaticText(expense_panel, label="원")
        expense_won.SetForegroundColour(ColorTheme.TEXT_SECONDARY)
        expense_amount_sizer.Add(expense_amt_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        expense_amount_sizer.Add(self.txtExpense, 1, wx.EXPAND | wx.RIGHT, 10)
        expense_amount_sizer.Add(expense_won, 0, wx.ALIGN_CENTER_VERTICAL)
        expense_sizer.Add(expense_amount_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        
        expense_panel.SetSizer(expense_sizer)
        
        self.notebook.AddPage(income_panel, "💰 수입")
        self.notebook.AddPage(expense_panel, "💸 지출")
        
        sizer.Add(self.notebook, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 비고
        remark_sizer = wx.BoxSizer(wx.HORIZONTAL)
        remark_label = wx.StaticText(card, label="비고")
        remark_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        self.txtRemark = wx.TextCtrl(card, style=wx.TE_MULTILINE, size=(-1, 80))
        
        remark_sizer.Add(remark_label, 0, wx.ALIGN_TOP | wx.RIGHT, 15)
        remark_sizer.Add(self.txtRemark, 1, wx.EXPAND)
        
        sizer.Add(remark_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 버튼들
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btn_favorite = ModernButton(card, "⭐ 즐겨찾기", size=(120, 40))
        btn_insert = ModernButton(card, "추가", size=(100, 40), primary=True)
        btn_clear = ModernButton(card, "초기화", size=(100, 40))
        
        btn_favorite.Bind(wx.EVT_BUTTON, self.OnFavorites)
        btn_insert.Bind(wx.EVT_BUTTON, self.OnInsert)
        btn_clear.Bind(wx.EVT_BUTTON, lambda e: self.ClearInputs())
        
        btn_sizer.Add(btn_favorite, 0, wx.RIGHT, 10)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(btn_insert, 0, wx.RIGHT, 10)
        btn_sizer.Add(btn_clear, 0)
        
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        card.main_sizer.Add(sizer, 1, wx.EXPAND)
        return card
    
    def CreateListPanel(self, parent):
        card = CardPanel(parent, "거래 내역", show_shadow=True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 필터 및 검색
        filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        month_label = wx.StaticText(card, label="월 선택")
        month_label.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        
        self.comboMonth = wx.ComboBox(card, choices=HL_CRUD.selectMonthList(), style=wx.CB_READONLY)
        if self.comboMonth.GetCount() > 0:
            self.comboMonth.SetSelection(0)
        
        btn_search = ModernButton(card, "🔍 검색", size=(100, 32))
        btn_refresh = ModernButton(card, "🔄 새로고침", size=(120, 32))
        
        btn_search.Bind(wx.EVT_BUTTON, self.OnSearch)
        btn_refresh.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        self.comboMonth.Bind(wx.EVT_COMBOBOX, self.OnMonthSelect)
        
        filter_sizer.Add(month_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        filter_sizer.Add(self.comboMonth, 0, wx.RIGHT, 15)
        filter_sizer.AddStretchSpacer()
        filter_sizer.Add(btn_search, 0, wx.RIGHT, 10)
        filter_sizer.Add(btn_refresh, 0)
        
        sizer.Add(filter_sizer, 0, wx.EXPAND | wx.ALL, 20)
        
        # 리스트
        self.list = wx.ListCtrl(card, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_NONE)
        self.list.InsertColumn(0, "번호", width=60)
        self.list.InsertColumn(1, "날짜", width=100)
        self.list.InsertColumn(2, "구분", width=80)
        self.list.InsertColumn(3, "내역", width=150)
        self.list.InsertColumn(4, "수입", width=120)
        self.list.InsertColumn(5, "지출", width=120)
        self.list.InsertColumn(6, "비고", width=180)
        
        self.list.SetBackgroundColour(ColorTheme.CARD_BG)
        self.list.SetForegroundColour(ColorTheme.TEXT_PRIMARY)
        
        sizer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 버튼들
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btn_update = ModernButton(card, "✏️ 수정", size=(100, 36))
        btn_delete = ModernButton(card, "🗑️ 삭제", size=(100, 36), danger=True)
        btn_load = ModernButton(card, "불러오기", size=(100, 36))
        
        btn_update.Bind(wx.EVT_BUTTON, self.OnUpdate)
        btn_delete.Bind(wx.EVT_BUTTON, self.OnDelete)
        btn_load.Bind(wx.EVT_BUTTON, self.OnLoadToInput)
        
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(btn_update, 0, wx.RIGHT, 10)
        btn_sizer.Add(btn_delete, 0, wx.RIGHT, 10)
        btn_sizer.Add(btn_load, 0)
        
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        card.main_sizer.Add(sizer, 1, wx.EXPAND)
        return card
    
    def CreateGraphPanel(self, parent):
        card = CardPanel(parent, "지출 분석 그래프", show_shadow=True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 그래프
        self.graphPanel = Barchart(card)
        self.graphPanel.SetBackgroundColour(ColorTheme.CARD_BG)
        self.graphPanel.SetMinSize((-1, 250))
        
        sizer.Add(self.graphPanel, 1, wx.EXPAND | wx.ALL, 20)
        
        # 그래프 생성 버튼
        btn_graph = ModernButton(card, "📊 그래프 생성", size=(140, 40), primary=True)
        btn_graph.Bind(wx.EVT_BUTTON, self.OnMakeGraph)
        
        sizer.Add(btn_graph, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        
        card.main_sizer.Add(sizer, 1, wx.EXPAND)
        return card
    
    def OnInsert(self, event):
        date_str = self.dateCtrl.GetValue().FormatISODate()
        
        current_tab = self.notebook.GetSelection()
        
        if current_tab == 0:  # 수입
            section = '수입'
            title = self.comboRevenue.GetValue()
            amount = self.txtRevenue.GetValue()
            revenue = amount.replace(',', '') if amount else '0'
            expense = '0'
        else:  # 지출
            section = '지출'
            title = self.comboExpense.GetValue()
            amount = self.txtExpense.GetValue()
            revenue = '0'
            expense = amount.replace(',', '') if amount else '0'
        
        remark = self.txtRemark.GetValue()
        
        # 유효성 검사
        if not title:
            wx.MessageBox("항목을 선택하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        if not amount or amount == '0':
            wx.MessageBox("금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            float(amount.replace(',', ''))
        except ValueError:
            wx.MessageBox("올바른 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        # 데이터 삽입
        HL_CRUD.insert((date_str, section, title, revenue, expense, remark))
        
        wx.MessageBox("거래가 추가되었습니다.", "추가 완료", wx.OK | wx.ICON_INFORMATION)
        
        self.ClearInputs()
        self.OnSelectAll(None)
    
    def OnSelectAll(self, event):
        self.list.DeleteAllItems()
        rows = HL_CRUD.selectAll()
        
        for row in rows:
            idx = self.list.InsertItem(self.list.GetItemCount(), str(row[0]))
            self.list.SetItem(idx, 1, row[1])
            self.list.SetItem(idx, 2, row[2])
            self.list.SetItem(idx, 3, row[3])
            self.list.SetItem(idx, 4, f"{float(row[4]):,.0f}" if row[4] else "0")
            self.list.SetItem(idx, 5, f"{float(row[5]):,.0f}" if row[5] else "0")
            self.list.SetItem(idx, 6, row[6])
            
            # 수입/지출에 따른 색상 (선택적)
            if row[2] == '수입':
                self.list.SetItemTextColour(idx, ColorTheme.INCOME_COLOR)
            else:
                self.list.SetItemTextColour(idx, ColorTheme.EXPENSE_COLOR)
    
    def OnMonthSelect(self, event):
        selected_month = self.comboMonth.GetValue()
        if not selected_month:
            return
        
        self.list.DeleteAllItems()
        rows = HL_CRUD.selectMonthlySum(selected_month)
        
        for row in rows:
            idx = self.list.InsertItem(self.list.GetItemCount(), str(row[0]))
            self.list.SetItem(idx, 1, row[1])
            self.list.SetItem(idx, 2, row[2])
            self.list.SetItem(idx, 3, row[3])
            self.list.SetItem(idx, 4, f"{float(row[4]):,.0f}" if row[4] else "0")
            self.list.SetItem(idx, 5, f"{float(row[5]):,.0f}" if row[5] else "0")
            self.list.SetItem(idx, 6, row[6])
    
    def OnUpdate(self, event):
        idx = self.list.GetFirstSelected()
        if idx == -1:
            wx.MessageBox("수정할 항목을 선택하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        key = self.list.GetItemText(idx, 0)
        date_str = self.dateCtrl.GetValue().FormatISODate()
        
        current_tab = self.notebook.GetSelection()
        
        if current_tab == 0:
            section = '수입'
            title = self.comboRevenue.GetValue()
            amount = self.txtRevenue.GetValue()
            revenue = amount.replace(',', '') if amount else '0'
            expense = '0'
        else:
            section = '지출'
            title = self.comboExpense.GetValue()
            amount = self.txtExpense.GetValue()
            revenue = '0'
            expense = amount.replace(',', '') if amount else '0'
        
        remark = self.txtRemark.GetValue()
        
        if not title or not amount:
            wx.MessageBox("모든 필드를 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        HL_CRUD.update((key, date_str, section, title, revenue, expense, remark))
        
        wx.MessageBox("거래가 수정되었습니다.", "수정 완료", wx.OK | wx.ICON_INFORMATION)
        
        self.OnSelectAll(None)
    
    def OnDelete(self, event):
        idx = self.list.GetFirstSelected()
        if idx == -1:
            wx.MessageBox("삭제할 항목을 선택하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        if wx.MessageBox("선택한 거래를 삭제하시겠습니까?", "확인",
                        wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            key = self.list.GetItemText(idx, 0)
            HL_CRUD.delete(key)
            
            wx.MessageBox("거래가 삭제되었습니다.", "삭제 완료", wx.OK | wx.ICON_INFORMATION)
            
            self.OnSelectAll(None)
    
    def OnLoadToInput(self, event):
        idx = self.list.GetFirstSelected()
        if idx == -1:
            wx.MessageBox("불러올 항목을 선택하세요.", "알림", wx.OK | wx.ICON_WARNING)
            return
        
        date_str = self.list.GetItemText(idx, 1)
        section = self.list.GetItemText(idx, 2)
        title = self.list.GetItemText(idx, 3)
        revenue = self.list.GetItemText(idx, 4).replace(',', '')
        expense = self.list.GetItemText(idx, 5).replace(',', '')
        remark = self.list.GetItemText(idx, 6)
        
        # 날짜 설정
        try:
            date = wx.DateTime()
            date.ParseDate(date_str)
            self.dateCtrl.SetValue(date)
        except:
            pass
        
        # 섹션에 따라 탭 전환
        if section == '수입':
            self.notebook.SetSelection(0)
            self.comboRevenue.SetValue(title)
            self.txtRevenue.SetValue(revenue if revenue != '0' else '')
        else:
            self.notebook.SetSelection(1)
            self.comboExpense.SetValue(title)
            self.txtExpense.SetValue(expense if expense != '0' else '')
        
        self.txtRemark.SetValue(remark)
    
    def ClearInputs(self):
        self.txtRevenue.Clear()
        self.txtExpense.Clear()
        self.txtRemark.Clear()
        self.comboRevenue.SetValue('')
        self.comboExpense.SetValue('')
        self.dateCtrl.SetValue(wx.DateTime.Today())
    
    def OnMakeGraph(self, event):
        rows = HL_CRUD.selectAll()
        expense_data = defaultdict(float)
        
        for row in rows:
            if row[2] == '지출':
                title = row[3].split('.')[0] if '.' in row[3] else row[3]
                try:
                    amount = float(row[5]) if row[5] else 0
                    if amount > 0:
                        expense_data[title] += amount / 1000
                except (ValueError, TypeError):
                    continue
        
        if expense_data:
            self.graphPanel.SetData(dict(expense_data))
            wx.MessageBox("그래프가 생성되었습니다.", "그래프 생성", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("표시할 지출 데이터가 없습니다.", "그래프 생성", wx.OK | wx.ICON_WARNING)
    
    def OnExport(self, event):
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill
            
            dlg = wx.FileDialog(
                self, "Excel 파일로 저장",
                wildcard="Excel files (*.xlsx)|*.xlsx",
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            )
            
            if dlg.ShowModal() == wx.ID_OK:
                filepath = dlg.GetPath()
                
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "가계부"
                
                headers = ["거래번호", "날짜", "구분", "상세내역", "수입", "지출", "비고"]
                ws.append(headers)
                
                header_fill = PatternFill(start_color="007AFF", end_color="007AFF", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF")
                
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")
                
                rows = HL_CRUD.selectAll()
                for row in rows:
                    ws.append(list(row))
                
                ws.column_dimensions['A'].width = 12
                ws.column_dimensions['B'].width = 12
                ws.column_dimensions['C'].width = 10
                ws.column_dimensions['D'].width = 20
                ws.column_dimensions['E'].width = 15
                ws.column_dimensions['F'].width = 15
                ws.column_dimensions['G'].width = 30
                
                wb.save(filepath)
                
                wx.MessageBox("Excel 파일로 저장되었습니다.", "내보내기 완료", wx.OK | wx.ICON_INFORMATION)
            
            dlg.Destroy()
            
        except ImportError:
            wx.MessageBox("openpyxl 모듈이 필요합니다.\npip install openpyxl", "모듈 오류", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"내보내기 실패: {str(e)}", "오류", wx.OK | wx.ICON_ERROR)
    
    def OnImport(self, event):
        dlg = wx.FileDialog(
            self, "CSV 파일 선택",
            wildcard="CSV files (*.csv)|*.csv",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            
            try:
                count = 0
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)
                    
                    for row in reader:
                        if len(row) >= 6:
                            HL_CRUD.insert((row[1], row[2], row[3], row[4], row[5], row[6]))
                            count += 1
                
                wx.MessageBox(f"{count}건의 데이터를 가져왔습니다.", "가져오기 완료", wx.OK | wx.ICON_INFORMATION)
                self.OnSelectAll(None)
                
            except Exception as e:
                wx.MessageBox(f"가져오기 실패: {str(e)}", "오류", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def OnExit(self, event):
        self.Close()
    
    def OnSearch(self, event):
        dlg = SearchDialog(self)
        
        if dlg.ShowModal() == wx.ID_OK:
            criteria = dlg.GetSearchCriteria()
            
            self.list.DeleteAllItems()
            rows = HL_CRUD.selectAll()
            
            count = 0
            for row in rows:
                if row[1] < criteria['start_date'] or row[1] > criteria['end_date']:
                    continue
                
                if row[2] == '수입' and not criteria['include_income']:
                    continue
                if row[2] == '지출' and not criteria['include_expense']:
                    continue
                
                amount = float(row[4]) if row[4] else float(row[5]) if row[5] else 0
                
                if criteria['min_amount']:
                    try:
                        if amount < float(criteria['min_amount'].replace(',', '')):
                            continue
                    except ValueError:
                        pass
                
                if criteria['max_amount']:
                    try:
                        if amount > float(criteria['max_amount'].replace(',', '')):
                            continue
                    except ValueError:
                        pass
                
                if criteria['keyword'] and criteria['keyword'] not in row[6]:
                    continue
                
                idx = self.list.InsertItem(self.list.GetItemCount(), str(row[0]))
                self.list.SetItem(idx, 1, row[1])
                self.list.SetItem(idx, 2, row[2])
                self.list.SetItem(idx, 3, row[3])
                self.list.SetItem(idx, 4, f"{float(row[4]):,.0f}" if row[4] else "0")
                self.list.SetItem(idx, 5, f"{float(row[5]):,.0f}" if row[5] else "0")
                self.list.SetItem(idx, 6, row[6])
                count += 1
            
            wx.MessageBox(f"검색 완료 - {count}건 발견", "검색 결과", wx.OK | wx.ICON_INFORMATION)
        
        dlg.Destroy()
    
    def OnStatistics(self, event):
        rows = HL_CRUD.selectAll()
        dlg = StatisticsDialog(self, rows)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnBudget(self, event):
        dlg = BudgetDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnFavorites(self, event):
        dlg = FavoritesDialog(self)
        
        if dlg.ShowModal() == wx.ID_OK:
            favorite = dlg.GetSelectedFavorite()
            if favorite:
                if favorite[0] == '수입':
                    self.notebook.SetSelection(0)
                    self.comboRevenue.SetValue(favorite[1])
                    self.txtRevenue.SetValue(favorite[2])
                else:
                    self.notebook.SetSelection(1)
                    self.comboExpense.SetValue(favorite[1])
                    self.txtExpense.SetValue(favorite[2])
                
                self.txtRemark.SetValue(favorite[3])
                wx.MessageBox("즐겨찾기 항목이 적용되었습니다.", "적용 완료", wx.OK | wx.ICON_INFORMATION)
        
        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(parent=None)
    frame.Show()
    app.MainLoop()
