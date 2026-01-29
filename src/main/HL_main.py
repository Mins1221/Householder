# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## MODIFIED - Enhanced with modern theme and styling
###########################################################################

import wx
import wx.xrc
import wx.adv
from . import HL_CRUD



from main import HL_CRUD
from main.barChart import Barchart


###########################################################################
## Class MyFrame - Modern Theme Version
###########################################################################
class MyFrame ( wx.Frame ):
    
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"💰 스마트 가계부", pos = wx.DefaultPosition, size = wx.Size( 1360,768 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        # 모던 컬러 테마 정의
        self.COLORS = {
            'background': '#FFFFFF',           # 깨끗한 화이트
            'secondary_bg': '#F8F9FA',         # 연한 그레이 배경
            'primary': '#4A90E2',              # 블루 (주요 액센트)
            'success': '#5CB85C',              # 그린 (수입)
            'danger': '#E74C3C',               # 레드 (지출)
            'text_primary': '#2C3E50',         # 진한 네이비 텍스트
            'text_secondary': '#7F8C8D',       # 중간 회색 텍스트
            'border': '#E1E8ED',               # 테두리 색상
            'card': '#FFFFFF',                 # 카드 배경
            'hover': '#E8F4F8'                 # 호버 효과
        }
        
        # 메인 패널 설정
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetBackgroundColour(self.COLORS['background'])
        
        # 전체 레이아웃
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 타이틀 바 (헤더)
        headerPanel = self.CreateHeaderPanel()
        mainSizer.Add(headerPanel, 0, wx.EXPAND|wx.ALL, 0)
        
        # 컨텐츠 영역
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 왼쪽: 입력 영역
        leftPanel = self.CreateInputPanel()
        contentSizer.Add(leftPanel, 0, wx.EXPAND|wx.ALL, 15)
        
        # 오른쪽: 리스트 및 그래프 영역
        rightPanel = self.CreateDisplayPanel()
        contentSizer.Add(rightPanel, 1, wx.EXPAND|wx.ALL, 15)
        
        mainSizer.Add(contentSizer, 1, wx.EXPAND)
        
        self.mainPanel.SetSizer(mainSizer)
        self.Layout()
        
        # 이벤트 바인딩
        self.BindEvents()
        
    def CreateHeaderPanel(self):
        """모던한 헤더 패널 생성"""
        headerPanel = wx.Panel(self.mainPanel)
        headerPanel.SetBackgroundColour(self.COLORS['primary'])
        headerPanel.SetMinSize((-1, 70))
        
        headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 타이틀
        titleText = wx.StaticText(headerPanel, label="💰 스마트 가계부")
        titleFont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="맑은 고딕")
        titleText.SetFont(titleFont)
        titleText.SetForegroundColour('#FFFFFF')
        
        headerSizer.Add(titleText, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 30)
        headerSizer.AddStretchSpacer()
        
        # 버전 정보
        versionText = wx.StaticText(headerPanel, label="v2.0")
        versionFont = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        versionText.SetFont(versionFont)
        versionText.SetForegroundColour('#BFD9F2')
        
        headerSizer.Add(versionText, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 30)
        
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
        self.datePicker.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        dateSizer.Add(self.datePicker, 0, wx.EXPAND|wx.ALL, 10)
        
        dateCard.SetSizer(dateSizer)
        inputSizer.Add(dateCard, 0, wx.EXPAND|wx.ALL, 8)
        
        # 월별 조회 카드
        monthCard = self.CreateCard(inputPanel, "📊 월별 조회")
        monthSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        months = HL_CRUD.selectMonthList()
        if not months:
            months = ['데이터 없음']
            
        self.cboMonth = wx.ComboBox(
            monthCard,
            choices=months,
            style=wx.CB_READONLY
        )
        self.cboMonth.SetSelection(0)
        self.cboMonth.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        self.btnMonthlySum = self.CreateStyledButton(monthCard, "조회", self.COLORS['primary'])
        
        monthSizer.Add(self.cboMonth, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)
        monthSizer.Add(self.btnMonthlySum, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)
        
        monthCard.SetSizer(monthSizer)
        inputSizer.Add(monthCard, 0, wx.EXPAND|wx.ALL, 8)
        
        # 수입 입력 카드
        revenueCard = self.CreateCard(inputPanel, "💵 수입")
        revenueSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.RadioRevenue = wx.RadioButton(revenueCard, label="수입 항목 선택")
        self.RadioRevenue.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        self.RadioRevenue.SetForegroundColour(self.COLORS['success'])
        
        comboRevenueChoices = ["상세내역 선택", "수입.급여", "수입.상여", "수입.이자", "수입.배당", "수입.사업", "수입.연금", "수입.기타"]
        self.comboRevenue = wx.ComboBox(revenueCard, choices=comboRevenueChoices, style=wx.CB_READONLY)
        self.comboRevenue.SetSelection(0)
        self.comboRevenue.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        self.txtRevenue = wx.TextCtrl(revenueCard, style=wx.TE_RIGHT)
        self.txtRevenue.SetHint("금액 입력")
        self.txtRevenue.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        revenueSizer.Add(self.RadioRevenue, 0, wx.ALL, 10)
        revenueSizer.Add(self.comboRevenue, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        revenueSizer.Add(self.txtRevenue, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        
        revenueCard.SetSizer(revenueSizer)
        inputSizer.Add(revenueCard, 0, wx.EXPAND|wx.ALL, 8)
        
        # 지출 입력 카드
        expenseCard = self.CreateCard(inputPanel, "💳 지출")
        expenseSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.RadioExpense = wx.RadioButton(expenseCard, label="지출 항목 선택")
        self.RadioExpense.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        self.RadioExpense.SetForegroundColour(self.COLORS['danger'])
        
        comboExpenseChoices = ["상세내역 선택", "지출.식대", "지출.간식", "지출.여가생활", "지출.소모품", "지출.패션", "지출.가전", "지출.차량", "지출.공과금", "지출.보험", "지출.기타"]
        self.comboExpense = wx.ComboBox(expenseCard, choices=comboExpenseChoices, style=wx.CB_READONLY)
        self.comboExpense.SetSelection(0)
        self.comboExpense.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        self.txtExpense = wx.TextCtrl(expenseCard, style=wx.TE_RIGHT)
        self.txtExpense.SetHint("금액 입력")
        self.txtExpense.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        
        expenseSizer.Add(self.RadioExpense, 0, wx.ALL, 10)
        expenseSizer.Add(self.comboExpense, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        expenseSizer.Add(self.txtExpense, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        
        expenseCard.SetSizer(expenseSizer)
        inputSizer.Add(expenseCard, 0, wx.EXPAND|wx.ALL, 8)
        
        # 비고 입력 카드
        remarkCard = self.CreateCard(inputPanel, "📝 비고")
        remarkSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.txtRemark = wx.TextCtrl(remarkCard, style=wx.TE_MULTILINE)
        self.txtRemark.SetHint("메모를 입력하세요")
        self.txtRemark.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        self.txtRemark.SetMinSize((-1, 80))
        
        remarkSizer.Add(self.txtRemark, 1, wx.EXPAND|wx.ALL, 10)
        
        remarkCard.SetSizer(remarkSizer)
        inputSizer.Add(remarkCard, 0, wx.EXPAND|wx.ALL, 8)
        
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
        
        inputSizer.Add(buttonSizer, 0, wx.EXPAND|wx.ALL, 8)
        
        inputPanel.SetSizer(inputSizer)
        return inputPanel
        
    def CreateDisplayPanel(self):
        """오른쪽 디스플레이 패널 생성"""
        displayPanel = wx.Panel(self.mainPanel)
        displayPanel.SetBackgroundColour(self.COLORS['background'])
        
        displaySizer = wx.BoxSizer(wx.VERTICAL)
        
        # 리스트 영역
        listCard = self.CreateCard(displayPanel, "📋 거래 내역")
        listSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 조회 버튼
        queryButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btnFind = self.CreateStyledButton(listCard, "수입만 조회", self.COLORS['success'])
        self.btnSelectAll = self.CreateStyledButton(listCard, "전체 조회", self.COLORS['primary'])
        
        queryButtonSizer.Add(self.btnFind, 0, wx.ALL, 5)
        queryButtonSizer.Add(self.btnSelectAll, 0, wx.ALL, 5)
        queryButtonSizer.AddStretchSpacer()
        
        listSizer.Add(queryButtonSizer, 0, wx.EXPAND|wx.ALL, 10)
        
        # 리스트 컨트롤
        self.list = wx.ListCtrl(listCard, style=wx.LC_REPORT|wx.BORDER_SIMPLE)
        self.list.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="맑은 고딕"))
        self.list.SetBackgroundColour('#FFFFFF')
        
        # 컬럼 설정
        self.list.InsertColumn(0, "거래번호", width=80)
        self.list.InsertColumn(1, "거래일자", width=100)
        self.list.InsertColumn(2, "구분", width=70)
        self.list.InsertColumn(3, "상세내역", width=120)
        self.list.InsertColumn(4, "수입", width=100)
        self.list.InsertColumn(5, "지출", width=100)
        self.list.InsertColumn(6, "비고", width=200)
        
        listSizer.Add(self.list, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        
        listCard.SetSizer(listSizer)
        displaySizer.Add(listCard, 1, wx.EXPAND|wx.ALL, 8)
        
        # 그래프 영역
        graphCard = self.CreateCard(displayPanel, "📊 지출 현황 그래프")
        graphSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 그래프 버튼
        graphButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btnPaint = self.CreateStyledButton(graphCard, "그래프 생성", self.COLORS['primary'])
        self.btnErase = self.CreateStyledButton(graphCard, "그래프 지우기", self.COLORS['text_secondary'])
        
        graphButtonSizer.Add(self.btnPaint, 0, wx.ALL, 5)
        graphButtonSizer.Add(self.btnErase, 0, wx.ALL, 5)
        graphButtonSizer.AddStretchSpacer()
        
        graphSizer.Add(graphButtonSizer, 0, wx.EXPAND|wx.ALL, 10)
        
        # 그래프 패널
        self.graphPanel = Barchart(graphCard)
        self.graphPanel.SetBackgroundColour('#FFFFFF')
        self.graphPanel.SetMinSize((-1, 200))
        
        graphSizer.Add(self.graphPanel, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        
        graphCard.SetSizer(graphSizer)
        displaySizer.Add(graphCard, 0, wx.EXPAND|wx.ALL, 8)
        
        # 작업 이력 영역
        historyCard = self.CreateCard(displayPanel, "📜 작업 이력")
        historySizer = wx.BoxSizer(wx.VERTICAL)
        
        self.txtWorkHistory = wx.TextCtrl(
            historyCard,
            style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP
        )
        self.txtWorkHistory.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.txtWorkHistory.SetBackgroundColour('#F8F9FA')
        self.txtWorkHistory.SetMinSize((-1, 120))
        
        historySizer.Add(self.txtWorkHistory, 1, wx.EXPAND|wx.ALL, 10)
        
        historyCard.SetSizer(historySizer)
        displaySizer.Add(historyCard, 0, wx.EXPAND|wx.ALL, 8)
        
        displayPanel.SetSizer(displaySizer)
        return displayPanel
        
    def CreateCard(self, parent, title):
        """카드 스타일 패널 생성"""
        card = wx.Panel(parent)
        card.SetBackgroundColour(self.COLORS['card'])
        
        cardSizer = wx.BoxSizer(wx.VERTICAL)
        
        # 카드 타이틀
        titleText = wx.StaticText(card, label=title)
        titleFont = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="맑은 고딕")
        titleText.SetFont(titleFont)
        titleText.SetForegroundColour(self.COLORS['text_primary'])
        
        cardSizer.Add(titleText, 0, wx.ALL, 12)
        
        # 구분선
        line = wx.Panel(card)
        line.SetBackgroundColour(self.COLORS['border'])
        line.SetMinSize((-1, 1))
        cardSizer.Add(line, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 12)
        
        card.SetSizer(cardSizer)
        return card
        
    def CreateStyledButton(self, parent, label, color):
        """스타일이 적용된 버튼 생성"""
        btn = wx.Button(parent, label=label)
        btn.SetBackgroundColour(color)
        btn.SetForegroundColour('#FFFFFF')
        btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="맑은 고딕"))
        btn.SetMinSize((100, 35))
        
        # 둥근 모서리 효과 (Windows에서는 제한적)
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
        
    # 기존 이벤트 핸들러들 (원본 코드의 메서드들)
    def OnMonthlySum( self, event ):
        self.list.DeleteAllItems()
        month = self.cboMonth.GetValue()
        rows = HL_CRUD.selectMonthlySum(month)
        
        if not rows:
            self.txtWorkHistory.AppendText(f" ⚠️ {month}에 해당하는 데이터가 없습니다.\n")
            return
        
        for row in rows:
            self.list.InsertItem(0, str(row[0]))
            self.list.SetItem(0, 1, row[1])
            self.list.SetItem(0, 2, row[2])
            self.list.SetItem(0, 3, row[3])
            self.list.SetItem(0, 4, str(row[4]))
            self.list.SetItem(0, 5, str(row[5]))
            self.list.SetItem(0, 6, row[6])
        
        self.txtWorkHistory.AppendText(f" ✅ {month} 월별 합계 조회완료.\n")
        event.Skip()
    
    def OnInsert( self, event ):
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
            
        revenue = self.txtRevenue.GetValue()
        expense = self.txtExpense.GetValue()
        remark = self.txtRemark.GetValue()
        
        HL_CRUD.insert((date, section, title, revenue, expense, remark))
        
        self.txtWorkHistory.AppendText(f" ✅ 거래내역 추가완료 - {section}/{title}\n")
        
        self.OnSelectAll(event)
        event.Skip()
    
    def OnUpdate( self, event ):
        idx = self.list.GetFirstSelected()
        if idx == -1:
            self.txtWorkHistory.AppendText(" ⚠️ 수정할 항목을 선택해주세요.\n")
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
            
        revenue = self.txtRevenue.GetValue()
        expense = self.txtExpense.GetValue()
        remark = self.txtRemark.GetValue()
        
        HL_CRUD.update((date, section, title, revenue, expense, remark, serialNo))
        
        self.txtWorkHistory.AppendText(f" ✅ 거래내역 수정완료 - 거래번호: {serialNo}\n")
        
        self.OnSelectAll(event)
        event.Skip()
    
    def OnDelete( self, event ):
        idx = self.list.GetFirstSelected()
        if idx == -1:
            self.txtWorkHistory.AppendText(" ⚠️ 삭제할 항목을 선택해주세요.\n")
            return
            
        key = self.list.GetItem(idx, 0).GetText()
        
        HL_CRUD.delete(key)
        
        self.txtWorkHistory.AppendText(f" ✅ 거래내역 삭제완료 - 거래번호: {key}\n")
        
        self.OnSelectAll(event)
        event.Skip()
    
    def OnClear( self, event ):
        self.datePicker.SetValue(wx.DateTime.Today())
        self.RadioRevenue.SetValue(False)
        self.RadioExpense.SetValue(False)
        self.comboRevenue.SetSelection(0)
        self.comboExpense.SetSelection(0)
        self.txtRevenue.SetValue("")
        self.txtExpense.SetValue("")
        self.txtRemark.SetValue("")
        
        self.txtWorkHistory.AppendText(" 🔄 화면 초기화 완료.\n")
        
        self.list.DeleteAllItems()
        event.Skip()
    
    def OnFind( self, event ):
        self.list.DeleteAllItems()
        rows = HL_CRUD.selectAll()
        
        count = 0
        for row in rows:
            if row[2] == '수입':
                self.list.InsertItem(0, str(row[0]))
                self.list.SetItem(0, 1, row[1])
                self.list.SetItem(0, 2, row[2])
                self.list.SetItem(0, 3, row[3])
                self.list.SetItem(0, 4, str(row[4]))
                self.list.SetItem(0, 5, str(row[5]))
                self.list.SetItem(0, 6, row[6])
                count += 1
                
        self.txtWorkHistory.AppendText(f" ✅ 수입 항목 조회완료 - {count}건\n")
        event.Skip()
        
    def OnSelectAll( self, event ):
        self.list.DeleteAllItems()
        rows = HL_CRUD.selectAll()
        
        for row in rows:
            self.list.InsertItem(0, str(row[0]))
            self.list.SetItem(0, 1, row[1])
            self.list.SetItem(0, 2, row[2])
            self.list.SetItem(0, 3, row[3])
            self.list.SetItem(0, 4, str(row[4]))
            self.list.SetItem(0, 5, str(row[5]))
            self.list.SetItem(0, 6, row[6])

        self.txtWorkHistory.AppendText(f" ✅ 전체 거래 조회완료 - {len(rows)}건\n")
        event.Skip()
 
    def OnSelected( self, event ):
        idx = event.GetIndex()
        
        date_str = self.list.GetItem(idx, 1).GetText()
        y, m, d = map(int, date_str.split('-'))
        self.datePicker.SetValue(wx.DateTime.FromDMY(d, m-1, y))
        
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
            
        self.txtRevenue.SetValue(self.list.GetItem(idx, 4).GetText())
        self.txtExpense.SetValue(self.list.GetItem(idx, 5).GetText())
        self.txtRemark.SetValue(self.list.GetItem(idx, 6).GetText())
        
        event.Skip()
        
    def OnPaint( self, event ):
        self.OnSelectAll(event)
                
        i = 0
        getTitle = []
        getExpense = []
        
        while i < self.list.GetItemCount():
            x = int(self.list.GetItem(i, 5).GetText())
            getExpense.append(x/1000)
            
            for b in getExpense:
                if b == 0.0 or 0:
                    getExpense.remove(b)

            y = self.list.GetItem(i, 3).GetText()
            getTitle.append(y)
            
            revTitle = ["수입.급여", "수입.상여", "수입.이자", "수입.배당", "수입.사업", "수입.연금", "수입.기타"]
            
            for a in getTitle:
                if a in revTitle:
                    getTitle.remove(a)
                    
            getExpDict = {}
            
            for v, k in enumerate(getTitle):
                val = getExpense[v]
                
                if k in getExpDict:
                    getExpDict[k] += val
                else:
                    getExpDict[k] = val
                        
            i = i + 1
            
            self.graphPanel.SetData(getExpDict)

        self.graphPanel.SetBackgroundColour('#FFFFFF')
        event.Skip()
        
        self.txtWorkHistory.AppendText(" 📊 지출현황 그래프 생성완료.\n")
        
    def OnErase( self, event ):
        self.graphPanel.Destroy()
        self.graphPanel = Barchart(self.GetParent())
        self.txtWorkHistory.AppendText(" 🗑️ 그래프 지우기 완료.\n")
        event.Skip()
    
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(parent=None)
    frame.Show()
    
    app.MainLoop()
