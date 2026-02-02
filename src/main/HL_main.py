# -*- coding: utf-8 -*- 

###########################################################################
## Modern Smart Household Account Book
## 모던 스마트 가계부 v5.0 - UI Enhanced
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
## 색상 테마 설정
###########################################################################
class ColorTheme:
    # 다크 모드
    DARK_BG = wx.Colour(18, 18, 18)
    DARK_CARD_BG = wx.Colour(28, 28, 28)
    DARK_SURFACE = wx.Colour(38, 38, 38)
    DARK_TEXT = wx.Colour(255, 255, 255)
    DARK_TEXT_SECONDARY = wx.Colour(158, 158, 158)
    
    # 라이트 모드
    LIGHT_BG = wx.Colour(246, 248, 250)
    LIGHT_CARD_BG = wx.Colour(255, 255, 255)
    LIGHT_SURFACE = wx.Colour(248, 249, 250)
    LIGHT_TEXT = wx.Colour(33, 37, 41)
    LIGHT_TEXT_SECONDARY = wx.Colour(108, 117, 125)
    
    # 액센트 컬러
    PRIMARY = wx.Colour(79, 70, 229)  # Indigo
    PRIMARY_HOVER = wx.Colour(67, 56, 202)
    SUCCESS = wx.Colour(16, 185, 129)  # Green
    DANGER = wx.Colour(239, 68, 68)  # Red
    WARNING = wx.Colour(245, 158, 11)  # Amber
    INFO = wx.Colour(59, 130, 246)  # Blue
    
    # 수입/지출 색상
    INCOME_COLOR = wx.Colour(16, 185, 129)
    EXPENSE_COLOR = wx.Colour(239, 68, 68)


###########################################################################
## 커스텀 버튼 (모던 스타일)
###########################################################################
class ModernButton(wx.Button):
    def __init__(self, parent, label="", size=wx.DefaultSize, primary=False):
        super().__init__(parent, label=label, size=size)
        
        self.primary = primary
        self.is_dark_mode = True
        
        # 기본 스타일 설정
        self.SetupStyle()
        
        # 호버 효과
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
    
    def SetupStyle(self):
        font = self.GetFont()
        font.SetPointSize(10)
        font.SetWeight(wx.FONTWEIGHT_MEDIUM)
        self.SetFont(font)
        
        if self.primary:
            self.SetBackgroundColour(ColorTheme.PRIMARY)
            self.SetForegroundColour(wx.WHITE)
        else:
            if self.is_dark_mode:
                self.SetBackgroundColour(ColorTheme.DARK_SURFACE)
                self.SetForegroundColour(ColorTheme.DARK_TEXT)
            else:
                self.SetBackgroundColour(ColorTheme.LIGHT_SURFACE)
                self.SetForegroundColour(ColorTheme.LIGHT_TEXT)
    
    def OnEnter(self, event):
        if self.primary:
            self.SetBackgroundColour(ColorTheme.PRIMARY_HOVER)
        else:
            if self.is_dark_mode:
                self.SetBackgroundColour(ColorTheme.DARK_CARD_BG)
            else:
                self.SetBackgroundColour(wx.Colour(243, 244, 246))
        self.Refresh()
    
    def OnLeave(self, event):
        self.SetupStyle()
        self.Refresh()


###########################################################################
## 카드 패널
###########################################################################
class CardPanel(wx.Panel):
    def __init__(self, parent, title="", is_dark_mode=True):
        super().__init__(parent)
        
        self.is_dark_mode = is_dark_mode
        
        if is_dark_mode:
            self.SetBackgroundColour(ColorTheme.DARK_CARD_BG)
        else:
            self.SetBackgroundColour(ColorTheme.LIGHT_CARD_BG)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        if title:
            title_text = wx.StaticText(self, label=title)
            font = title_text.GetFont()
            font.SetPointSize(14)
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            title_text.SetFont(font)
            
            if is_dark_mode:
                title_text.SetForegroundColour(ColorTheme.DARK_TEXT)
            else:
                title_text.SetForegroundColour(ColorTheme.LIGHT_TEXT)
            
            self.main_sizer.Add(title_text, 0, wx.ALL, 15)
            
            # 구분선
            line = wx.StaticLine(self)
            if is_dark_mode:
                line.SetBackgroundColour(ColorTheme.DARK_SURFACE)
            else:
                line.SetBackgroundColour(wx.Colour(229, 231, 235))
            self.main_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        
        self.SetSizer(self.main_sizer)


###########################################################################
## 즐겨찾기 관리 다이얼로그 (개선된 UI)
###########################################################################
class FavoritesDialog(wx.Dialog):
    def __init__(self, parent, is_dark_mode=True):
        super().__init__(parent, title="⭐ 즐겨찾기 관리", size=(600, 500))
        
        self.is_dark_mode = is_dark_mode
        
        if is_dark_mode:
            self.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            self.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        panel = wx.Panel(self)
        if is_dark_mode:
            panel.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            panel.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = wx.StaticText(panel, label="즐겨찾기 목록")
        font = header.GetFont()
        font.SetPointSize(16)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        header.SetFont(font)
        if is_dark_mode:
            header.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            header.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        sizer.Add(header, 0, wx.ALL, 20)
        
        # 즐겨찾기 목록
        self.favoritesList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.favoritesList.InsertColumn(0, "구분", width=100)
        self.favoritesList.InsertColumn(1, "항목", width=180)
        self.favoritesList.InsertColumn(2, "금액", width=120)
        self.favoritesList.InsertColumn(3, "비고", width=170)
        
        # 리스트 스타일
        if is_dark_mode:
            self.favoritesList.SetBackgroundColour(ColorTheme.DARK_CARD_BG)
            self.favoritesList.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            self.favoritesList.SetBackgroundColour(ColorTheme.LIGHT_CARD_BG)
            self.favoritesList.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        
        sizer.Add(self.favoritesList, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnAdd = ModernButton(panel, label="➕ 추가", primary=True)
        btnDelete = ModernButton(panel, label="🗑️ 삭제")
        btnClose = ModernButton(panel, label="✕ 닫기")
        
        btnSizer.Add(btnAdd, 0, wx.ALL, 5)
        btnSizer.Add(btnDelete, 0, wx.ALL, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(btnClose, 0, wx.ALL, 5)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        panel.SetSizer(sizer)
        
        # 이벤트 바인딩
        btnAdd.Bind(wx.EVT_BUTTON, self.OnAdd)
        btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        btnClose.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        self.LoadFavorites()
    
    def LoadFavorites(self):
        self.favorites = []
        try:
            with open('favorites.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                self.favorites = list(reader)
        except FileNotFoundError:
            pass
        
        self.favoritesList.DeleteAllItems()
        for fav in self.favorites:
            if len(fav) >= 4:
                idx = self.favoritesList.InsertItem(self.favoritesList.GetItemCount(), fav[0])
                self.favoritesList.SetItem(idx, 1, fav[1])
                self.favoritesList.SetItem(idx, 2, fav[2])
                self.favoritesList.SetItem(idx, 3, fav[3])
    
    def OnAdd(self, event):
        dlg = wx.TextEntryDialog(self, "즐겨찾기 이름:", "즐겨찾기 추가")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            self.favorites.append(['수입', '수입.급여', '0', name])
            self.SaveFavorites()
            self.LoadFavorites()
        dlg.Destroy()
    
    def OnDelete(self, event):
        idx = self.favoritesList.GetFirstSelected()
        if idx >= 0:
            del self.favorites[idx]
            self.SaveFavorites()
            self.LoadFavorites()
    
    def SaveFavorites(self):
        with open('favorites.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.favorites)
    
    def GetSelectedFavorite(self):
        idx = self.favoritesList.GetFirstSelected()
        if idx >= 0 and idx < len(self.favorites):
            return self.favorites[idx]
        return None


###########################################################################
## 검색 다이얼로그 (개선된 UI)
###########################################################################
class SearchDialog(wx.Dialog):
    def __init__(self, parent, is_dark_mode=True):
        super().__init__(parent, title="🔍 고급 검색", size=(600, 550))
        
        self.is_dark_mode = is_dark_mode
        
        if is_dark_mode:
            self.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            self.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        panel = wx.Panel(self)
        if is_dark_mode:
            panel.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            panel.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = wx.StaticText(panel, label="상세 검색 조건")
        font = header.GetFont()
        font.SetPointSize(16)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        header.SetFont(font)
        if is_dark_mode:
            header.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            header.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        sizer.Add(header, 0, wx.ALL, 20)
        
        # 날짜 범위 카드
        dateCard = CardPanel(panel, "📅 날짜 범위", is_dark_mode)
        dateSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        dateSizer.Add(wx.StaticText(dateCard, label="시작일:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.startDate = wx.adv.DatePickerCtrl(dateCard, style=wx.adv.DP_DROPDOWN)
        dateSizer.Add(self.startDate, 1, wx.ALL, 5)
        
        dateSizer.Add(wx.StaticText(dateCard, label="종료일:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.endDate = wx.adv.DatePickerCtrl(dateCard, style=wx.adv.DP_DROPDOWN)
        dateSizer.Add(self.endDate, 1, wx.ALL, 5)
        
        dateCard.main_sizer.Add(dateSizer, 0, wx.EXPAND | wx.ALL, 15)
        sizer.Add(dateCard, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 구분 카드
        sectionCard = CardPanel(panel, "📊 구분", is_dark_mode)
        sectionSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.chkIncome = wx.CheckBox(sectionCard, label="💰 수입")
        self.chkExpense = wx.CheckBox(sectionCard, label="💸 지출")
        self.chkIncome.SetValue(True)
        self.chkExpense.SetValue(True)
        sectionSizer.Add(self.chkIncome, 0, wx.ALL, 5)
        sectionSizer.Add(self.chkExpense, 0, wx.ALL, 5)
        sectionCard.main_sizer.Add(sectionSizer, 0, wx.ALL, 15)
        sizer.Add(sectionCard, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 금액 범위 카드
        amountCard = CardPanel(panel, "💵 금액 범위", is_dark_mode)
        amountSizer = wx.BoxSizer(wx.HORIZONTAL)
        amountSizer.Add(wx.StaticText(amountCard, label="최소:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.minAmount = wx.TextCtrl(amountCard)
        amountSizer.Add(self.minAmount, 1, wx.ALL, 5)
        
        amountSizer.Add(wx.StaticText(amountCard, label="최대:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.maxAmount = wx.TextCtrl(amountCard)
        amountSizer.Add(self.maxAmount, 1, wx.ALL, 5)
        amountCard.main_sizer.Add(amountSizer, 0, wx.EXPAND | wx.ALL, 15)
        sizer.Add(amountCard, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 키워드 카드
        keywordCard = CardPanel(panel, "🔎 키워드 검색", is_dark_mode)
        self.keyword = wx.TextCtrl(keywordCard)
        self.keyword.SetHint("비고에서 검색할 키워드를 입력하세요")
        keywordCard.main_sizer.Add(self.keyword, 0, wx.EXPAND | wx.ALL, 15)
        sizer.Add(keywordCard, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSearch = ModernButton(panel, label="🔍 검색", primary=True)
        btnCancel = ModernButton(panel, label="✕ 취소")
        btnSizer.AddStretchSpacer()
        btnSizer.Add(btnSearch, 0, wx.ALL, 5)
        btnSizer.Add(btnCancel, 0, wx.ALL, 5)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        panel.SetSizer(sizer)
        
        btnSearch.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        btnCancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
    
    def GetSearchCriteria(self):
        return {
            'start_date': self.startDate.GetValue().FormatISODate(),
            'end_date': self.endDate.GetValue().FormatISODate(),
            'include_income': self.chkIncome.GetValue(),
            'include_expense': self.chkExpense.GetValue(),
            'min_amount': self.minAmount.GetValue(),
            'max_amount': self.maxAmount.GetValue(),
            'keyword': self.keyword.GetValue()
        }


###########################################################################
## 예산 설정 다이얼로그 (개선된 UI)
###########################################################################
class BudgetDialog(wx.Dialog):
    def __init__(self, parent, is_dark_mode=True):
        super().__init__(parent, title="💰 예산 관리", size=(700, 600))
        
        self.is_dark_mode = is_dark_mode
        
        if is_dark_mode:
            self.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            self.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        panel = wx.Panel(self)
        if is_dark_mode:
            panel.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            panel.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = wx.StaticText(panel, label="월별 예산 설정")
        font = header.GetFont()
        font.SetPointSize(16)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        header.SetFont(font)
        if is_dark_mode:
            header.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            header.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        sizer.Add(header, 0, wx.ALL, 20)
        
        # 월 선택 카드
        monthCard = CardPanel(panel, "📅 월 선택", is_dark_mode)
        monthSizer = wx.BoxSizer(wx.HORIZONTAL)
        monthSizer.Add(wx.StaticText(monthCard, label="대상 월:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.comboMonth = wx.ComboBox(monthCard, choices=HL_CRUD.selectMonthList(), style=wx.CB_READONLY)
        if self.comboMonth.GetCount() > 0:
            self.comboMonth.SetSelection(0)
        monthSizer.Add(self.comboMonth, 1, wx.ALL, 5)
        monthCard.main_sizer.Add(monthSizer, 0, wx.EXPAND | wx.ALL, 15)
        sizer.Add(monthCard, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 예산 입력 카드
        budgetCard = CardPanel(panel, "💵 예산 금액", is_dark_mode)
        budgetSizer = wx.BoxSizer(wx.HORIZONTAL)
        budgetSizer.Add(wx.StaticText(budgetCard, label="총 예산:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.txtBudget = wx.TextCtrl(budgetCard, size=(200, -1))
        self.txtBudget.SetHint("예산 금액을 입력하세요")
        budgetSizer.Add(self.txtBudget, 1, wx.ALL, 5)
        budgetSizer.Add(wx.StaticText(budgetCard, label="원"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        budgetCard.main_sizer.Add(budgetSizer, 0, wx.EXPAND | wx.ALL, 15)
        sizer.Add(budgetCard, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 예산 현황 카드
        statusCard = CardPanel(panel, "📊 예산 현황", is_dark_mode)
        self.lblStatus = wx.StaticText(statusCard, label="월을 선택하고 조회 버튼을 클릭하세요")
        font = self.lblStatus.GetFont()
        font.SetPointSize(11)
        self.lblStatus.SetFont(font)
        if is_dark_mode:
            self.lblStatus.SetForegroundColour(ColorTheme.DARK_TEXT_SECONDARY)
        else:
            self.lblStatus.SetForegroundColour(ColorTheme.LIGHT_TEXT_SECONDARY)
        statusCard.main_sizer.Add(self.lblStatus, 0, wx.ALL, 15)
        sizer.Add(statusCard, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSave = ModernButton(panel, label="💾 저장", primary=True)
        btnLoad = ModernButton(panel, label="🔄 조회")
        btnClose = ModernButton(panel, label="✕ 닫기")
        
        btnSizer.Add(btnSave, 0, wx.ALL, 5)
        btnSizer.Add(btnLoad, 0, wx.ALL, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(btnClose, 0, wx.ALL, 5)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        panel.SetSizer(sizer)
        
        btnSave.Bind(wx.EVT_BUTTON, self.OnSave)
        btnLoad.Bind(wx.EVT_BUTTON, self.OnLoad)
        btnClose.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        self.budgets = {}
        self.LoadBudgets()
    
    def LoadBudgets(self):
        try:
            with open('budgets.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        self.budgets[row[0]] = row[1]
        except FileNotFoundError:
            pass
    
    def OnSave(self, event):
        month = self.comboMonth.GetValue()
        budget = self.txtBudget.GetValue().replace(',', '')
        
        if month and budget:
            try:
                float(budget)
                self.budgets[month] = budget
                
                with open('budgets.csv', 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    for m, b in self.budgets.items():
                        writer.writerow([m, b])
                
                wx.MessageBox("예산이 저장되었습니다.", "저장 완료", wx.OK | wx.ICON_INFORMATION)
                self.OnLoad(None)
            except ValueError:
                wx.MessageBox("올바른 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_ERROR)
    
    def OnLoad(self, event):
        month = self.comboMonth.GetValue()
        if month:
            # 예산 로드
            budget = float(self.budgets.get(month, 0))
            self.txtBudget.SetValue(f"{budget:,.0f}" if budget > 0 else "")
            
            # 실제 지출 계산
            rows = HL_CRUD.selectMonthlySum(month)
            total_expense = 0
            for row in rows:
                if row[2] == '지출' or row[2] == '합계':
                    try:
                        total_expense += float(row[5]) if row[5] else 0
                    except (ValueError, TypeError):
                        pass
            
            if budget > 0:
                remaining = budget - total_expense
                percent = (total_expense / budget * 100) if budget > 0 else 0
                
                status_text = f"예산: {budget:,.0f}원\n"
                status_text += f"지출: {total_expense:,.0f}원\n"
                status_text += f"잔액: {remaining:,.0f}원\n"
                status_text += f"사용률: {percent:.1f}%"
                
                self.lblStatus.SetLabel(status_text)
                
                if percent > 100:
                    self.lblStatus.SetForegroundColour(ColorTheme.DANGER)
                elif percent > 80:
                    self.lblStatus.SetForegroundColour(ColorTheme.WARNING)
                else:
                    self.lblStatus.SetForegroundColour(ColorTheme.SUCCESS)
            else:
                self.lblStatus.SetLabel("예산이 설정되지 않았습니다.")
                if self.is_dark_mode:
                    self.lblStatus.SetForegroundColour(ColorTheme.DARK_TEXT_SECONDARY)
                else:
                    self.lblStatus.SetForegroundColour(ColorTheme.LIGHT_TEXT_SECONDARY)


###########################################################################
## 통계 다이얼로그 (개선된 UI)
###########################################################################
class StatisticsDialog(wx.Dialog):
    def __init__(self, parent, data, is_dark_mode=True):
        super().__init__(parent, title="📊 통계 분석", size=(800, 600))
        
        self.is_dark_mode = is_dark_mode
        self.data = data
        
        if is_dark_mode:
            self.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            self.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        panel = wx.Panel(self)
        if is_dark_mode:
            panel.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            panel.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 헤더
        header = wx.StaticText(panel, label="상세 통계")
        font = header.GetFont()
        font.SetPointSize(18)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        header.SetFont(font)
        if is_dark_mode:
            header.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            header.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        sizer.Add(header, 0, wx.ALL, 20)
        
        # 통계 계산
        total_income = 0
        total_expense = 0
        expense_by_category = defaultdict(float)
        
        for row in data:
            try:
                if row[2] == '수입':
                    total_income += float(row[4]) if row[4] else 0
                elif row[2] == '지출':
                    amount = float(row[5]) if row[5] else 0
                    total_expense += amount
                    category = row[3].split('.')[0] if '.' in row[3] else row[3]
                    expense_by_category[category] += amount
            except (ValueError, TypeError, IndexError):
                continue
        
        # 요약 카드
        summaryCard = CardPanel(panel, "💰 전체 요약", is_dark_mode)
        summaryText = f"총 수입: {total_income:,.0f}원\n"
        summaryText += f"총 지출: {total_expense:,.0f}원\n"
        summaryText += f"순자산: {(total_income - total_expense):,.0f}원"
        
        lblSummary = wx.StaticText(summaryCard, label=summaryText)
        font = lblSummary.GetFont()
        font.SetPointSize(12)
        lblSummary.SetFont(font)
        if is_dark_mode:
            lblSummary.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            lblSummary.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        summaryCard.main_sizer.Add(lblSummary, 0, wx.ALL, 15)
        sizer.Add(summaryCard, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 카테고리별 지출 카드
        categoryCard = CardPanel(panel, "📊 카테고리별 지출", is_dark_mode)
        
        categoryList = wx.ListCtrl(categoryCard, style=wx.LC_REPORT)
        categoryList.InsertColumn(0, "카테고리", width=200)
        categoryList.InsertColumn(1, "금액", width=150)
        categoryList.InsertColumn(2, "비율", width=100)
        
        if is_dark_mode:
            categoryList.SetBackgroundColour(ColorTheme.DARK_SURFACE)
            categoryList.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            categoryList.SetBackgroundColour(ColorTheme.LIGHT_SURFACE)
            categoryList.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        
        for category, amount in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True):
            percent = (amount / total_expense * 100) if total_expense > 0 else 0
            idx = categoryList.InsertItem(categoryList.GetItemCount(), category)
            categoryList.SetItem(idx, 1, f"{amount:,.0f}원")
            categoryList.SetItem(idx, 2, f"{percent:.1f}%")
        
        categoryCard.main_sizer.Add(categoryList, 1, wx.EXPAND | wx.ALL, 15)
        sizer.Add(categoryCard, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # 닫기 버튼
        btnClose = ModernButton(panel, label="✕ 닫기", primary=True)
        btnClose.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        sizer.Add(btnClose, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        
        panel.SetSizer(sizer)


###########################################################################
## 메인 프레임 (개선된 UI)
###########################################################################
class MyFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="💰 모던 스마트 가계부 v5.0", size=(1400, 900))
        
        self.is_dark_mode = True
        
        # 메뉴바 생성
        self.CreateMenuBar()
        
        # 메인 패널
        self.panel = wx.Panel(self)
        if self.is_dark_mode:
            self.panel.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            self.panel.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 상단 헤더
        self.CreateHeader(mainSizer)
        
        # 컨텐츠 영역 (좌우 분할)
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 좌측: 입력 영역
        leftPanel = self.CreateLeftPanel()
        contentSizer.Add(leftPanel, 1, wx.EXPAND | wx.ALL, 10)
        
        # 우측: 리스트 및 그래프
        rightPanel = self.CreateRightPanel()
        contentSizer.Add(rightPanel, 2, wx.EXPAND | wx.ALL, 10)
        
        mainSizer.Add(contentSizer, 1, wx.EXPAND)
        
        self.panel.SetSizer(mainSizer)
        
        # 초기 데이터 로드
        self.OnSelectAll(None)
        
        self.Centre()
    
    def CreateMenuBar(self):
        menubar = wx.MenuBar()
        
        # 파일 메뉴
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_ANY, "📤 Excel로 내보내기\tCtrl+E", "데이터를 Excel 파일로 내보내기")
        fileMenu.Append(wx.ID_ANY, "📥 CSV에서 가져오기\tCtrl+I", "CSV 파일에서 데이터 가져오기")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, "❌ 종료\tCtrl+Q", "프로그램 종료")
        
        # 도구 메뉴
        toolsMenu = wx.Menu()
        toolsMenu.Append(wx.ID_ANY, "🔍 고급 검색\tCtrl+F", "상세 검색 조건으로 검색")
        toolsMenu.Append(wx.ID_ANY, "📊 통계 보기\tCtrl+T", "통계 분석 보기")
        toolsMenu.Append(wx.ID_ANY, "💰 예산 관리\tCtrl+B", "월별 예산 설정 및 관리")
        toolsMenu.Append(wx.ID_ANY, "⭐ 즐겨찾기\tCtrl+D", "즐겨찾기 관리")
        toolsMenu.AppendSeparator()
        self.darkModeItem = toolsMenu.AppendCheckItem(wx.ID_ANY, "🌙 다크 모드", "다크 모드 전환")
        self.darkModeItem.Check(self.is_dark_mode)
        
        menubar.Append(fileMenu, "📁 파일")
        menubar.Append(toolsMenu, "🛠️ 도구")
        
        self.SetMenuBar(menubar)
        
        # 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.OnExport, id=fileMenu.FindItemByPosition(0).GetId())
        self.Bind(wx.EVT_MENU, self.OnImport, id=fileMenu.FindItemByPosition(1).GetId())
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        
        self.Bind(wx.EVT_MENU, self.OnSearch, id=toolsMenu.FindItemByPosition(0).GetId())
        self.Bind(wx.EVT_MENU, self.OnStatistics, id=toolsMenu.FindItemByPosition(1).GetId())
        self.Bind(wx.EVT_MENU, self.OnBudget, id=toolsMenu.FindItemByPosition(2).GetId())
        self.Bind(wx.EVT_MENU, self.OnFavorites, id=toolsMenu.FindItemByPosition(3).GetId())
        self.Bind(wx.EVT_MENU, self.OnToggleDarkMode, id=self.darkModeItem.GetId())
    
    def CreateHeader(self, sizer):
        headerPanel = wx.Panel(self.panel)
        if self.is_dark_mode:
            headerPanel.SetBackgroundColour(ColorTheme.DARK_CARD_BG)
        else:
            headerPanel.SetBackgroundColour(ColorTheme.LIGHT_CARD_BG)
        
        headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 타이틀
        title = wx.StaticText(headerPanel, label="💰 스마트 가계부")
        font = title.GetFont()
        font.SetPointSize(20)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        if self.is_dark_mode:
            title.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            title.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        
        headerSizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        headerSizer.AddStretchSpacer()
        
        # 월 선택
        monthLabel = wx.StaticText(headerPanel, label="월 선택:")
        if self.is_dark_mode:
            monthLabel.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            monthLabel.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        headerSizer.Add(monthLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        self.comboMonth = wx.ComboBox(headerPanel, choices=HL_CRUD.selectMonthList(), 
                                      style=wx.CB_READONLY, size=(150, -1))
        if self.comboMonth.GetCount() > 0:
            self.comboMonth.SetSelection(0)
        headerSizer.Add(self.comboMonth, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        btnMonthSearch = ModernButton(headerPanel, label="🔍 조회", primary=True)
        btnMonthSearch.Bind(wx.EVT_BUTTON, self.OnMonthSelect)
        headerSizer.Add(btnMonthSearch, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        headerPanel.SetSizer(headerSizer)
        sizer.Add(headerPanel, 0, wx.EXPAND | wx.ALL, 10)
    
    def CreateLeftPanel(self):
        leftPanel = wx.Panel(self.panel)
        if self.is_dark_mode:
            leftPanel.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            leftPanel.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 입력 카드
        inputCard = CardPanel(leftPanel, "➕ 새 거래 입력", self.is_dark_mode)
        
        # 노트북 (탭)
        self.notebook = wx.Notebook(inputCard)
        
        # 수입 탭
        pageRevenue = self.CreateRevenuePage(self.notebook)
        self.notebook.AddPage(pageRevenue, "💰 수입")
        
        # 지출 탭
        pageExpense = self.CreateExpensePage(self.notebook)
        self.notebook.AddPage(pageExpense, "💸 지출")
        
        inputCard.main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        # 공통 입력 필드
        commonSizer = wx.GridBagSizer(10, 10)
        
        # 날짜
        commonSizer.Add(wx.StaticText(inputCard, label="📅 날짜:"), 
                       pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.dateCtrl = wx.adv.DatePickerCtrl(inputCard, style=wx.adv.DP_DROPDOWN)
        commonSizer.Add(self.dateCtrl, pos=(0, 1), flag=wx.EXPAND)
        
        # 비고
        commonSizer.Add(wx.StaticText(inputCard, label="📝 비고:"), 
                       pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.txtRemark = wx.TextCtrl(inputCard)
        self.txtRemark.SetHint("상세 내용을 입력하세요")
        commonSizer.Add(self.txtRemark, pos=(1, 1), flag=wx.EXPAND)
        
        commonSizer.AddGrowableCol(1)
        inputCard.main_sizer.Add(commonSizer, 0, wx.EXPAND | wx.ALL, 15)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnInsert = ModernButton(inputCard, label="✅ 추가", primary=True)
        btnUpdate = ModernButton(inputCard, label="✏️ 수정")
        btnDelete = ModernButton(inputCard, label="🗑️ 삭제")
        
        btnInsert.Bind(wx.EVT_BUTTON, self.OnInsert)
        btnUpdate.Bind(wx.EVT_BUTTON, self.OnUpdate)
        btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        
        btnSizer.Add(btnInsert, 1, wx.ALL, 5)
        btnSizer.Add(btnUpdate, 1, wx.ALL, 5)
        btnSizer.Add(btnDelete, 1, wx.ALL, 5)
        
        inputCard.main_sizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 15)
        
        sizer.Add(inputCard, 1, wx.EXPAND)
        
        leftPanel.SetSizer(sizer)
        return leftPanel
    
    def CreateRevenuePage(self, parent):
        page = wx.Panel(parent)
        if self.is_dark_mode:
            page.SetBackgroundColour(ColorTheme.DARK_CARD_BG)
        else:
            page.SetBackgroundColour(ColorTheme.LIGHT_CARD_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        grid = wx.GridBagSizer(10, 10)
        
        grid.Add(wx.StaticText(page, label="항목:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.comboRevenue = wx.ComboBox(page, choices=[
            '수입.급여', '수입.보너스', '수입.이자', '수입.배당',
            '수입.기타', '수입.용돈', '수입.부업'
        ])
        grid.Add(self.comboRevenue, pos=(0, 1), flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(page, label="금액:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.txtRevenue = wx.TextCtrl(page)
        self.txtRevenue.SetHint("수입 금액")
        grid.Add(self.txtRevenue, pos=(1, 1), flag=wx.EXPAND)
        
        grid.AddGrowableCol(1)
        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 15)
        
        page.SetSizer(sizer)
        return page
    
    def CreateExpensePage(self, parent):
        page = wx.Panel(parent)
        if self.is_dark_mode:
            page.SetBackgroundColour(ColorTheme.DARK_CARD_BG)
        else:
            page.SetBackgroundColour(ColorTheme.LIGHT_CARD_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        grid = wx.GridBagSizer(10, 10)
        
        grid.Add(wx.StaticText(page, label="항목:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.comboExpense = wx.ComboBox(page, choices=[
            '지출.식비', '지출.교통', '지출.통신', '지출.주거',
            '지출.의류', '지출.의료', '지출.교육', '지출.문화',
            '지출.경조사', '지출.기타'
        ])
        grid.Add(self.comboExpense, pos=(0, 1), flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(page, label="금액:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.txtExpense = wx.TextCtrl(page)
        self.txtExpense.SetHint("지출 금액")
        grid.Add(self.txtExpense, pos=(1, 1), flag=wx.EXPAND)
        
        grid.AddGrowableCol(1)
        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 15)
        
        page.SetSizer(sizer)
        return page
    
    def CreateRightPanel(self):
        rightPanel = wx.Panel(self.panel)
        if self.is_dark_mode:
            rightPanel.SetBackgroundColour(ColorTheme.DARK_BG)
        else:
            rightPanel.SetBackgroundColour(ColorTheme.LIGHT_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 거래 내역 카드
        listCard = CardPanel(rightPanel, "📋 거래 내역", self.is_dark_mode)
        
        # 리스트 컨트롤
        self.list = wx.ListCtrl(listCard, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.InsertColumn(0, "번호", width=60)
        self.list.InsertColumn(1, "날짜", width=100)
        self.list.InsertColumn(2, "구분", width=80)
        self.list.InsertColumn(3, "항목", width=150)
        self.list.InsertColumn(4, "수입", width=120)
        self.list.InsertColumn(5, "지출", width=120)
        self.list.InsertColumn(6, "비고", width=200)
        
        if self.is_dark_mode:
            self.list.SetBackgroundColour(ColorTheme.DARK_SURFACE)
            self.list.SetForegroundColour(ColorTheme.DARK_TEXT)
        else:
            self.list.SetBackgroundColour(ColorTheme.LIGHT_SURFACE)
            self.list.SetForegroundColour(ColorTheme.LIGHT_TEXT)
        
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        
        listCard.main_sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 10)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnAll = ModernButton(listCard, label="📋 전체 조회")
        btnGraph = ModernButton(listCard, label="📊 그래프 생성", primary=True)
        
        btnAll.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        btnGraph.Bind(wx.EVT_BUTTON, self.OnMakeGraph)
        
        btnSizer.Add(btnAll, 0, wx.ALL, 5)
        btnSizer.Add(btnGraph, 0, wx.ALL, 5)
        btnSizer.AddStretchSpacer()
        
        listCard.main_sizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        sizer.Add(listCard, 2, wx.EXPAND | wx.BOTTOM, 10)
        
        # 그래프 카드
        graphCard = CardPanel(rightPanel, "📊 지출 분석 그래프", self.is_dark_mode)
        
        self.graphPanel = Barchart(graphCard)
        if self.is_dark_mode:
            self.graphPanel.SetBackgroundColour(ColorTheme.DARK_SURFACE)
        else:
            self.graphPanel.SetBackgroundColour(ColorTheme.LIGHT_SURFACE)
        
        graphCard.main_sizer.Add(self.graphPanel, 1, wx.EXPAND | wx.ALL, 10)
        
        sizer.Add(graphCard, 1, wx.EXPAND)
        
        rightPanel.SetSizer(sizer)
        return rightPanel
    
    def OnToggleDarkMode(self, event):
        self.is_dark_mode = self.darkModeItem.IsChecked()
        wx.MessageBox(
            "다크 모드 설정이 변경되었습니다.\n프로그램을 재시작하면 적용됩니다.",
            "다크 모드",
            wx.OK | wx.ICON_INFORMATION
        )
    
    # 이하 기존 메서드들과 동일한 로직 유지
    def OnInsert(self, event):
        date = self.dateCtrl.GetValue().FormatISODate()
        remark = self.txtRemark.GetValue()
        
        if self.notebook.GetSelection() == 0:  # 수입
            section = '수입'
            title = self.comboRevenue.GetValue()
            revenue = self.txtRevenue.GetValue().replace(',', '')
            expense = '0'
            
            if not title or not revenue:
                wx.MessageBox("항목과 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return
        else:  # 지출
            section = '지출'
            title = self.comboExpense.GetValue()
            revenue = '0'
            expense = self.txtExpense.GetValue().replace(',', '')
            
            if not title or not expense:
                wx.MessageBox("항목과 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return
        
        try:
            HL_CRUD.insert((date, section, title, revenue, expense, remark))
            wx.MessageBox("저장되었습니다.", "저장 완료", wx.OK | wx.ICON_INFORMATION)
            self.ClearInputs()
            self.OnSelectAll(None)
        except Exception as e:
            wx.MessageBox(f"저장 실패: {str(e)}", "오류", wx.OK | wx.ICON_ERROR)
    
    def OnUpdate(self, event):
        idx = self.list.GetFirstSelected()
        if idx < 0:
            wx.MessageBox("수정할 항목을 선택하세요.", "선택 오류", wx.OK | wx.ICON_WARNING)
            return
        
        key = self.list.GetItemText(idx, 0)
        date = self.dateCtrl.GetValue().FormatISODate()
        remark = self.txtRemark.GetValue()
        
        if self.notebook.GetSelection() == 0:
            section = '수입'
            title = self.comboRevenue.GetValue()
            revenue = self.txtRevenue.GetValue().replace(',', '')
            expense = '0'
        else:
            section = '지출'
            title = self.comboExpense.GetValue()
            revenue = '0'
            expense = self.txtExpense.GetValue().replace(',', '')
        
        try:
            HL_CRUD.update((key, date, section, title, revenue, expense, remark))
            wx.MessageBox("수정되었습니다.", "수정 완료", wx.OK | wx.ICON_INFORMATION)
            self.ClearInputs()
            self.OnSelectAll(None)
        except Exception as e:
            wx.MessageBox(f"수정 실패: {str(e)}", "오류", wx.OK | wx.ICON_ERROR)
    
    def OnDelete(self, event):
        idx = self.list.GetFirstSelected()
        if idx < 0:
            wx.MessageBox("삭제할 항목을 선택하세요.", "선택 오류", wx.OK | wx.ICON_WARNING)
            return
        
        key = self.list.GetItemText(idx, 0)
        
        dlg = wx.MessageDialog(self, "정말 삭제하시겠습니까?", "삭제 확인", 
                               wx.YES_NO | wx.ICON_QUESTION)
        
        if dlg.ShowModal() == wx.ID_YES:
            try:
                HL_CRUD.delete(key)
                wx.MessageBox("삭제되었습니다.", "삭제 완료", wx.OK | wx.ICON_INFORMATION)
                self.ClearInputs()
                self.OnSelectAll(None)
            except Exception as e:
                wx.MessageBox(f"삭제 실패: {str(e)}", "오류", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
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
            
            if row[2] == '수입':
                self.list.SetItemTextColour(idx, ColorTheme.INCOME_COLOR)
            else:
                self.list.SetItemTextColour(idx, ColorTheme.EXPENSE_COLOR)
    
    def OnMonthSelect(self, event):
        month = self.comboMonth.GetValue()
        if month:
            self.list.DeleteAllItems()
            rows = HL_CRUD.selectMonthlySum(month)
            
            for row in rows:
                idx = self.list.InsertItem(self.list.GetItemCount(), str(row[0]))
                self.list.SetItem(idx, 1, row[1])
                self.list.SetItem(idx, 2, row[2])
                self.list.SetItem(idx, 3, row[3])
                self.list.SetItem(idx, 4, f"{float(row[4]):,.0f}" if row[4] else "0")
                self.list.SetItem(idx, 5, f"{float(row[5]):,.0f}" if row[5] else "0")
                self.list.SetItem(idx, 6, row[6])
                
                if row[2] == '수입':
                    self.list.SetItemTextColour(idx, ColorTheme.INCOME_COLOR)
                else:
                    self.list.SetItemTextColour(idx, ColorTheme.EXPENSE_COLOR)
    
    def OnListItemSelected(self, event):
        idx = event.GetIndex()
        
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
                
                header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
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
        dlg = SearchDialog(self, self.is_dark_mode)
        
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
        dlg = StatisticsDialog(self, rows, self.is_dark_mode)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnBudget(self, event):
        dlg = BudgetDialog(self, self.is_dark_mode)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnFavorites(self, event):
        dlg = FavoritesDialog(self, self.is_dark_mode)
        
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
