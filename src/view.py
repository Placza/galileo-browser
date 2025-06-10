from PySide6.QtWidgets import QWidget, QScrollBar, QHBoxLayout
from PySide6.QtGui import QPainter, QFont, QFontMetrics, QColor
from PySide6.QtCore import Qt
from . import htmlparser as htmlp

class View(QWidget):
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        
        self.content = ''
        self.display_list = []
        self.HSTEP = 13
        self.VSTEP = 18
        self.scroll = 0
        self.SCROLL_STEP = 50
        self.page_size = 0
        self.layout = None
        self.nodes = None
        
        # Create vertical scrollbar
        self.scrollbar = QScrollBar(Qt.Vertical, self)
        self.scrollbar.valueChanged.connect(self.scrollbar_move)

        # Create horizontal layout so we can put scrollbar on the right side with stretch
        layout = QHBoxLayout(self)
        self.setStyleSheet('background-color: white;')
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.scrollbar)
        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.white)
        
        painter.setPen(QColor(0, 0, 0))  
                
        for x, y, c, font in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + self.VSTEP < self.scroll:
                continue
            painter.setFont(font)
            painter.drawText(x, y - self.scroll, c)

    def load(self, content):
        if content:
            parser = htmlp.HTMLParser(content)
            self.nodes = parser.parse()
            self.layout = Layout(self.nodes, self.width, self.height)
            self.display_list = self.layout.display_list
            self.page_size = self.layout.page_size
            self.render()

    def resizeEvent(self, event):  
        self.height = event.size().height()
        self.width = event.size().width()
        
        if self.layout and self.page_size > 0:
            if self.page_size - self.height <= self.scroll:
                self.scroll = max(0, min(self.scroll, self.page_size - self.height))
            if self.nodes:
                self.layout = Layout(self.nodes, self.width, self.height)
                self.display_list = self.layout.display_list
                self.page_size = self.layout.page_size
                self.render()

    def update_scrollbar(self):
        max_scroll = max(0, self.page_size - self.height)
        self.scrollbar.setMaximum(max_scroll)
        self.scrollbar.setPageStep(self.height)
        self.scrollbar.setValue(self.scroll)

    def scrollbar_move(self, value):
        self.scroll = value
        self.update()
 
    def render(self):
        self.update_scrollbar()
        self.update()

class Layout:
    def __init__(self, nodes, width, height):
        self.display_list = []
        self.line = []
        self.fonts = {}
        self.width = width
        self.height = height
        self.HSTEP = 13
        self.VSTEP = 18
        self.cursor_x = self.HSTEP
        self.cursor_y = self.VSTEP
        self.weight = 'normal'
        self.style = 'roman'
        self.align = 'left'
        self.placement = 0
        self.size = 12
        
        self.recurse(nodes)
        self.flush()  
        
        if self.display_list:
            self.page_size = max([y for x, y, c, font in self.display_list]) + self.VSTEP
        else:
            self.page_size = 0

    def get_font(self, size, weight, style):
        key = (size, weight, style)
        if key not in self.fonts:
            font = QFont()
            font.setPointSize(size)
            if weight == 'bold':
                font.setWeight(QFont.Weight.Bold)
            else:
                font.setWeight(QFont.Weight.Normal)
            if style == 'italic':
                font.setItalic(True)
            else:
                font.setItalic(False)
            self.fonts[key] = font
        return self.fonts[key]

    def flush(self, align='left'):
        if not self.line: 
            return
            
        font_metrics_list = [QFontMetrics(font) for x, word, font, placement in self.line]
        max_ascent = max([fm.ascent() for fm in font_metrics_list])
        baseline = self.cursor_y + 1.25 * max_ascent
        
        # Ispravka za centriranje
        if align == 'center':
            line_width = sum([QFontMetrics(font).horizontalAdvance(word) for x, word, font, placement in self.line])
            offset = (self.width - line_width) / 2
        else:
            offset = 0
            
        for i, (x, word, font, placement) in enumerate(self.line):
            fm = font_metrics_list[i]
            y = baseline - fm.ascent() - placement
            final_x = x + offset if align == 'center' else x
            self.display_list.append((final_x, y, word, font))
            
        max_descent = max([fm.descent() for fm in font_metrics_list])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = self.HSTEP
        self.line = []

    def word(self, word):
        font = self.get_font(self.size, self.weight, self.style)
        font_metrics = QFontMetrics(font)
        w = font_metrics.horizontalAdvance(word)
        space_width = font_metrics.horizontalAdvance(' ')
        
        if self.cursor_x + w > self.width - self.HSTEP:
            self.flush()
        
        self.line.append((self.cursor_x, word, font, self.placement))
        self.cursor_x += w + space_width

    def open_tag(self, tag):
        if tag == 'i':
            self.style = 'italic'
        elif tag == 'b':
            self.weight = 'bold'
        elif tag == 'small':
            self.size -= 2
        elif tag == 'big':
            self.size += 4
        elif tag == 'br':
            self.flush()
        elif tag == 'h1':
            self.flush() 
            self.align = 'center'
            self.size += 5
        elif tag == 'sup':
            self.size = round(self.size / 2)
            self.placement += self.size

    def close_tag(self, tag):
        if tag == 'i':
            self.style = 'roman'
        elif tag == 'b':
            self.weight = 'normal'
        elif tag == 'small':
            self.size += 2
        elif tag == 'big':
            self.size -= 4
        elif tag == 'br':
            self.flush()
        elif tag == 'p':
            self.flush()
            self.cursor_y += self.VSTEP
        elif tag == 'h1':
            self.flush(align=self.align)
            self.size -= 5
            self.align = 'left'
        elif tag == 'title':
            self.flush()
        elif tag == 'sup':
            self.placement -= self.size
            self.size *= 2

    def recurse(self, tree):
        if isinstance(tree, htmlp.Text):
            for word in tree.text.split():
                if word.strip():  
                    self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)