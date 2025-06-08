import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

class View:
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
        self.display_list = []
        self.HSTEP = 13
        self.VSTEP = 18
        self.scroll = 0
        self.SCROLL_STEP = 50
        self.page_size = 0
        self.layout = None

    def load(self, text):
        self.scroll = 0
        tokens = self.lex(text)
        self.layout = Layout(tokens, self.width, self.height)
        self.display_list = self.layout.display_list
        self.page_size = self.layout.page_size
        self.render()  

    def lex(self, body):
        out = []
        buffer = ''
        in_tag = False
        for c in body:
            if c == '<':
                in_tag = True
                if buffer: out.append(Text(buffer))
                buffer = ''
            elif c == '>':
                in_tag = False
                out.append(Tag(buffer))
                buffer = ''
            else:
                buffer += c
        if not in_tag and buffer:
            out.append(Text(buffer))
        return out

    def resize(self, event):
        self.height = event.height
        self.width = event.width
        if self.page_size - self.height <= self.scroll:
            self.scroll = max(0, min(self.scroll, self.page_size - self.height))

        self.render()

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
    def __init__(self, tokens, width, height):
        self.display_list = []
        self.width = width
        self.height = height
        self.HSTEP = 13
        self.VSTEP = 18
        self.cursor_x = self.HSTEP
        self.cursor_y = self.VSTEP
        self.weight = 'normal'
        self.style = 'roman'
        self.size = 12
        for tok in tokens:
            self.token(tok)
        t1, self.page_size, t2, t3 = self.display_list[len(self.display_list) - 1]

    def word(self, word):
        font = tkinter.font.Font(
            size = self.size,
            weight=self.weight,
            slant=self.style
        )
        w = font.measure(word)
        self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.cursor_x += w + font.measure(' ')
        if self.cursor_x + w > self.width - self.HSTEP:
            self.cursor_y += font.metrics('linespace') * 1.25
            self.cursor_x = self.HSTEP

    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        elif tok.tag == 'i':
            self.style = 'italic'
        elif tok.tag == '/i':
            self.style = 'roman'
        elif tok.tag == 'b':
            self.weight = 'bold'
        elif tok.tag == '/b':
            self.weight = 'normal'
        elif tok.tag == 'small':
            self.size -= 2
        elif tok.tag == '/small':
            self.size += 2
        elif tok.tag == 'big':
            self.size += 4
        elif tok.tag == '/big':
            self.size -= 4
        
        