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
        super().__init__(parent, title="💰 예산 설정", size=(600, 500))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 월 선택
        monthSizer = wx.BoxSizer(wx.HORIZONTAL)
        monthSizer.Add(wx.StaticText(panel, label="대상 월:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.monthPicker = wx.TextCtrl(panel, value=datetime.now().strftime("%Y-%m"))
        monthSizer.Add(self.monthPicker, 1, wx.ALL, 5)
        sizer.Add(monthSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 예산 목록
        self.budgetList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.budgetList.InsertColumn(0, "카테고리", width=200)
        self.budgetList.InsertColumn(1, "예산", width=120)
        self.budgetList.InsertColumn(2, "실제 지출", width=120)
        self.budgetList.InsertColumn(3, "잔액", width=120)
        
        sizer.Add(self.budgetList, 1, wx.EXPAND | wx.ALL, 10)
        
        # 입력 영역
        inputSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.categoryChoice = wx.ComboBox(panel, choices=[
            "지출.식대", "지출.간식", "지출.여가생활", "지출.소모품",
            "지출.패션", "지출.가전", "지출.차량", "지출.공과금", "지출.보험"
        ])
        self.budgetAmount = wx.TextCtrl(panel)
        btnSet = wx.Button(panel, label="설정")
        
        inputSizer.Add(wx.StaticText(panel, label="카테고리:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        inputSizer.Add(self.categoryChoice, 1, wx.ALL, 5)
        inputSizer.Add(wx.StaticText(panel, label="예산:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        inputSizer.Add(self.budgetAmount, 1, wx.ALL, 5)
        inputSizer.Add(btnSet, 0, wx.ALL, 5)
        
        sizer.Add(inputSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # 버튼
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnClose = wx.Button(panel, wx.ID_CLOSE, label="닫기")
        btnSizer.AddStretchSpacer()
        btnSizer.Add(btnClose, 0, wx.ALL, 5)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        btnSet.Bind(wx.EVT_BUTTON, self.OnSetBudget)
        btnClose.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
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
        
        self.RefreshList()
    
    def RefreshList(self):
        self.budgetList.DeleteAllItems()
        for category, budget in self.budgets.items():
            idx = self.budgetList.InsertItem(self.budgetList.GetItemCount(), category)
            self.budgetList.SetItem(idx, 1, f"{budget:,.0f}")
            self.budgetList.SetItem(idx, 2, "0")  # 실제 지출은 메인에서 계산 필요
            self.budgetList.SetItem(idx, 3, f"{budget:,.0f}")
    
    def OnSetBudget(self, event):
        category = self.categoryChoice.GetValue()
        amount = self.budgetAmount.GetValue()
        
        if not category or not amount:
            wx.MessageBox("카테고리와 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            amount_float = float(amount.replace(',', ''))
            self.budgets[category] = amount_float
            self.SaveBudgets()
            self.RefreshList()
            wx.MessageBox(f"{category}의 예산이 {amount_float:,.0f}원으로 설정되었습니다.", "예산 설정 완료", wx.OK | wx.ICON_INFORMATION)
        except ValueError:
            wx.MessageBox("올바른 금액을 입력하세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
    
    def SaveBudgets(self):
        with open('budgets.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for category, budget in self.budgets.items():
                writer.writerow([category, budget])


###########################################################################
## 통계 대시보드 다이얼로그
###########################################################################
class StatisticsDialog(wx.Dialog):
    def __init__(self, parent, data):
        super().__init__(parent, title="📊 통계 대시보드", size=(800, 600))
        
        self.data = data
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 월별 요약
        summaryBox = wx.StaticBoxSizer(wx.VERTICAL, panel, "월별 요약")
        
        # 총 수입/지출
        totalSizer = wx.GridSizer(2, 2, 10, 20)
        
        self.totalIncome = wx.StaticText(panel, label="총 수입: 0원")
        self.totalExpense = wx.StaticText(panel, label="총 지출: 0원")
        self.balance = wx.StaticText(panel, label="잔액: 0원")
        self.avgDaily = wx.StaticText(panel, label="일평균 지출: 0원")
        
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.totalIncome.SetFont(font)
        self.totalExpense.SetFont(font)
        self.balance.SetFont(font)
        self.avgDaily.SetFont(font)
        
        totalSizer.Add(self.totalIncome, 0, wx.ALL, 5)
        totalSizer.Add(self.totalExpense, 0, wx.ALL, 5)
        totalSizer.Add(self.balance, 0, wx.ALL, 5)
        totalSizer.Add(self.avgDaily, 0, wx.ALL, 5)
        
        summaryBox.Add(totalSizer, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(summaryBox, 0, wx.EXPAND | wx.ALL, 10)
        
        # 카테고리별 지출
        categoryBox = wx.StaticBoxSizer(wx.VERTICAL, panel, "카테고리별 지출 현황")
        
        self.categoryList = wx.ListCtrl(panel, style=wx.LC_REPORT)
        self.categoryList.InsertColumn(0, "카테고리", width=200)
        self.categoryList.InsertColumn(1, "금액", width=150)
        self.categoryList.InsertColumn(2, "비율", width=100)
        self.categoryList.InsertColumn(3, "건수", width=100)
        
        categoryBox.Add(self.categoryList, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(categoryBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # 닫기 버튼
        btnClose = wx.Button(panel, wx.ID_CLOSE, label="닫기")
        btnClose.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        sizer.Add(btnClose, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        
        self.CalculateStatistics()
    
    def CalculateStatistics(self):
        total_income = 0
        total_expense = 0
        category_stats = defaultdict(lambda: {'amount': 0, 'count': 0})
        
        for row in self.data:
            if len(row) >= 6:
                section = row[2]
                title = row[3]
                revenue = float(row[4]) if row[4] else 0
                expense = float(row[5]) if row[5] else 0
                
                if section == '수입':
                    total_income += revenue
                elif section == '지출':
                    total_expense += expense
                    category_stats[title]['amount'] += expense
                    category_stats[title]['count'] += 1
        
        balance = total_income - total_expense
        
        # UI 업데이트
        self.totalIncome.SetLabel(f"총 수입: {total_income:,.0f}원")
        self.totalIncome.SetForegroundColour('#5CB85C')
        
        self.totalExpense.SetLabel(f"총 지출: {total_expense:,.0f}원")
        self.totalExpense.SetForegroundColour('#E74C3C')
        
        self.balance.SetLabel(f"잔액: {balance:,.0f}원")
        self.balance.SetForegroundColour('#5CB85C' if balance >= 0 else '#E74C3C')
        
        if len(self.data) > 0:
            avg_daily = total_expense / max(len(set(row[1] for row in self.data if len(row) >= 2)), 1)
            self.avgDaily.SetLabel(f"일평균 지출: {avg_daily:,.0f}원")
        
        # 카테고리별 통계
        self.categoryList.DeleteAllItems()
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['amount'], reverse=True)
        
        for category, stats in sorted_categories:
            if total_expense > 0:
                ratio = (stats['amount'] / total_expense) * 100
            else:
                ratio = 0
            
            idx = self.categoryList.InsertItem(self.categoryList.GetItemCount(), category)
            self.categoryList.SetItem(idx, 1, f"{stats['amount']:,.0f}원")
            self.categoryList.SetItem(idx, 2, f"{ratio:.1f}%")
            self.categoryList.SetItem(idx, 3, f"{stats['count']}건")


###########################################################################
## 메인 프레임
###########################################################################
class MyFrame(wx.Frame):
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"💰 스마트 가계부 v3.0", 
                         pos=wx.DefaultPosition, size=wx.Size(1360, 768), 
                         style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        
        # 모던 컬러 테마 정의
        self.COLORS = {
            'background': '#FFFFFF',
            'secondary_bg': '#F8F9FA',
            'primary': '#4A90E2',
            'success': '#5CB85C',
            'danger': '#E74C3C',
            'warning': '#F39C12',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
            'border': '#E1E8ED',
            'card': '#FFFFFF',
            'hover': '#E8F4F8'
        }
        
        # 메인 패널 설정
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetBackgroundColour(self.COLORS['background'])
        
        # 전체 레이아웃
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 타이틀 바 (헤더)
        headerPanel = self.CreateHeaderPanel()
        mainSizer.Add(headerPanel, 0, wx.EXPAND | wx.ALL, 0)
        
        # 메뉴바
        menuBar = self.CreateMenuBar()
        self.SetMenuBar(menuBar)
        
        # 컨텐츠 영역
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 왼쪽: 입력 영역
        leftPanel = self.CreateInputPanel()
        contentSizer.Add(leftPanel, 0, wx.EXPAND | wx.ALL, 15)
        
        # 오른쪽: 리스트 및 그래프 영역
        rightPanel = self.CreateDisplayPanel()
        contentSizer.Add(rightPanel, 1, wx.EXPAND | wx.ALL, 15)
        
        mainSizer.Add(contentSizer, 1, wx.EXPAND)
        
        self.mainPanel.SetSizer(mainSizer)
        self.Layout()
        
        # 이벤트 바인딩
        self.BindEvents()
        
        # 초기 데이터 로드
        self.LoadInitialData()
    
    def CreateMenuBar(self):
        """메뉴바 생성"""
        menuBar = wx.MenuBar()
        
        # 파일 메뉴
        fileMenu = wx.Menu()
        exportItem = fileMenu.Append(wx.ID_ANY, "📤 내보내기 (Excel)\tCtrl+E", "데이터를 Excel로 내보내기")
        importItem = fileMenu.Append(wx.ID_ANY, "📥 가져오기 (CSV)\tCtrl+I", "CSV에서 데이터 가져오기")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT, "종료\tCtrl+Q")
        
        # 도구 메뉴
        toolMenu = wx.Menu()
        searchItem = toolMenu.Append(wx.ID_ANY, "🔍 고급 검색\tCtrl+F", "상세 검색")
        statsItem = toolMenu.Append(wx.ID_ANY, "📊 통계 보기\tCtrl+T", "통계 대시보드")
        budgetItem = toolMenu.Append(wx.ID_ANY, "💰 예산 관리\tCtrl+B", "예산 설정 및 관리")
        favoriteItem = toolMenu.Append(wx.ID_ANY, "⭐ 즐겨찾기\tCtrl+D", "즐겨찾기 관리")
        
        menuBar.Append(fileMenu, "파일")
        menuBar.Append(toolMenu, "도구")
        
        # 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.OnExport, exportItem)
        self.Bind(wx.EVT_MENU, self.OnImport, importItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnSearch, searchItem)
        self.Bind(wx.EVT_MENU, self.OnStatistics, statsItem)
        self.Bind(wx.EVT_MENU, self.OnBudget, budgetItem)
        self.Bind(wx.EVT_MENU, self.OnFavorites, favoriteItem)
        
        return menuBar
    
    def CreateHeaderPanel(self):
        """모던한 헤더 패널 생성"""
        headerPanel = wx.Panel(self.mainPanel)
        headerPanel.SetBackgroundColour(self.COLORS['primary'])
        headerPanel.SetMinSize((-1, 70))
        
        headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 타이틀
        titleText = wx.StaticText(headerPanel, label="💰 스마트 가계부")
        titleFont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                           wx.FONTWEIGHT_BOLD, faceName="맑은 고딕")
        titleText.SetFont(titleFont)
        titleText.SetForegroundColour('#FFFFFF')
        
        headerSizer.Add(titleText, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 30)
        headerSizer.AddStretchSpacer()
        
        # 버전 정보
        versionText = wx.StaticText(headerPanel, label="v3.0 Enhanced")
        versionFont = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        versionText.SetFont(versionFont)
        versionText.SetForegroundColour('#BFD9F2')
        
        headerSizer.Add(versionText, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 30)
        
        headerPanel.SetSizer(headerSizer)
        return headerPanel
    
    def CreateInputPanel(self):
        """왼쪽 입력 패널 생성"""
        inputPanel = wx.Panel(self.mainPanel)
        inputPanel.SetBackgroundColour(self.COLORS['secondary_bg'])
        inputPanel.SetMinSize((450, -1))
        
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 날짜 선택 카드
        dateCard = self.CreateCard(inputPanel, "📅 거래 일자")
        dateSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.datePicker = wx.adv.DatePickerCtrl(
            dateCard,
            wx.ID_ANY,
            style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY
        )
        self.datePicker.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                       wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        dateSizer.Add(self.datePicker, 0, wx.EXPAND | wx.ALL, 10)
        
        dateCard.SetSizer(dateSizer)
        inputSizer.Add(dateCard, 0, wx.EXPAND | wx.ALL, 8)
        
        # 월별 조회 카드
        monthCard = self.CreateCard(inputPanel, "📊 월별 조회")
        monthSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        months = HL_CRUD.selectMonthList()
        if not months:
            months = ['데이터 없음']
        
        self.cboMonth = wx.ComboBox(monthCard, choices=months, style=wx.CB_READONLY)
        if months and months[0] != '데이터 없음':
            self.cboMonth.SetSelection(0)
        self.cboMonth.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                     wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        self.btnMonthlySum = self.CreateStyledButton(monthCard, "조회", self.COLORS['primary'])
        
        monthSizer.Add(self.cboMonth, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        monthSizer.Add(self.btnMonthlySum, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        
        monthCard.SetSizer(monthSizer)
        inputSizer.Add(monthCard, 0, wx.EXPAND | wx.ALL, 8)
        
        # 수입 입력 카드
        revenueCard = self.CreateCard(inputPanel, "💵 수입")
        revenueSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.RadioRevenue = wx.RadioButton(revenueCard, label="수입 항목 선택")
        self.RadioRevenue.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                         wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        self.RadioRevenue.SetForegroundColour(self.COLORS['success'])
        
        comboRevenueChoices = ["상세내역 선택", "수입.급여", "수입.상여", "수입.이자", 
                              "수입.배당", "수입.사업", "수입.연금", "수입.기타"]
        self.comboRevenue = wx.ComboBox(revenueCard, choices=comboRevenueChoices, style=wx.CB_READONLY)
        self.comboRevenue.SetSelection(0)
        self.comboRevenue.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                         wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        self.txtRevenue = wx.TextCtrl(revenueCard, style=wx.TE_RIGHT)
        self.txtRevenue.SetHint("금액 입력 (숫자만)")
        self.txtRevenue.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                       wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        revenueSizer.Add(self.RadioRevenue, 0, wx.ALL, 10)
        revenueSizer.Add(self.comboRevenue, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        revenueSizer.Add(self.txtRevenue, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        revenueCard.SetSizer(revenueSizer)
        inputSizer.Add(revenueCard, 0, wx.EXPAND | wx.ALL, 8)
        
        # 지출 입력 카드
        expenseCard = self.CreateCard(inputPanel, "💳 지출")
        expenseSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.RadioExpense = wx.RadioButton(expenseCard, label="지출 항목 선택")
        self.RadioExpense.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                         wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        self.RadioExpense.SetForegroundColour(self.COLORS['danger'])
        
        comboExpenseChoices = ["상세내역 선택", "지출.식대", "지출.간식", "지출.여가생활", 
                              "지출.소모품", "지출.패션", "지출.가전", "지출.차량", 
                              "지출.공과금", "지출.보험", "지출.기타"]
        self.comboExpense = wx.ComboBox(expenseCard, choices=comboExpenseChoices, style=wx.CB_READONLY)
        self.comboExpense.SetSelection(0)
        self.comboExpense.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                         wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        self.txtExpense = wx.TextCtrl(expenseCard, style=wx.TE_RIGHT)
        self.txtExpense.SetHint("금액 입력 (숫자만)")
        self.txtExpense.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                       wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        expenseSizer.Add(self.RadioExpense, 0, wx.ALL, 10)
        expenseSizer.Add(self.comboExpense, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        expenseSizer.Add(self.txtExpense, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        expenseCard.SetSizer(expenseSizer)
        inputSizer.Add(expenseCard, 0, wx.EXPAND | wx.ALL, 8)
        
        # 비고 입력 카드
        remarkCard = self.CreateCard(inputPanel, "📝 비고")
        remarkSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.txtRemark = wx.TextCtrl(remarkCard, style=wx.TE_MULTILINE)
        self.txtRemark.SetHint("메모를 입력하세요")
        self.txtRemark.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                      wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        self.txtRemark.SetMinSize((-1, 80))
        
        remarkSizer.Add(self.txtRemark, 1, wx.EXPAND | wx.ALL, 10)
        
        remarkCard.SetSizer(remarkSizer)
        inputSizer.Add(remarkCard, 0, wx.EXPAND | wx.ALL, 8)
        
        # 버튼 영역
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btnInsert = self.CreateStyledButton(inputPanel, "➕ 추가", self.COLORS['success'])
        self.btnUpdate = self.CreateStyledButton(inputPanel, "✏️ 수정", self.COLORS['primary'])
        self.btnDelete = self.CreateStyledButton(inputPanel, "🗑️ 삭제", self.COLORS['danger'])
        self.btnClear = self.CreateStyledButton(inputPanel, "🔄 초기화", self.COLORS['text_secondary'])
        
        buttonSizer.Add(self.btnInsert, 1, wx.ALL, 5)
        buttonSizer.Add(self.btnUpdate, 1, wx.ALL, 5)
        buttonSizer.Add(self.btnDelete, 1, wx.ALL, 5)
        buttonSizer.Add(self.btnClear, 1, wx.ALL, 5)
        
        inputSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 8)
        
        inputPanel.SetSizer(inputSizer)
        return inputPanel
    
    def CreateDisplayPanel(self):
        """오른쪽 디스플레이 패널 생성"""
        displayPanel = wx.Panel(self.mainPanel)
        displayPanel.SetBackgroundColour(self.COLORS['background'])
        
        displaySizer = wx.BoxSizer(wx.VERTICAL)
        
        # 필터 및 조회 버튼
        filterCard = self.CreateCard(displayPanel, "🔍 데이터 조회")
        filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btnFind = self.CreateStyledButton(filterCard, "💵 수입만", self.COLORS['success'])
        self.btnSelectAll = self.CreateStyledButton(filterCard, "📋 전체조회", self.COLORS['primary'])
        self.btnPaint = self.CreateStyledButton(filterCard, "📊 그래프", self.COLORS['warning'])
        self.btnErase = self.CreateStyledButton(filterCard, "🗑️ 그래프삭제", self.COLORS['text_secondary'])
        
        filterSizer.Add(self.btnFind, 1, wx.ALL, 5)
        filterSizer.Add(self.btnSelectAll, 1, wx.ALL, 5)
        filterSizer.Add(self.btnPaint, 1, wx.ALL, 5)
        filterSizer.Add(self.btnErase, 1, wx.ALL, 5)
        
        filterCard.SetSizer(filterSizer)
        displaySizer.Add(filterCard, 0, wx.EXPAND | wx.ALL, 8)
        
        # 거래 내역 리스트
        listCard = self.CreateCard(displayPanel, "📝 거래 내역")
        listSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.list = wx.ListCtrl(listCard, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.InsertColumn(0, "거래번호", width=80)
        self.list.InsertColumn(1, "날짜", width=100)
        self.list.InsertColumn(2, "구분", width=60)
        self.list.InsertColumn(3, "상세내역", width=120)
        self.list.InsertColumn(4, "수입", width=100)
        self.list.InsertColumn(5, "지출", width=100)
        self.list.InsertColumn(6, "비고", width=200)
        
        listFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                          wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕")
        self.list.SetFont(listFont)
        
        listSizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 10)
        
        listCard.SetSizer(listSizer)
        displaySizer.Add(listCard, 1, wx.EXPAND | wx.ALL, 8)
        
        # 그래프 영역
        graphCard = self.CreateCard(displayPanel, "📊 지출 현황 그래프")
        graphSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.graphPanel = Barchart(graphCard)
        self.graphPanel.SetMinSize((-1, 200))
        graphSizer.Add(self.graphPanel, 1, wx.EXPAND | wx.ALL, 10)
        
        graphCard.SetSizer(graphSizer)
        displaySizer.Add(graphCard, 0, wx.EXPAND | wx.ALL, 8)
        
        # 작업 이력
        historyCard = self.CreateCard(displayPanel, "📋 작업 이력")
        historySizer = wx.BoxSizer(wx.VERTICAL)
        
        self.txtWorkHistory = wx.TextCtrl(historyCard, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.txtWorkHistory.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, 
                                           wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        self.txtWorkHistory.SetMinSize((-1, 100))
        
        historySizer.Add(self.txtWorkHistory, 1, wx.EXPAND | wx.ALL, 10)
        
        historyCard.SetSizer(historySizer)
        displaySizer.Add(historyCard, 0, wx.EXPAND | wx.ALL, 8)
        
        displayPanel.SetSizer(displaySizer)
        return displayPanel
    
    def CreateCard(self, parent, title):
        """카드 스타일 패널 생성"""
        card = wx.Panel(parent)
        card.SetBackgroundColour(self.COLORS['card'])
        
        # 타이틀
        titleText = wx.StaticText(card, label=title)
        titleFont = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                           wx.FONTWEIGHT_BOLD, faceName="맑은 고딕")
        titleText.SetFont(titleFont)
        titleText.SetForegroundColour(self.COLORS['text_primary'])
        
        return card
    
    def CreateStyledButton(self, parent, label, color):
        """스타일이 적용된 버튼 생성"""
        btn = wx.Button(parent, label=label)
        btn.SetBackgroundColour(color)
        btn.SetForegroundColour('#FFFFFF')
        btnFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                         wx.FONTWEIGHT_BOLD, faceName="맑은 고딕")
        btn.SetFont(btnFont)
        btn.SetMinSize((-1, 35))
        return btn
    
    def BindEvents(self):
        """이벤트 바인딩"""
        self.btnMonthlySum.Bind(wx.EVT_BUTTON, self.OnMonthlySum)
        self.btnInsert.Bind(wx.EVT_BUTTON, self.OnInsert)
        self.btnUpdate.Bind(wx.EVT_BUTTON, self.OnUpdate)
        self.btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
        self.btnClear.Bind(wx.EVT_BUTTON, self.OnClear)
        self.btnFind.Bind(wx.EVT_BUTTON, self.OnFind)
        self.btnSelectAll.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        self.btnPaint.Bind(wx.EVT_BUTTON, self.OnPaint)
        self.btnErase.Bind(wx.EVT_BUTTON, self.OnErase)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelected)
        
        # 금액 입력 시 자동 포맷팅
        self.txtRevenue.Bind(wx.EVT_TEXT, self.OnAmountInput)
        self.txtExpense.Bind(wx.EVT_TEXT, self.OnAmountInput)
        
        # 라디오 버튼 이벤트
        self.RadioRevenue.Bind(wx.EVT_RADIOBUTTON, self.OnRadioChange)
        self.RadioExpense.Bind(wx.EVT_RADIOBUTTON, self.OnRadioChange)
    
    def LoadInitialData(self):
        """초기 데이터 로드"""
        self.txtWorkHistory.AppendText(" 🎉 스마트 가계부 v3.0을 시작합니다.\n")
        self.txtWorkHistory.AppendText(" 💡 Ctrl+F: 검색 | Ctrl+T: 통계 | Ctrl+B: 예산\n")
        wx.CallAfter(self.OnSelectAll, None)
    
    def OnRadioChange(self, event):
        """라디오 버튼 변경 시 다른 쪽 초기화"""
        if self.RadioRevenue.GetValue():
            self.comboExpense.SetSelection(0)
            self.txtExpense.SetValue("")
        elif self.RadioExpense.GetValue():
            self.comboRevenue.SetSelection(0)
            self.txtRevenue.SetValue("")
    
    def OnAmountInput(self, event):
        """금액 입력 시 자동 포맷팅 (콤마 추가)"""
        ctrl = event.GetEventObject()
        value = ctrl.GetValue()
        
        # 숫자와 콤마만 허용
        cleaned = re.sub(r'[^\d,]', '', value)
        
        # 콤마 제거 후 다시 추가
        if cleaned:
            try:
                number = int(cleaned.replace(',', ''))
                formatted = f"{number:,}"
                
                # 값이 변경되었을 때만 업데이트 (무한 루프 방지)
                if formatted != value:
                    insertion_point = ctrl.GetInsertionPoint()
                    ctrl.ChangeValue(formatted)
                    # 커서 위치 조정
                    ctrl.SetInsertionPoint(min(insertion_point, len(formatted)))
            except ValueError:
                pass
    
    def ValidateInput(self):
        """입력 검증"""
        # 구분 선택 확인
        if not self.RadioRevenue.GetValue() and not self.RadioExpense.GetValue():
            wx.MessageBox("수입 또는 지출을 선택해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
            return False
        
        # 상세내역 선택 확인
        if self.RadioRevenue.GetValue():
            if self.comboRevenue.GetSelection() == 0:
                wx.MessageBox("수입 상세내역을 선택해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return False
            if not self.txtRevenue.GetValue():
                wx.MessageBox("수입 금액을 입력해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return False
        
        if self.RadioExpense.GetValue():
            if self.comboExpense.GetSelection() == 0:
                wx.MessageBox("지출 상세내역을 선택해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return False
            if not self.txtExpense.GetValue():
                wx.MessageBox("지출 금액을 입력해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return False
        
        # 금액 검증
        revenue = self.txtRevenue.GetValue().replace(',', '')
        expense = self.txtExpense.GetValue().replace(',', '')
        
        if revenue:
            try:
                amount = float(revenue)
                if amount > 1000000000:  # 10억 이상
                    result = wx.MessageBox(
                        f"입력하신 금액이 {amount:,.0f}원입니다.\n이 금액이 맞습니까?",
                        "금액 확인",
                        wx.YES_NO | wx.ICON_QUESTION
                    )
                    if result != wx.YES:
                        return False
            except ValueError:
                wx.MessageBox("올바른 금액을 입력해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return False
        
        if expense:
            try:
                amount = float(expense)
                if amount > 1000000000:  # 10억 이상
                    result = wx.MessageBox(
                        f"입력하신 금액이 {amount:,.0f}원입니다.\n이 금액이 맞습니까?",
                        "금액 확인",
                        wx.YES_NO | wx.ICON_QUESTION
                    )
                    if result != wx.YES:
                        return False
            except ValueError:
                wx.MessageBox("올바른 금액을 입력해주세요.", "입력 오류", wx.OK | wx.ICON_WARNING)
                return False
        
        return True
    
    def OnMonthlySum(self, event):
        """월별 합계 조회"""
        month = self.cboMonth.GetValue()
        if not month or month == '데이터 없음':
            self.txtWorkHistory.AppendText(" ⚠️ 조회할 월을 선택해주세요.\n")
            return
        
        self.list.DeleteAllItems()
        rows = HL_CRUD.selectMonthlySum(month)
        
        for row in rows:
            self.list.InsertItem(0, str(row[0]))
            self.list.SetItem(0, 1, row[1])
            self.list.SetItem(0, 2, row[2])
            self.list.SetItem(0, 3, row[3])
            self.list.SetItem(0, 4, str(row[4]))
            self.list.SetItem(0, 5, str(row[5]))
            self.list.SetItem(0, 6, row[6])
        
        self.txtWorkHistory.AppendText(f" ✅ {month} 월별 합계 조회완료.\n")
        if event:
            event.Skip()
    
    def OnInsert(self, event):
        """거래 추가"""
        if not self.ValidateInput():
            return
        
        date = self.datePicker.GetValue().FormatISODate()
        
        section = ""
        if self.RadioRevenue.GetValue():
            section = '수입'
        elif self.RadioExpense.GetValue():
            section = '지출'
        
        title = ""
        if '수입' in self.comboRevenue.GetValue():
            title = self.comboRevenue.GetValue()
        elif '지출' in self.comboExpense.GetValue():
            title = self.comboExpense.GetValue()
        
        revenue = self.txtRevenue.GetValue().replace(',', '')
        expense = self.txtExpense.GetValue().replace(',', '')
        remark = self.txtRemark.GetValue()
        
        # 중복 거래 확인
        if self.CheckDuplicate(date, title, revenue if revenue else expense):
            result = wx.MessageBox(
                "동일한 날짜, 항목, 금액의 거래가 이미 존재합니다.\n추가하시겠습니까?",
                "중복 확인",
                wx.YES_NO | wx.ICON_QUESTION
            )
            if result != wx.YES:
                return
        
        HL_CRUD.insert((date, section, title, revenue, expense, remark))
        
        self.txtWorkHistory.AppendText(f" ✅ 거래내역 추가완료 - {section}/{title} {revenue or expense}원\n")
        
        self.OnSelectAll(event)
        self.OnClear(event)
    
    def CheckDuplicate(self, date, title, amount):
        """중복 거래 확인"""
        rows = HL_CRUD.selectAll()
        for row in rows:
            if (row[1] == date and row[3] == title and 
                (str(row[4]) == amount or str(row[5]) == amount)):
                return True
        return False
    
    def OnUpdate(self, event):
        """거래 수정"""
        idx = self.list.GetFirstSelected()
        if idx == -1:
            self.txtWorkHistory.AppendText(" ⚠️ 수정할 항목을 선택해주세요.\n")
            return
        
        if not self.ValidateInput():
            return
        
        serialNo = self.list.GetItem(idx, 0).GetText()
        date = self.datePicker.GetValue().FormatISODate()
        
        section = ""
        if self.RadioRevenue.GetValue():
            section = '수입'
        elif self.RadioExpense.GetValue():
            section = '지출'
        
        title = ""
        if '수입' in self.comboRevenue.GetValue():
            title = self.comboRevenue.GetValue()
        elif '지출' in self.comboExpense.GetValue():
            title = self.comboExpense.GetValue()
        
        revenue = self.txtRevenue.GetValue().replace(',', '')
        expense = self.txtExpense.GetValue().replace(',', '')
        remark = self.txtRemark.GetValue()
        
        HL_CRUD.update((date, section, title, revenue, expense, remark, serialNo))
        
        self.txtWorkHistory.AppendText(f" ✅ 거래내역 수정완료 - 거래번호: {serialNo}\n")
        
        self.OnSelectAll(event)
    
    def OnDelete(self, event):
        """거래 삭제"""
        idx = self.list.GetFirstSelected()
        if idx == -1:
            self.txtWorkHistory.AppendText(" ⚠️ 삭제할 항목을 선택해주세요.\n")
            return
        
        key = self.list.GetItem(idx, 0).GetText()
        
        # 삭제 확인
        result = wx.MessageBox(
            f"거래번호 {key}를 삭제하시겠습니까?",
            "삭제 확인",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if result == wx.YES:
            HL_CRUD.delete(key)
            self.txtWorkHistory.AppendText(f" ✅ 거래내역 삭제완료 - 거래번호: {key}\n")
            self.OnSelectAll(event)
    
    def OnClear(self, event):
        """화면 초기화"""
        self.datePicker.SetValue(wx.DateTime.Today())
        self.RadioRevenue.SetValue(False)
        self.RadioExpense.SetValue(False)
        self.comboRevenue.SetSelection(0)
        self.comboExpense.SetSelection(0)
        self.txtRevenue.SetValue("")
        self.txtExpense.SetValue("")
        self.txtRemark.SetValue("")
        
        self.txtWorkHistory.AppendText(" 🔄 입력 화면 초기화 완료.\n")
        
        if event:
            event.Skip()
    
    def OnFind(self, event):
        """수입만 조회"""
        self.list.DeleteAllItems()
        rows = HL_CRUD.selectAll()
        
        count = 0
        for row in rows:
            if row[2] == '수입':
                idx = self.list.InsertItem(0, str(row[0]))
                self.list.SetItem(idx, 1, row[1])
                self.list.SetItem(idx, 2, row[2])
                self.list.SetItem(idx, 3, row[3])
                self.list.SetItem(idx, 4, f"{float(row[4]):,.0f}" if row[4] else "0")
                self.list.SetItem(idx, 5, f"{float(row[5]):,.0f}" if row[5] else "0")
                self.list.SetItem(idx, 6, row[6])
                count += 1
        
        self.txtWorkHistory.AppendText(f" ✅ 수입 항목 조회완료 - {count}건\n")
        if event:
            event.Skip()
    
    def OnSelectAll(self, event):
        """전체 조회"""
        self.list.DeleteAllItems()
        rows = HL_CRUD.selectAll()
        
        for row in rows:
            idx = self.list.InsertItem(0, str(row[0]))
            self.list.SetItem(idx, 1, row[1])
            self.list.SetItem(idx, 2, row[2])
            self.list.SetItem(idx, 3, row[3])
            # 금액에 콤마 추가
            self.list.SetItem(idx, 4, f"{float(row[4]):,.0f}" if row[4] else "0")
            self.list.SetItem(idx, 5, f"{float(row[5]):,.0f}" if row[5] else "0")
            self.list.SetItem(idx, 6, row[6])
        
        self.txtWorkHistory.AppendText(f" ✅ 전체 거래 조회완료 - {len(rows)}건\n")
        if event:
            event.Skip()
    
    def OnSelected(self, event):
        """리스트 항목 선택 시"""
        idx = event.GetIndex()
        
        date_str = self.list.GetItem(idx, 1).GetText()
        y, m, d = map(int, date_str.split('-'))
        self.datePicker.SetValue(wx.DateTime.FromDMY(d, m - 1, y))
        
        if self.list.GetItem(idx, 2).GetText() == '수입':
            self.RadioRevenue.SetValue(True)
            self.RadioExpense.SetValue(False)
        elif self.list.GetItem(idx, 2).GetText() == '지출':
            self.RadioExpense.SetValue(True)
            self.RadioRevenue.SetValue(False)
        
        if '수입' in self.list.GetItem(idx, 3).GetText():
            self.comboRevenue.SetValue(self.list.GetItem(idx, 3).GetText())
            self.comboExpense.SetSelection(0)
        elif '지출' in self.list.GetItem(idx, 3).GetText():
            self.comboExpense.SetValue(self.list.GetItem(idx, 3).GetText())
            self.comboRevenue.SetSelection(0)
        
        # 콤마 제거한 값으로 설정
        revenue = self.list.GetItem(idx, 4).GetText().replace(',', '')
        expense = self.list.GetItem(idx, 5).GetText().replace(',', '')
        
        self.txtRevenue.SetValue(revenue)
        self.txtExpense.SetValue(expense)
        self.txtRemark.SetValue(self.list.GetItem(idx, 6).GetText())
        
        event.Skip()
    
    def OnPaint(self, event):
        """그래프 그리기 (수정된 로직)"""
        self.OnSelectAll(event)
        
        # 지출 데이터만 수집
        expense_data = defaultdict(float)
        
        rows = HL_CRUD.selectAll()
        for row in rows:
            if len(row) >= 6 and row[2] == '지출':  # 지출만
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
