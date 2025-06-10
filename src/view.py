import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font
from . import htmlparser as htmlp

class View:
    def __init__(self, root, width, height):
        self.root = root
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

    def load(self):
        if self.content:
            parser = htmlp.HTMLParser(self.content)
            self.nodes = parser.parse()
            self.layout = Layout(self.nodes, self.width, self.height)
            self.display_list = self.layout.display_list
            self.page_size = self.layout.page_size
            self.render()  

    def resize(self, event):
        self.height = event.height
        self.width = event.width
        if self.page_size - self.height <= self.scroll:
            self.scroll = max(0, min(self.scroll, self.page_size - self.height))
        self.load()

    def scrolldown(self, event):
        if self.page_size - self.height > self.scroll:
            self.scroll = max(0, min(self.scroll + self.SCROLL_STEP, self.page_size - self.height))
            self.render()

    def scrollup(self, event):
        if self.scroll >= 0:
            self.scroll = max(0, min(self.scroll - self.SCROLL_STEP, self.page_size - self.height))
            self.render()

    def update_scrollbar(self):
        if self.page_size <= self.height:
            self.scrollbar.set(0, 1)
        else:
            delta = self.height / self.page_size
            scroll_range = 1 - delta
            scrollbar_start = scroll_range * (self.scroll / (self.page_size - self.height))
            scrollbar_end = scrollbar_start + delta
            self.scrollbar.set(scrollbar_start, min(scrollbar_end, 1.0))

    def scrollbar_move(self, *args):
        scrollbar_start, scrollbar_end = self.scrollbar.get()
        delta = scrollbar_end - scrollbar_start
        if args[0] == 'moveto':
            scrollbar_start = min(float(args[1]), 1 - delta)
            scrollbar_end = max(scrollbar_start + delta, delta)
            self.scrollbar.set(scrollbar_start, scrollbar_end)

        elif args[0] == 'scroll':
            scrollbar_start = min(scrollbar_start + float(args[1]) * 
                                  (self.SCROLL_STEP / self.page_size), 1 - delta)
            scrollbar_end = max(scrollbar_start + delta, delta)
            self.scrollbar.set(scrollbar_start, scrollbar_end)

        self.scroll = (scrollbar_start / 1) * (self.page_size)
        self.scroll = max(0, min(self.scroll, self.page_size - self.height))
        self.render()
 
    def create_view(self):
        container = tk.Frame(self.root)
        container.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(container)
        self.canvas.configure(background='white')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.bind('<Configure>', lambda event: self.resize(event))
        self.canvas.bind('<Down>', lambda event : self.scrolldown(event))
        self.canvas.bind('<Up>', lambda event : self.scrollup(event))
        self.canvas.bind('<Button-4>', lambda event : self.scrollup(event))
        self.canvas.bind('<Button-5>', lambda event : self.scrolldown(event))
        
        self.scrollbar = tk.Scrollbar(container)
        self.scrollbar.configure(orient='vertical', width=8, command=self.scrollbar_move)
        self.scrollbar.pack(side='right', fill='y', padx=(0, 2), pady=5)
        self.scrollbar.set(0, 0)

    def render(self):
        self.canvas.delete('all')
        self.update_scrollbar()
        for x, y, c, font in self.display_list:
            if y > self.scroll + self.height: continue
            if y + self.VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c, anchor='nw', font=font)

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
        if self.display_list:
            a, self.page_size, b, c = self.display_list[-1]

    def get_font(self, size, weight, style):
        key = (size, weight, style)
        if key not in self.fonts:
            font = tkinter.font.Font(size=size, weight=weight, slant=style)
            label = tkinter.Label(font=font)
            self.fonts[key] = (font, label)
        return self.fonts[key][0]

    def flush(self, align = 'left'):
        if not self.line: return
        metrics = [font.metrics() for x, word, font, placement in self.line]
        max_ascent = max([metric['ascent'] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        line_center = sum(x[0] for x in self.line) / 2
        for x, word, font, placement in self.line:
            y = baseline - font.metrics('ascent') - placement
            if align == 'center' : x += self.width / 2 - line_center / 2 
            self.display_list.append((x, y, word, font))
        max_descent = max([metric['descent'] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = self.HSTEP
        self.line = []

    def word(self, word):
        font = self.get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > self.width - self.HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font, self.placement))
        self.cursor_x += w + font.measure(' ')

    def open_tag(self, tag):
        if tag == 'i':
            self.style = 'italic'
        elif tag == 'b':
            self.style = 'bold'
        elif tag == 'small':
            self.size -= 2
        elif tag == 'big':
            self.size += 4
        elif tag == 'br':
            self.flush()
        elif tag == 'h1':
            self.align = 'center'
            self.size += 5
        elif tag == 'sup':
            self.size = round(self.size / 2) # change later so that the resize works for odd numbers too
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
            if self.align == 'center' : self.size -= 5
            self.align = 'left'
        elif tag == 'title':
            self.flush()
        elif tag == 'sup':
            self.placement -= self.size
            self.size *= 2

    def recurse(self, tree):
        if isinstance(tree, htmlp.Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)
  
        
        