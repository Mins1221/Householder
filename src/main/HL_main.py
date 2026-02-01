# -*- coding: utf-8 -*- 

###########################################################################
## Enhanced Smart Household Account Book
## 개선된 스마트 가계부 v4.0
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
## 즐겨찾기 관리 다이얼로그
###########################################################################
class FavoritesDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="⭐ 즐겨찾기 관리", size=(500, 400))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 즐겨찾기 목록
        self.favoritesList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.favoritesList.InsertColumn(0, "구분", width=80)
        self.favoritesList.InsertColumn(1, "항목", width=150)
        self.favoritesList.InsertColumn(2, "금액", width=100)
        self.favoritesList.InsertColumn(3, "비고", width=150)
        
        sizer.Add(self.favoritesList, 1, wx.EXPAND | wx.ALL, 10)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnAdd = wx.Button(panel, label="추가")
        btnDelete = wx.Button(panel, label="삭제")
        btnClose = wx.Button(panel, wx.ID_CLOSE, label="닫기")
        
        btnSizer.Add(btnAdd, 0, wx.ALL, 5)
        btnSizer.Add(btnDelete, 0, wx.ALL, 5)
        btnSizer.AddStretchSpacer()
        btnSizer.Add(btnClose, 0, wx.ALL, 5)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        # 이벤트 바인딩
        btnAdd.Bind(wx.EVT_BUTTON, self.OnAdd)
        btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        btnClose.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        self.LoadFavorites()
    
    def LoadFavorites(self):
        # 즐겨찾기 데이터 로드
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
## 검색 다이얼로그
###########################################################################
class SearchDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="🔍 고급 검색", size=(500, 400))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 날짜 범위
        dateBox = wx.StaticBoxSizer(wx.VERTICAL, panel, "날짜 범위")
        dateSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        dateSizer.Add(wx.StaticText(panel, label="시작일:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.startDate = wx.adv.DatePickerCtrl(panel, style=wx.adv.DP_DROPDOWN)
        dateSizer.Add(self.startDate, 1, wx.ALL, 5)
        
        dateSizer.Add(wx.StaticText(panel, label="종료일:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.endDate = wx.adv.DatePickerCtrl(panel, style=wx.adv.DP_DROPDOWN)
        dateSizer.Add(self.endDate, 1, wx.ALL, 5)
        
        dateBox.Add(dateSizer, 0, wx.EXPAND)
        sizer.Add(dateBox, 0, wx.EXPAND | wx.ALL, 10)
        
        # 구분
        sectionBox = wx.StaticBoxSizer(wx.HORIZONTAL, panel, "구분")
        self.chkIncome = wx.CheckBox(panel, label="수입")
        self.chkExpense = wx.CheckBox(panel, label="지출")
        self.chkIncome.SetValue(True)
        self.chkExpense.SetValue(True)
        sectionBox.Add(self.chkIncome, 0, wx.ALL, 5)
        sectionBox.Add(self.chkExpense, 0, wx.ALL, 5)
        sizer.Add(sectionBox, 0, wx.EXPAND | wx.ALL, 10)
        
        # 금액 범위
        amountBox = wx.StaticBoxSizer(wx.HORIZONTAL, panel, "금액 범위")
        amountBox.Add(wx.StaticText(panel, label="최소:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.minAmount = wx.TextCtrl(panel)
        amountBox.Add(self.minAmount, 1, wx.ALL, 5)
        
        amountBox.Add(wx.StaticText(panel, label="최대:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.maxAmount = wx.TextCtrl(panel)
        amountBox.Add(self.maxAmount, 1, wx.ALL, 5)
        sizer.Add(amountBox, 0, wx.EXPAND | wx.ALL, 10)
        
        # 키워드
        keywordBox = wx.StaticBoxSizer(wx.VERTICAL, panel, "키워드 검색")
        self.keyword = wx.TextCtrl(panel)
        self.keyword.SetHint("비고에서 검색할 키워드")
        keywordBox.Add(self.keyword, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(keywordBox, 0, wx.EXPAND | wx.ALL, 10)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSearch = wx.Button(panel, wx.ID_OK, label="검색")
        btnCancel = wx.Button(panel, wx.ID_CANCEL, label="취소")
        btnSizer.Add(btnSearch, 0, wx.ALL, 5)
        btnSizer.Add(btnCancel, 0, wx.ALL, 5)
        
        sizer.Add(btnSizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)
    
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
## 예산 설정 다이얼로그
###########################################################################
class BudgetDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="💰 예산 관리", size=(600, 500))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 월 선택
        monthSizer = wx.BoxSizer(wx.HORIZONTAL)
        monthSizer.Add(wx.StaticText(panel, label="대상 월:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.monthChoice = wx.Choice(panel, choices=HL_CRUD.selectMonthList())
        if self.monthChoice.GetCount() > 0:
            self.monthChoice.SetSelection(0)
        monthSizer.Add(self.monthChoice, 1, wx.ALL, 5)
        sizer.Add(monthSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 예산 항목 목록
        self.budgetList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.budgetList.InsertColumn(0, "카테고리", width=150)
        self.budgetList.InsertColumn(1, "예산", width=120)
        self.budgetList.InsertColumn(2, "실제 지출", width=120)
        self.budgetList.InsertColumn(3, "잔액", width=120)
        
        sizer.Add(self.budgetList, 1, wx.EXPAND | wx.ALL, 10)
        
        # 예산 설정
        budgetBox = wx.StaticBoxSizer(wx.HORIZONTAL, panel, "예산 설정")
        budgetBox.Add(wx.StaticText(panel, label="카테고리:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.categoryChoice = wx.Choice(panel, choices=[
            '식비', '교통비', '통신비', '주거비', '의료비', '교육비', '문화비', '기타'
        ])
        budgetBox.Add(self.categoryChoice, 1, wx.ALL, 5)
        
        budgetBox.Add(wx.StaticText(panel, label="예산:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.budgetAmount = wx.TextCtrl(panel, size=(150, -1))
        budgetBox.Add(self.budgetAmount, 0, wx.ALL, 5)
        
        btnSet = wx.Button(panel, label="설정")
        btnSet.Bind(wx.EVT_BUTTON, self.OnSetBudget)
        budgetBox.Add(btnSet, 0, wx.ALL, 5)
        
        sizer.Add(budgetBox, 0, wx.EXPAND | wx.ALL, 10)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSave = wx.Button(panel, wx.ID_OK, label="저장")
        btnCancel = wx.Button(panel, wx.ID_CANCEL, label="닫기")
        btnSizer.Add(btnSave, 0, wx.ALL, 5)
        btnSizer.Add(btnCancel, 0, wx.ALL, 5)
        
        sizer.Add(btnSizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        self.LoadBudgets()
    
    def LoadBudgets(self):
        # 예산 데이터 로드
        self.budgets = {}
        try:
            with open('budgets.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        self.budgets[row[0]] = float(row[1])
        except FileNotFoundError:
            pass
        
        self.UpdateBudgetList()
    
    def UpdateBudgetList(self):
        self.budgetList.DeleteAllItems()
        
        categories = ['식비', '교통비', '통신비', '주거비', '의료비', '교육비', '문화비', '기타']
        for category in categories:
            budget = self.budgets.get(category, 0)
            actual = 0  # 실제 지출은 DB에서 조회해야 함
            balance = budget - actual
            
            idx = self.budgetList.InsertItem(self.budgetList.GetItemCount(), category)
            self.budgetList.SetItem(idx, 1, f"{budget:,.0f}원")
            self.budgetList.SetItem(idx, 2, f"{actual:,.0f}원")
            self.budgetList.SetItem(idx, 3, f"{balance:,.0f}원")
            
            # 색상 표시
            if balance < 0:
                self.budgetList.SetItemTextColour(idx, wx.RED)
    
    def OnSetBudget(self, event):
        category = self.categoryChoice.GetStringSelection()
        amount = self.budgetAmount.GetValue()
        
        if not category:
            wx.MessageBox("카테고리를 선택하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            amount_float = float(amount.replace(',', ''))
            self.budgets[category] = amount_float
            self.UpdateBudgetList()
            self.budgetAmount.Clear()
            wx.MessageBox(f"{category} 예산이 설정되었습니다.", "설정 완료", wx.OK | wx.ICON_INFORMATION)
        except ValueError:
            wx.MessageBox("올바른 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
    
    def SaveBudgets(self):
        with open('budgets.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for category, amount in self.budgets.items():
                writer.writerow([category, amount])


###########################################################################
## 통계 다이얼로그
###########################################################################
class StatisticsDialog(wx.Dialog):
    def __init__(self, parent, data):
        super().__init__(parent, title="📊 통계 분석", size=(700, 500))
        
        self.data = data
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 노트북 (탭)
        notebook = wx.Notebook(panel)
        
        # 월별 통계 탭
        monthlyPanel = wx.Panel(notebook)
        monthlySizer = wx.BoxSizer(wx.VERTICAL)
        
        self.monthlyList = wx.ListCtrl(monthlyPanel, style=wx.LC_REPORT)
        self.monthlyList.InsertColumn(0, "월", width=100)
        self.monthlyList.InsertColumn(1, "수입", width=150)
        self.monthlyList.InsertColumn(2, "지출", width=150)
        self.monthlyList.InsertColumn(3, "잔액", width=150)
        
        monthlySizer.Add(self.monthlyList, 1, wx.EXPAND | wx.ALL, 10)
        monthlyPanel.SetSizer(monthlySizer)
        notebook.AddPage(monthlyPanel, "월별 통계")
        
        # 카테고리별 통계 탭
        categoryPanel = wx.Panel(notebook)
        categorySizer = wx.BoxSizer(wx.VERTICAL)
        
        self.categoryList = wx.ListCtrl(categoryPanel, style=wx.LC_REPORT)
        self.categoryList.InsertColumn(0, "카테고리", width=200)
        self.categoryList.InsertColumn(1, "금액", width=150)
        self.categoryList.InsertColumn(2, "비율", width=100)
        
        categorySizer.Add(self.categoryList, 1, wx.EXPAND | wx.ALL, 10)
        categoryPanel.SetSizer(categorySizer)
        notebook.AddPage(categoryPanel, "카테고리별 통계")
        
        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        # 닫기 버튼
        btnClose = wx.Button(panel, wx.ID_CLOSE, label="닫기")
        btnClose.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        sizer.Add(btnClose, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        self.CalculateStatistics()
    
    def CalculateStatistics(self):
        # 월별 통계
        monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})
        category_data = defaultdict(float)
        
        for row in self.data:
            try:
                month = row[1][:7]  # YYYY-MM
                income = float(row[4]) if row[4] else 0
                expense = float(row[5]) if row[5] else 0
                
                monthly_data[month]['income'] += income
                monthly_data[month]['expense'] += expense
                
                if expense > 0:
                    category = row[3].split('.')[0] if '.' in row[3] else row[3]
                    category_data[category] += expense
            except (ValueError, IndexError):
                continue
        
        # 월별 리스트 채우기
        for month in sorted(monthly_data.keys()):
            income = monthly_data[month]['income']
            expense = monthly_data[month]['expense']
            balance = income - expense
            
            idx = self.monthlyList.InsertItem(self.monthlyList.GetItemCount(), month)
            self.monthlyList.SetItem(idx, 1, f"{income:,.0f}원")
            self.monthlyList.SetItem(idx, 2, f"{expense:,.0f}원")
            self.monthlyList.SetItem(idx, 3, f"{balance:,.0f}원")
            
            if balance < 0:
                self.monthlyList.SetItemTextColour(idx, wx.RED)
        
        # 카테고리별 리스트 채우기
        total_expense = sum(category_data.values())
        for category in sorted(category_data.keys(), key=lambda x: category_data[x], reverse=True):
            amount = category_data[category]
            ratio = (amount / total_expense * 100) if total_expense > 0 else 0
            
            idx = self.categoryList.InsertItem(self.categoryList.GetItemCount(), category)
            self.categoryList.SetItem(idx, 1, f"{amount:,.0f}원")
            self.categoryList.SetItem(idx, 2, f"{ratio:.1f}%")


###########################################################################
## 메인 프레임
###########################################################################
class MyFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="💰 스마트 가계부 v4.0", size=(1200, 700))
        
        self.SetMinSize((1000, 600))
        
        # 메뉴바
        self.CreateMenuBar()
        
        # 메인 패널
        panel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 상단: 입력 영역
        inputSizer = self.CreateInputArea(panel)
        mainSizer.Add(inputSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 중단: 목록 및 그래프
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 왼쪽: 목록
        listBox = wx.StaticBoxSizer(wx.VERTICAL, panel, "📋 내역")
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.InsertColumn(0, "번호", width=60)
        self.list.InsertColumn(1, "날짜", width=100)
        self.list.InsertColumn(2, "구분", width=60)
        self.list.InsertColumn(3, "상세내역", width=180)
        self.list.InsertColumn(4, "수입", width=100)
        self.list.InsertColumn(5, "지출", width=100)
        self.list.InsertColumn(6, "비고", width=200)
        
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        
        listBox.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)
        contentSizer.Add(listBox, 2, wx.EXPAND | wx.ALL, 5)
        
        # 오른쪽: 그래프
        graphBox = wx.StaticBoxSizer(wx.VERTICAL, panel, "📊 지출 현황")
        self.graphPanel = Barchart(panel)
        graphBox.Add(self.graphPanel, 1, wx.EXPAND | wx.ALL, 5)
        contentSizer.Add(graphBox, 1, wx.EXPAND | wx.ALL, 5)
        
        mainSizer.Add(contentSizer, 1, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(mainSizer)
        
        # 초기 데이터 로드
        self.OnSelectAll(None)
        
        self.Centre()
    
    def CreateMenuBar(self):
        """메뉴바 생성"""
        menubar = wx.MenuBar()
        
        # 파일 메뉴
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_ANY, "📤 Excel 내보내기\tCtrl+E", "데이터를 Excel 파일로 내보내기")
        fileMenu.Append(wx.ID_ANY, "📥 CSV 가져오기\tCtrl+I", "CSV 파일에서 데이터 가져오기")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, "🚪 종료\tCtrl+Q", "프로그램 종료")
        menubar.Append(fileMenu, "파일")
        
        # 도구 메뉴
        toolsMenu = wx.Menu()
        toolsMenu.Append(wx.ID_ANY, "🔍 고급 검색\tCtrl+F", "조건별 검색")
        toolsMenu.Append(wx.ID_ANY, "📊 통계 보기\tCtrl+S", "월별/카테고리별 통계")
        toolsMenu.Append(wx.ID_ANY, "💰 예산 관리\tCtrl+B", "월별 예산 설정 및 관리")
        toolsMenu.Append(wx.ID_ANY, "⭐ 즐겨찾기\tCtrl+D", "자주 사용하는 항목 관리")
        menubar.Append(toolsMenu, "도구")
        
        self.SetMenuBar(menubar)
        
        # 메뉴 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.OnExport, id=fileMenu.FindItemByPosition(0).GetId())
        self.Bind(wx.EVT_MENU, self.OnImport, id=fileMenu.FindItemByPosition(1).GetId())
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        
        self.Bind(wx.EVT_MENU, self.OnSearch, id=toolsMenu.FindItemByPosition(0).GetId())
        self.Bind(wx.EVT_MENU, self.OnStatistics, id=toolsMenu.FindItemByPosition(1).GetId())
        self.Bind(wx.EVT_MENU, self.OnBudget, id=toolsMenu.FindItemByPosition(2).GetId())
        self.Bind(wx.EVT_MENU, self.OnFavorites, id=toolsMenu.FindItemByPosition(3).GetId())
    
    def CreateInputArea(self, parent):
        """입력 영역 생성"""
        inputBox = wx.StaticBoxSizer(wx.VERTICAL, parent, "✏️ 입력")
        
        # 날짜 및 비고
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        topSizer.Add(wx.StaticText(parent, label="날짜:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.DatePick = wx.adv.DatePickerCtrl(parent, style=wx.adv.DP_DROPDOWN)
        topSizer.Add(self.DatePick, 0, wx.ALL, 5)
        
        topSizer.Add(wx.StaticText(parent, label="비고:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.txtRemark = wx.TextCtrl(parent, size=(300, -1))
        self.txtRemark.SetHint("메모나 설명을 입력하세요")
        topSizer.Add(self.txtRemark, 1, wx.ALL, 5)
        
        inputBox.Add(topSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 탭으로 수입/지출 구분
        self.notebook = wx.Notebook(parent)
        
        # 수입 탭
        incomePanel = wx.Panel(self.notebook)
        incomeSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        incomeSizer.Add(wx.StaticText(incomePanel, label="항목:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.comboRevenue = wx.ComboBox(incomePanel, choices=[
            '수입.급여', '수입.보너스', '수입.이자', '수입.배당', '수입.기타'
        ], style=wx.CB_DROPDOWN, size=(200, -1))
        incomeSizer.Add(self.comboRevenue, 0, wx.ALL, 5)
        
        incomeSizer.Add(wx.StaticText(incomePanel, label="금액:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.txtRevenue = wx.TextCtrl(incomePanel, size=(150, -1))
        self.txtRevenue.SetHint("금액 입력")
        incomeSizer.Add(self.txtRevenue, 0, wx.ALL, 5)
        
        btnAddIncome = wx.Button(incomePanel, label="✅ 수입 등록", size=(120, 35))
        btnAddIncome.SetBackgroundColour('#4CAF50')
        btnAddIncome.SetForegroundColour('#FFFFFF')
        btnAddIncome.Bind(wx.EVT_BUTTON, self.OnAddIncome)
        incomeSizer.Add(btnAddIncome, 0, wx.ALL, 5)
        
        incomePanel.SetSizer(incomeSizer)
        self.notebook.AddPage(incomePanel, "💰 수입")
        
        # 지출 탭
        expensePanel = wx.Panel(self.notebook)
        expenseSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        expenseSizer.Add(wx.StaticText(expensePanel, label="항목:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.comboExpense = wx.ComboBox(expensePanel, choices=[
            '지출.식비', '지출.교통비', '지출.통신비', '지출.주거비',
            '지출.의료비', '지출.교육비', '지출.문화비', '지출.기타'
        ], style=wx.CB_DROPDOWN, size=(200, -1))
        expenseSizer.Add(self.comboExpense, 0, wx.ALL, 5)
        
        expenseSizer.Add(wx.StaticText(expensePanel, label="금액:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.txtExpense = wx.TextCtrl(expensePanel, size=(150, -1))
        self.txtExpense.SetHint("금액 입력")
        expenseSizer.Add(self.txtExpense, 0, wx.ALL, 5)
        
        btnAddExpense = wx.Button(expensePanel, label="✅ 지출 등록", size=(120, 35))
        btnAddExpense.SetBackgroundColour('#F44336')
        btnAddExpense.SetForegroundColour('#FFFFFF')
        btnAddExpense.Bind(wx.EVT_BUTTON, self.OnAddExpense)
        expenseSizer.Add(btnAddExpense, 0, wx.ALL, 5)
        
        expensePanel.SetSizer(expenseSizer)
        self.notebook.AddPage(expensePanel, "💸 지출")
        
        inputBox.Add(self.notebook, 0, wx.EXPAND | wx.ALL, 5)
        
        # 버튼 영역
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btnUpdate = wx.Button(parent, label="🔄 수정")
        btnUpdate.Bind(wx.EVT_BUTTON, self.OnUpdate)
        btnSizer.Add(btnUpdate, 0, wx.ALL, 5)
        
        btnDelete = wx.Button(parent, label="🗑️ 삭제")
        btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        btnSizer.Add(btnDelete, 0, wx.ALL, 5)
        
        btnSizer.AddStretchSpacer()
        
        btnSelectAll = wx.Button(parent, label="📋 전체 조회")
        btnSelectAll.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        btnSizer.Add(btnSelectAll, 0, wx.ALL, 5)
        
        btnSelectMonth = wx.Button(parent, label="📅 월별 조회")
        btnSelectMonth.Bind(wx.EVT_BUTTON, self.OnSelectMonth)
        btnSizer.Add(btnSelectMonth, 0, wx.ALL, 5)
        
        btnGraph = wx.Button(parent, label="📊 그래프")
        btnGraph.Bind(wx.EVT_BUTTON, self.OnMakeGraph)
        btnSizer.Add(btnGraph, 0, wx.ALL, 5)
        
        inputBox.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        return inputBox
    
    def OnAddIncome(self, event):
        """수입 등록"""
        item = self.comboRevenue.GetValue()
        amount = self.txtRevenue.GetValue()
        remark = self.txtRemark.GetValue()
        date = self.DatePick.GetValue().FormatISODate()
        
        if not item or not amount:
            wx.MessageBox("항목과 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            amount = amount.replace(',', '')
            float(amount)
            
            data = (date, '수입', item, '0', amount, remark)
            HL_CRUD.insert(data)
            
            wx.MessageBox("수입이 등록되었습니다.", "등록 완료", wx.OK | wx.ICON_INFORMATION)
            
            # 입력 필드 초기화
            self.txtRevenue.Clear()
            self.txtRemark.Clear()
            
            # 목록 새로고침
            self.OnSelectAll(None)
            
        except ValueError:
            wx.MessageBox("올바른 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
    
    def OnAddExpense(self, event):
        """지출 등록"""
        item = self.comboExpense.GetValue()
        amount = self.txtExpense.GetValue()
        remark = self.txtRemark.GetValue()
        date = self.DatePick.GetValue().FormatISODate()
        
        if not item or not amount:
            wx.MessageBox("항목과 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            amount = amount.replace(',', '')
            float(amount)
            
            data = (date, '지출', item, amount, '0', remark)
            HL_CRUD.insert(data)
            
            wx.MessageBox("지출이 등록되었습니다.", "등록 완료", wx.OK | wx.ICON_INFORMATION)
            
            # 입력 필드 초기화
            self.txtExpense.Clear()
            self.txtRemark.Clear()
            
            # 목록 새로고침
            self.OnSelectAll(None)
            
        except ValueError:
            wx.MessageBox("올바른 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
    
    def OnUpdate(self, event):
        """항목 수정"""
        idx = self.list.GetFirstSelected()
        if idx < 0:
            wx.MessageBox("수정할 항목을 선택하세요.", "선택 오류", wx.OK | wx.ICON_WARNING)
            return
        
        key = self.list.GetItemText(idx, 0)
        date = self.DatePick.GetValue().FormatISODate()
        remark = self.txtRemark.GetValue()
        
        # 현재 선택된 탭에 따라 데이터 구성
        if self.notebook.GetSelection() == 0:  # 수입 탭
            item = self.comboRevenue.GetValue()
            revenue = self.txtRevenue.GetValue().replace(',', '')
            expense = '0'
            section = '수입'
        else:  # 지출 탭
            item = self.comboExpense.GetValue()
            revenue = '0'
            expense = self.txtExpense.GetValue().replace(',', '')
            section = '지출'
        
        if not item:
            wx.MessageBox("항목을 선택하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            data = (key, date, section, item, revenue, expense, remark)
            HL_CRUD.update(data)
            
            wx.MessageBox("수정되었습니다.", "수정 완료", wx.OK | wx.ICON_INFORMATION)
            self.OnSelectAll(None)
            
        except Exception as e:
            wx.MessageBox(f"수정 실패: {str(e)}", "오류", wx.OK | wx.ICON_ERROR)
    
    def OnDelete(self, event):
        """항목 삭제"""
        idx = self.list.GetFirstSelected()
        if idx < 0:
            wx.MessageBox("삭제할 항목을 선택하세요.", "선택 오류", wx.OK | wx.ICON_WARNING)
            return
        
        result = wx.MessageBox("선택한 항목을 삭제하시겠습니까?", "삭제 확인",
                              wx.YES_NO | wx.ICON_QUESTION)
        
        if result == wx.YES:
            key = self.list.GetItemText(idx, 0)
            HL_CRUD.delete(key)
            
            wx.MessageBox("삭제되었습니다.", "삭제 완료", wx.OK | wx.ICON_INFORMATION)
            self.OnSelectAll(None)
    
    def OnItemSelected(self, event):
        """목록 항목 선택시 입력 필드에 표시"""
        idx = event.GetIndex()
        
        # 날짜 설정
        date_str = self.list.GetItemText(idx, 1)
        try:
            date_parts = date_str.split('-')
            if len(date_parts) == 3:
                year, month, day = map(int, date_parts)
                self.DatePick.SetValue(wx.DateTime(day, month-1, year))
        except:
            pass
        
        # 구분에 따라 탭 전환
        section = self.list.GetItemText(idx, 2)
        item = self.list.GetItemText(idx, 3)
        revenue = self.list.GetItemText(idx, 4).replace(',', '')
        expense = self.list.GetItemText(idx, 5).replace(',', '')
        remark = self.list.GetItemText(idx, 6)
        
        if section == '수입':
            self.notebook.SetSelection(0)
            self.comboRevenue.SetValue(item)
            self.txtRevenue.SetValue(revenue)
        else:
            self.notebook.SetSelection(1)
            self.comboExpense.SetValue(item)
            self.txtExpense.SetValue(expense)
        
        self.txtRemark.SetValue(remark)
    
    def OnSelectAll(self, event):
        """전체 조회"""
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
            
            # 수입은 파란색, 지출은 빨간색
            if row[2] == '수입':
                self.list.SetItemTextColour(idx, wx.Colour(33, 150, 243))
            else:
                self.list.SetItemTextColour(idx, wx.Colour(244, 67, 54))
    
    def OnSelectMonth(self, event):
        """월별 조회"""
        months = HL_CRUD.selectMonthList()
        
        dlg = wx.SingleChoiceDialog(self, "조회할 월을 선택하세요:", "월별 조회", months)
        
        if dlg.ShowModal() == wx.ID_OK:
            selected_month = dlg.GetStringSelection()
            
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
                
                if row[2] == '수입':
                    self.list.SetItemTextColour(idx, wx.Colour(33, 150, 243))
                else:
                    self.list.SetItemTextColour(idx, wx.Colour(244, 67, 54))
        
        dlg.Destroy()
    
    def OnMakeGraph(self, event):
        """그래프 생성"""
        rows = HL_CRUD.selectAll()
        expense_data = defaultdict(float)
        
        for row in rows:
            if row[2] == '지출':
                title = row[3].split('.')[0] if '.' in row[3] else row[3]
                try:
                    amount = float(row[5]) if row[5] else 0
                    if amount > 0:
                        expense_data[title] += amount / 1000  # 천원 단위
                except (ValueError, TypeError):
                    continue
        
        if expense_data:
            self.graphPanel.SetData(dict(expense_data))
            self.graphPanel.SetBackgroundColour('#FFFFFF')
            wx.MessageBox("그래프가 생성되었습니다.", "그래프 생성", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("표시할 지출 데이터가 없습니다.", "그래프 생성", wx.OK | wx.ICON_WARNING)
    
    # 메뉴 이벤트 핸들러
    def OnExport(self, event):
        """Excel로 내보내기"""
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
                
                # 워크북 생성
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "가계부"
                
                # 헤더
                headers = ["거래번호", "날짜", "구분", "상세내역", "수입", "지출", "비고"]
                ws.append(headers)
                
                # 헤더 스타일
                header_fill = PatternFill(start_color="4A90E2", end_color="4A90E2", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF")
                
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center")
                
                # 데이터
                rows = HL_CRUD.selectAll()
                for row in rows:
                    ws.append(list(row))
                
                # 열 너비 조정
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
        """CSV에서 가져오기"""
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
                    next(reader)  # 헤더 스킵
                    
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
        """프로그램 종료"""
        self.Close()
    
    def OnSearch(self, event):
        """고급 검색"""
        dlg = SearchDialog(self)
        
        if dlg.ShowModal() == wx.ID_OK:
            criteria = dlg.GetSearchCriteria()
            
            self.list.DeleteAllItems()
            rows = HL_CRUD.selectAll()
            
            count = 0
            for row in rows:
                # 날짜 필터
                if row[1] < criteria['start_date'] or row[1] > criteria['end_date']:
                    continue
                
                # 구분 필터
                if row[2] == '수입' and not criteria['include_income']:
                    continue
                if row[2] == '지출' and not criteria['include_expense']:
                    continue
                
                # 금액 필터
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
                
                # 키워드 필터
                if criteria['keyword'] and criteria['keyword'] not in row[6]:
                    continue
                
                # 조건을 모두 만족하는 항목 추가
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
        """통계 보기"""
        rows = HL_CRUD.selectAll()
        dlg = StatisticsDialog(self, rows)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnBudget(self, event):
        """예산 관리"""
        dlg = BudgetDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnFavorites(self, event):
        """즐겨찾기 관리"""
        dlg = FavoritesDialog(self)
        
        if dlg.ShowModal() == wx.ID_OK:
            favorite = dlg.GetSelectedFavorite()
            if favorite:
                # 즐겨찾기 항목을 입력 필드에 자동 채우기
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
