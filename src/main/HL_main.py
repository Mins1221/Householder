# -*- coding: utf-8 -*- 

###########################################################################
## Enhanced Smart Household Account Book
## 개선된 스마트 가계부 v3.0
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
        # 즐겨찾기 데이터 로드 (실제로는 파일이나 DB에서)
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
            # 간단한 예제
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
        
        # 예산 항목
        budgetBox = wx.StaticBoxSizer(wx.VERTICAL, panel, "카테고리별 예산")
        
        # 카테고리 목록
        categories = [
            "식비", "교통비", "통신비", "주거비", "의료비",
            "교육비", "문화생활", "경조사비", "기타"
        ]
        
        self.budgetInputs = {}
        grid = wx.FlexGridSizer(cols=2, hgap=10, vgap=5)
        
        for cat in categories:
            label = wx.StaticText(panel, label=f"{cat}:")
            textCtrl = wx.TextCtrl(panel, value="0")
            self.budgetInputs[cat] = textCtrl
            grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(textCtrl, 1, wx.EXPAND)
        
        grid.AddGrowableCol(1)
        budgetBox.Add(grid, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(budgetBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # 총 예산
        totalSizer = wx.BoxSizer(wx.HORIZONTAL)
        totalSizer.Add(wx.StaticText(panel, label="총 예산:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.totalBudget = wx.TextCtrl(panel, style=wx.TE_READONLY)
        totalSizer.Add(self.totalBudget, 1, wx.ALL, 5)
        
        btnCalc = wx.Button(panel, label="계산")
        btnCalc.Bind(wx.EVT_BUTTON, self.OnCalculate)
        totalSizer.Add(btnCalc, 0, wx.ALL, 5)
        sizer.Add(totalSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSave = wx.Button(panel, wx.ID_OK, label="저장")
        btnCancel = wx.Button(panel, wx.ID_CANCEL, label="취소")
        btnSizer.Add(btnSave, 0, wx.ALL, 5)
        btnSizer.Add(btnCancel, 0, wx.ALL, 5)
        
        sizer.Add(btnSizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        self.LoadBudget()
    
    def LoadBudget(self):
        # 예산 데이터 로드
        try:
            with open('budget.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2 and row[0] in self.budgetInputs:
                        self.budgetInputs[row[0]].SetValue(row[1])
        except FileNotFoundError:
            pass
    
    def OnCalculate(self, event):
        total = 0
        for textCtrl in self.budgetInputs.values():
            try:
                value = float(textCtrl.GetValue().replace(',', ''))
                total += value
            except ValueError:
                pass
        
        self.totalBudget.SetValue(f"{total:,.0f}")
    
    def SaveBudget(self):
        with open('budget.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for cat, textCtrl in self.budgetInputs.items():
                writer.writerow([cat, textCtrl.GetValue()])


###########################################################################
## 통계 다이얼로그
###########################################################################
class StatisticsDialog(wx.Dialog):
    def __init__(self, parent, data):
        super().__init__(parent, title="📊 상세 통계", size=(700, 600))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 노트북 (탭)
        notebook = wx.Notebook(panel)
        
        # 월별 통계 탭
        monthlyPanel = wx.Panel(notebook)
        monthlyList = wx.ListCtrl(monthlyPanel, style=wx.LC_REPORT)
        monthlyList.InsertColumn(0, "월", width=100)
        monthlyList.InsertColumn(1, "수입", width=120)
        monthlyList.InsertColumn(2, "지출", width=120)
        monthlyList.InsertColumn(3, "잔액", width=120)
        monthlyList.InsertColumn(4, "저축률", width=100)
        
        # 월별 데이터 집계
        monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})
        for row in data:
            if len(row) >= 6:
                month = row[1][:7]  # YYYY-MM
                try:
                    if row[4]:  # 수입
                        monthly_data[month]['income'] += float(row[4])
                    if row[5]:  # 지출
                        monthly_data[month]['expense'] += float(row[5])
                except (ValueError, TypeError):
                    continue
        
        for month in sorted(monthly_data.keys()):
            income = monthly_data[month]['income']
            expense = monthly_data[month]['expense']
            balance = income - expense
            savings_rate = (balance / income * 100) if income > 0 else 0
            
            idx = monthlyList.InsertItem(monthlyList.GetItemCount(), month)
            monthlyList.SetItem(idx, 1, f"{income:,.0f}")
            monthlyList.SetItem(idx, 2, f"{expense:,.0f}")
            monthlyList.SetItem(idx, 3, f"{balance:,.0f}")
            monthlyList.SetItem(idx, 4, f"{savings_rate:.1f}%")
        
        monthlySizer = wx.BoxSizer(wx.VERTICAL)
        monthlySizer.Add(monthlyList, 1, wx.EXPAND | wx.ALL, 10)
        monthlyPanel.SetSizer(monthlySizer)
        
        # 카테고리별 통계 탭
        categoryPanel = wx.Panel(notebook)
        categoryList = wx.ListCtrl(categoryPanel, style=wx.LC_REPORT)
        categoryList.InsertColumn(0, "카테고리", width=150)
        categoryList.InsertColumn(1, "금액", width=120)
        categoryList.InsertColumn(2, "비율", width=100)
        categoryList.InsertColumn(3, "건수", width=100)
        
        # 카테고리별 데이터 집계
        category_data = defaultdict(lambda: {'amount': 0, 'count': 0})
        total_expense = 0
        
        for row in data:
            if len(row) >= 6 and row[2] == '지출':
                category = row[3]
                try:
                    amount = float(row[5]) if row[5] else 0
                    category_data[category]['amount'] += amount
                    category_data[category]['count'] += 1
                    total_expense += amount
                except (ValueError, TypeError):
                    continue
        
        for category in sorted(category_data.keys(), key=lambda x: category_data[x]['amount'], reverse=True):
            amount = category_data[category]['amount']
            count = category_data[category]['count']
            ratio = (amount / total_expense * 100) if total_expense > 0 else 0
            
            idx = categoryList.InsertItem(categoryList.GetItemCount(), category)
            categoryList.SetItem(idx, 1, f"{amount:,.0f}")
            categoryList.SetItem(idx, 2, f"{ratio:.1f}%")
            categoryList.SetItem(idx, 3, str(count))
        
        categorySizer = wx.BoxSizer(wx.VERTICAL)
        categorySizer.Add(categoryList, 1, wx.EXPAND | wx.ALL, 10)
        categoryPanel.SetSizer(categorySizer)
        
        # 탭 추가
        notebook.AddPage(monthlyPanel, "월별 통계")
        notebook.AddPage(categoryPanel, "카테고리별 통계")
        
        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        # 닫기 버튼
        btnClose = wx.Button(panel, wx.ID_CLOSE, label="닫기")
        btnClose.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        sizer.Add(btnClose, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)


###########################################################################
## 메인 프레임
###########################################################################
class MyFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, title="💰 스마트 가계부 v3.0", 
                        pos=wx.DefaultPosition, size=(1200, 800))
        
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        
        # 아이콘 설정 (선택사항)
        try:
            icon = wx.Icon()
            icon.CopyFromBitmap(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_FRAME_ICON, (16, 16)))
            self.SetIcon(icon)
        except:
            pass
        
        # 메뉴바 생성
        self.CreateMenuBar()
        
        # 상태바 생성
        self.statusBar = self.CreateStatusBar(3, wx.STB_SIZEGRIP)
        self.statusBar.SetStatusWidths([-2, -1, -1])
        self.UpdateStatusBar()
        
        # 메인 패널
        mainPanel = wx.Panel(self)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 상단 정보 패널
        self.CreateInfoPanel(mainPanel, mainSizer)
        
        # 중앙 분할 윈도우
        splitter = wx.SplitterWindow(mainPanel, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        
        # 왼쪽 패널 (입력 및 제어)
        leftPanel = wx.Panel(splitter)
        self.CreateLeftPanel(leftPanel)
        
        # 오른쪽 패널 (리스트 및 그래프)
        rightPanel = wx.Panel(splitter)
        self.CreateRightPanel(rightPanel)
        
        splitter.SplitVertically(leftPanel, rightPanel)
        splitter.SetSashPosition(400)
        splitter.SetMinimumPaneSize(300)
        
        mainSizer.Add(splitter, 1, wx.EXPAND | wx.ALL, 5)
        
        mainPanel.SetSizer(mainSizer)
        
        self.Centre(wx.BOTH)
        
        # 초기 데이터 로드
        self.OnSelectAll(None)
    
    def CreateMenuBar(self):
        """메뉴바 생성"""
        menuBar = wx.MenuBar()
        
        # 파일 메뉴
        fileMenu = wx.Menu()
        menuExport = fileMenu.Append(wx.ID_ANY, "📤 Excel로 내보내기\tCtrl+E")
        menuImport = fileMenu.Append(wx.ID_ANY, "📥 CSV 가져오기\tCtrl+I")
        fileMenu.AppendSeparator()
        menuExit = fileMenu.Append(wx.ID_EXIT, "🚪 종료\tCtrl+Q")
        
        # 도구 메뉴
        toolMenu = wx.Menu()
        menuSearch = toolMenu.Append(wx.ID_ANY, "🔍 고급 검색\tCtrl+F")
        menuStatistics = toolMenu.Append(wx.ID_ANY, "📊 통계 보기\tCtrl+T")
        toolMenu.AppendSeparator()
        menuBudget = toolMenu.Append(wx.ID_ANY, "💰 예산 관리\tCtrl+B")
        menuFavorites = toolMenu.Append(wx.ID_ANY, "⭐ 즐겨찾기\tCtrl+D")
        
        # 도움말 메뉴
        helpMenu = wx.Menu()
        menuAbout = helpMenu.Append(wx.ID_ABOUT, "ℹ️ 프로그램 정보")
        
        menuBar.Append(fileMenu, "파일(&F)")
        menuBar.Append(toolMenu, "도구(&T)")
        menuBar.Append(helpMenu, "도움말(&H)")
        
        self.SetMenuBar(menuBar)
        
        # 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.OnExport, menuExport)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImport)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnSearch, menuSearch)
        self.Bind(wx.EVT_MENU, self.OnStatistics, menuStatistics)
        self.Bind(wx.EVT_MENU, self.OnBudget, menuBudget)
        self.Bind(wx.EVT_MENU, self.OnFavorites, menuFavorites)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
    
    def CreateInfoPanel(self, parent, sizer):
        """상단 정보 패널 생성"""
        infoPanel = wx.Panel(parent)
        infoPanel.SetBackgroundColour(wx.Colour(240, 248, 255))
        
        infoSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 현재 날짜
        now = datetime.now()
        date_str = f"📅 {now.year}년 {now.month}월 {now.day}일"
        dateText = wx.StaticText(infoPanel, label=date_str)
        font = dateText.GetFont()
        font.PointSize += 2
        font = font.Bold()
        dateText.SetFont(font)
        
        infoSizer.Add(dateText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        infoSizer.AddStretchSpacer()
        
        # 요약 정보
        self.summaryText = wx.StaticText(infoPanel, label="수입: 0원 | 지출: 0원 | 잔액: 0원")
        summaryFont = self.summaryText.GetFont()
        summaryFont.PointSize += 1
        self.summaryText.SetFont(summaryFont)
        
        infoSizer.Add(self.summaryText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        infoPanel.SetSizer(infoSizer)
        sizer.Add(infoPanel, 0, wx.EXPAND | wx.ALL, 5)
    
    def CreateLeftPanel(self, parent):
        """왼쪽 패널 (입력 및 제어) 생성"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 입력 영역
        inputBox = wx.StaticBoxSizer(wx.VERTICAL, parent, "📝 거래 입력")
        
        # 날짜 선택
        dateSizer = wx.BoxSizer(wx.HORIZONTAL)
        dateSizer.Add(wx.StaticText(parent, label="날짜:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.datePicker = wx.adv.DatePickerCtrl(parent, style=wx.adv.DP_DROPDOWN)
        dateSizer.Add(self.datePicker, 1, wx.EXPAND)
        inputBox.Add(dateSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 구분 라디오 버튼
        radioSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.RadioRevenue = wx.RadioButton(parent, label="💰 수입", style=wx.RB_GROUP)
        self.RadioExpense = wx.RadioButton(parent, label="💸 지출")
        radioSizer.Add(self.RadioRevenue, 0, wx.ALL, 5)
        radioSizer.Add(self.RadioExpense, 0, wx.ALL, 5)
        inputBox.Add(radioSizer, 0, wx.ALL, 5)
        
        # 수입 항목 (StaticText와 콤보박스를 별도 행으로 분리)
        revenueBox = wx.StaticBoxSizer(wx.VERTICAL, parent, "수입 항목")
        
        revenueLabelSizer = wx.BoxSizer(wx.HORIZONTAL)
        revenueLabelSizer.Add(wx.StaticText(parent, label="항목:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        revenueBox.Add(revenueLabelSizer, 0, wx.EXPAND | wx.ALL, 3)
        
        self.comboRevenue = wx.ComboBox(parent, choices=[
            "수입.급여", "수입.상여", "수입.부수입", "수입.이자",
            "수입.배당", "수입.기타"
        ], style=wx.CB_DROPDOWN)
        revenueBox.Add(self.comboRevenue, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 3)
        
        revenueAmountSizer = wx.BoxSizer(wx.HORIZONTAL)
        revenueAmountSizer.Add(wx.StaticText(parent, label="금액:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.txtRevenue = wx.TextCtrl(parent, value="0")
        revenueAmountSizer.Add(self.txtRevenue, 1, wx.EXPAND)
        revenueBox.Add(revenueAmountSizer, 0, wx.EXPAND | wx.ALL, 3)
        
        inputBox.Add(revenueBox, 0, wx.EXPAND | wx.ALL, 5)
        
        # 지출 항목 (StaticText와 콤보박스를 별도 행으로 분리)
        expenseBox = wx.StaticBoxSizer(wx.VERTICAL, parent, "지출 항목")
        
        expenseLabelSizer = wx.BoxSizer(wx.HORIZONTAL)
        expenseLabelSizer.Add(wx.StaticText(parent, label="항목:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        expenseBox.Add(expenseLabelSizer, 0, wx.EXPAND | wx.ALL, 3)
        
        self.comboExpense = wx.ComboBox(parent, choices=[
            "지출.식비", "지출.교통비", "지출.통신비", "지출.주거비",
            "지출.의료비", "지출.교육비", "지출.문화생활", "지출.경조사비",
            "지출.세금", "지출.보험료", "지출.대출상환", "지출.기타"
        ], style=wx.CB_DROPDOWN)
        expenseBox.Add(self.comboExpense, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 3)
        
        expenseAmountSizer = wx.BoxSizer(wx.HORIZONTAL)
        expenseAmountSizer.Add(wx.StaticText(parent, label="금액:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.txtExpense = wx.TextCtrl(parent, value="0")
        expenseAmountSizer.Add(self.txtExpense, 1, wx.EXPAND)
        expenseBox.Add(expenseAmountSizer, 0, wx.EXPAND | wx.ALL, 3)
        
        inputBox.Add(expenseBox, 0, wx.EXPAND | wx.ALL, 5)
        
        # 비고
        remarkSizer = wx.BoxSizer(wx.HORIZONTAL)
        remarkSizer.Add(wx.StaticText(parent, label="비고:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.txtRemark = wx.TextCtrl(parent)
        remarkSizer.Add(self.txtRemark, 1, wx.EXPAND)
        inputBox.Add(remarkSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(inputBox, 0, wx.EXPAND | wx.ALL, 10)
        
        # 버튼 영역
        btnBox = wx.StaticBoxSizer(wx.VERTICAL, parent, "⚙️ 제어")
        
        btnGrid = wx.GridSizer(rows=3, cols=2, hgap=5, vgap=5)
        
        self.btnInsert = wx.Button(parent, label="➕ 추가")
        self.btnUpdate = wx.Button(parent, label="✏️ 수정")
        self.btnDelete = wx.Button(parent, label="🗑️ 삭제")
        self.btnSelectAll = wx.Button(parent, label="📋 전체조회")
        self.btnMonthSum = wx.Button(parent, label="📊 월별합계")
        self.btnClear = wx.Button(parent, label="🔄 초기화")
        
        btnGrid.Add(self.btnInsert, 0, wx.EXPAND)
        btnGrid.Add(self.btnUpdate, 0, wx.EXPAND)
        btnGrid.Add(self.btnDelete, 0, wx.EXPAND)
        btnGrid.Add(self.btnSelectAll, 0, wx.EXPAND)
        btnGrid.Add(self.btnMonthSum, 0, wx.EXPAND)
        btnGrid.Add(self.btnClear, 0, wx.EXPAND)
        
        btnBox.Add(btnGrid, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btnBox, 0, wx.EXPAND | wx.ALL, 10)
        
        # 작업 내역
        historyBox = wx.StaticBoxSizer(wx.VERTICAL, parent, "📜 작업 내역")
        self.txtWorkHistory = wx.TextCtrl(parent, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        self.txtWorkHistory.SetBackgroundColour(wx.Colour(250, 250, 250))
        historyBox.Add(self.txtWorkHistory, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(historyBox, 1, wx.EXPAND | wx.ALL, 10)
        
        parent.SetSizer(sizer)
        
        # 이벤트 바인딩
        self.btnInsert.Bind(wx.EVT_BUTTON, self.OnInsert)
        self.btnUpdate.Bind(wx.EVT_BUTTON, self.OnUpdate)
        self.btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        self.btnSelectAll.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        self.btnMonthSum.Bind(wx.EVT_BUTTON, self.OnMonthSum)
        self.btnClear.Bind(wx.EVT_BUTTON, self.OnClear)
    
    def CreateRightPanel(self, parent):
        """오른쪽 패널 (리스트 및 그래프) 생성"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 리스트 영역
        listBox = wx.StaticBoxSizer(wx.VERTICAL, parent, "📊 거래 내역")
        
        self.list = wx.ListCtrl(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.InsertColumn(0, "거래번호", width=80)
        self.list.InsertColumn(1, "날짜", width=100)
        self.list.InsertColumn(2, "구분", width=70)
        self.list.InsertColumn(3, "상세내역", width=150)
        self.list.InsertColumn(4, "수입", width=100)
        self.list.InsertColumn(5, "지출", width=100)
        self.list.InsertColumn(6, "비고", width=200)
        
        listBox.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)
        
        # 리스트 하단 버튼
        listBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnDraw = wx.Button(parent, label="📈 그래프 생성")
        self.btnErase = wx.Button(parent, label="🗑️ 그래프 지우기")
        listBtnSizer.Add(self.btnDraw, 0, wx.ALL, 5)
        listBtnSizer.Add(self.btnErase, 0, wx.ALL, 5)
        listBox.Add(listBtnSizer, 0, wx.ALL, 5)
        
        sizer.Add(listBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # 그래프 영역
        graphBox = wx.StaticBoxSizer(wx.VERTICAL, parent, "📊 지출 현황 그래프")
        self.graphPanel = Barchart(parent)
        self.graphPanel.SetMinSize((400, 250))
        graphBox.Add(self.graphPanel, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(graphBox, 0, wx.EXPAND | wx.ALL, 10)
        
        parent.SetSizer(sizer)
        
        # 이벤트 바인딩
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        self.btnDraw.Bind(wx.EVT_BUTTON, self.OnDraw)
        self.btnErase.Bind(wx.EVT_BUTTON, self.OnErase)
    
    def UpdateStatusBar(self):
        """상태바 업데이트"""
        now = datetime.now()
        date_str = f"📅 {now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"
        self.statusBar.SetStatusText(date_str, 0)
        self.statusBar.SetStatusText("✅ 준비", 1)
        self.statusBar.SetStatusText("v3.0", 2)
    
    def UpdateSummary(self):
        """요약 정보 업데이트"""
        rows = HL_CRUD.selectAll()
        total_income = 0
        total_expense = 0
        
        for row in rows:
            try:
                if row[4]:  # 수입
                    total_income += float(row[4])
                if row[5]:  # 지출
                    total_expense += float(row[5])
            except (ValueError, TypeError):
                continue
        
        balance = total_income - total_expense
        self.summaryText.SetLabel(
            f"수입: {total_income:,.0f}원 | 지출: {total_expense:,.0f}원 | 잔액: {balance:,.0f}원"
        )
    
    def OnAbout(self, event):
        """프로그램 정보"""
        info = wx.adv.AboutDialogInfo()
        info.SetName("스마트 가계부")
        info.SetVersion("3.0")
        info.SetDescription("개인 재무 관리를 위한 스마트 가계부 프로그램")
        info.SetWebSite("https://github.com/yourusername/smart-accountbook")
        info.AddDeveloper("개발자")
        info.SetLicence("MIT License")
        
        wx.adv.AboutBox(info)
    
    # 리스트 이벤트
    def OnListItemSelected(self, event):
        """리스트 항목 선택 시"""
        idx = event.GetIndex()
        
        # 선택된 항목의 데이터 가져오기
        key = self.list.GetItemText(idx, 0)
        date = self.list.GetItemText(idx, 1)
        section = self.list.GetItemText(idx, 2)
        title = self.list.GetItemText(idx, 3)
        revenue = self.list.GetItemText(idx, 4)
        expense = self.list.GetItemText(idx, 5)
        remark = self.list.GetItemText(idx, 6)
        
        # 날짜 설정
        try:
            date_parts = date.split('-')
            if len(date_parts) == 3:
                year, month, day = map(int, date_parts)
                wx_date = wx.DateTime()
                wx_date.Set(day, month - 1, year)
                self.datePicker.SetValue(wx_date)
        except:
            pass
        
        # 구분에 따라 라디오 버튼 및 값 설정
        if section == "수입":
            self.RadioRevenue.SetValue(True)
            self.comboRevenue.SetValue(title)
            self.txtRevenue.SetValue(revenue.replace(',', ''))
            self.txtExpense.SetValue("0")
        else:
            self.RadioExpense.SetValue(True)
            self.comboExpense.SetValue(title)
            self.txtExpense.SetValue(expense.replace(',', ''))
            self.txtRevenue.SetValue("0")
        
        self.txtRemark.SetValue(remark)
        
        self.txtWorkHistory.AppendText(f" 📌 항목 선택: {key} - {title}\n")
    
    # CRUD 이벤트
    def OnInsert(self, event):
        """데이터 추가"""
        date = self.datePicker.GetValue().FormatISODate()
        
        if self.RadioRevenue.GetValue():
            section = "수입"
            title = self.comboRevenue.GetValue()
            revenue = self.txtRevenue.GetValue().replace(',', '')
            expense = "0"
        else:
            section = "지출"
            title = self.comboExpense.GetValue()
            revenue = "0"
            expense = self.txtExpense.GetValue().replace(',', '')
        
        remark = self.txtRemark.GetValue()
        
        # 유효성 검사
        if not title:
            wx.MessageBox("항목을 선택해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            amount = float(revenue) if revenue != "0" else float(expense)
            if amount <= 0:
                wx.MessageBox("금액을 입력해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return
        except ValueError:
            wx.MessageBox("올바른 금액을 입력해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        # DB 삽입
        HL_CRUD.insert((date, section, title, revenue, expense, remark))
        
        self.txtWorkHistory.AppendText(f" ✅ 추가 완료: {date} - {title} ({section})\n")
        self.OnSelectAll(None)
        self.OnClear(None)
    
    def OnUpdate(self, event):
        """데이터 수정"""
        idx = self.list.GetFirstSelected()
        if idx < 0:
            wx.MessageBox("수정할 항목을 선택해주세요.", "선택 오류", wx.OK | wx.ICON_WARNING)
            return
        
        key = self.list.GetItemText(idx, 0)
        date = self.datePicker.GetValue().FormatISODate()
        
        if self.RadioRevenue.GetValue():
            section = "수입"
            title = self.comboRevenue.GetValue()
            revenue = self.txtRevenue.GetValue().replace(',', '')
            expense = "0"
        else:
            section = "지출"
            title = self.comboExpense.GetValue()
            revenue = "0"
            expense = self.txtExpense.GetValue().replace(',', '')
        
        remark = self.txtRemark.GetValue()
        
        # DB 업데이트
        HL_CRUD.update((key, date, section, title, revenue, expense, remark))
        
        self.txtWorkHistory.AppendText(f" ✏️ 수정 완료: {key} - {title}\n")
        self.OnSelectAll(None)
    
    def OnDelete(self, event):
        """데이터 삭제"""
        idx = self.list.GetFirstSelected()
        if idx < 0:
            wx.MessageBox("삭제할 항목을 선택해주세요.", "선택 오류", wx.OK | wx.ICON_WARNING)
            return
        
        key = self.list.GetItemText(idx, 0)
        title = self.list.GetItemText(idx, 3)
        
        # 확인 대화상자
        dlg = wx.MessageDialog(
            self,
            f"'{title}' 항목을 삭제하시겠습니까?",
            "삭제 확인",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            HL_CRUD.delete(key)
            self.txtWorkHistory.AppendText(f" 🗑️ 삭제 완료: {key} - {title}\n")
            self.OnSelectAll(None)
            self.OnClear(None)
        
        dlg.Destroy()
    
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
        
        self.UpdateSummary()
        self.txtWorkHistory.AppendText(f" 📋 전체 조회 완료 - {len(rows)}건\n")
        
        if event:
            event.Skip()
    
    def OnMonthSum(self, event):
        """월별 합계"""
        # 월 선택 다이얼로그
        months = HL_CRUD.selectMonthList()
        
        if not months:
            wx.MessageBox("조회할 데이터가 없습니다.", "정보", wx.OK | wx.ICON_INFORMATION)
            return
        
        dlg = wx.SingleChoiceDialog(
            self,
            "월을 선택하세요:",
            "월별 합계",
            months
        )
        
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
            
            self.txtWorkHistory.AppendText(f" 📊 월별합계 조회: {selected_month}\n")
        
        dlg.Destroy()
        
        if event:
            event.Skip()
    
    def OnClear(self, event):
        """입력 필드 초기화"""
        self.datePicker.SetValue(wx.DateTime.Today())
        self.RadioRevenue.SetValue(True)
        self.comboRevenue.SetValue("")
        self.comboExpense.SetValue("")
        self.txtRevenue.SetValue("0")
        self.txtExpense.SetValue("0")
        self.txtRemark.SetValue("")
        
        self.txtWorkHistory.AppendText(" 🔄 입력 필드 초기화\n")
        
        if event:
            event.Skip()
    
    def OnDraw(self, event):
        """그래프 생성"""
        rows = HL_CRUD.selectAll()
        
        # 지출 데이터만 추출
        expense_data = defaultdict(float)
        
        for row in rows:
            if len(row) >= 6 and row[2] == '지출':
                title = row[3]
                try:
                    amount = float(row[5]) if row[5] else 0
                    if amount > 0:
                        expense_data[title] += amount / 1000  # 천원 단위
                except (ValueError, TypeError):
                    continue
        
        if expense_data:
            self.graphPanel.SetData(dict(expense_data))
            self.graphPanel.SetBackgroundColour('#FFFFFF')
            self.txtWorkHistory.AppendText(" 📊 지출현황 그래프 생성완료.\n")
        else:
            self.txtWorkHistory.AppendText(" ⚠️ 표시할 지출 데이터가 없습니다.\n")
        
        if event:
            event.Skip()
    
    def OnErase(self, event):
        """그래프 지우기"""
        try:
            self.graphPanel.Destroy()
            self.graphPanel = Barchart(self.GetParent())
            self.txtWorkHistory.AppendText(" 🗑️ 그래프 지우기 완료.\n")
        except:
            self.txtWorkHistory.AppendText(" ⚠️ 그래프 지우기 실패.\n")
        
        if event:
            event.Skip()
    
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
                
                self.txtWorkHistory.AppendText(f" ✅ Excel 파일로 내보내기 완료: {filepath}\n")
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
                            # date, section, title, revenue, expense, remark
                            HL_CRUD.insert((row[1], row[2], row[3], row[4], row[5], row[6]))
                            count += 1
                
                self.txtWorkHistory.AppendText(f" ✅ CSV 가져오기 완료: {count}건\n")
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
            
            self.txtWorkHistory.AppendText(f" 🔍 검색 완료 - {count}건 발견\n")
        
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
                    self.RadioRevenue.SetValue(True)
                    self.comboRevenue.SetValue(favorite[1])
                    self.txtRevenue.SetValue(favorite[2])
                else:
                    self.RadioExpense.SetValue(True)
                    self.comboExpense.SetValue(favorite[1])
                    self.txtExpense.SetValue(favorite[2])
                
                self.txtRemark.SetValue(favorite[3])
                self.txtWorkHistory.AppendText(" ⭐ 즐겨찾기 항목이 적용되었습니다.\n")
        
        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(parent=None)
    frame.Show()
    app.MainLoop()
