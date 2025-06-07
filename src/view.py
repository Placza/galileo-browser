import tkinter as tk
import tkinter.ttk as ttk

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

        self.render()
    def mouse_wheel(self, event):
        print(event.delta)

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

    def layout(self, text):
        self.display_list.clear()
        cursor_x, cursor_y = self.HSTEP, self.VSTEP
        for c in text:
            self.display_list.append((cursor_x, cursor_y, c))
            cursor_x += self.HSTEP
            if cursor_x >= self.width - 7 or c == '\n':
                cursor_x = self.HSTEP
                cursor_y += self.VSTEP
        if len(self.display_list):
            x, self.page_size, temp = self.display_list[len(self.display_list) - 1]

    def render(self):
        self.canvas.delete('all')
        self.layout(self.content)
        
        self.update_scrollbar()
        top, bottom = 0, 0
        for x, y, c in self.display_list:
            if y > self.scroll + self.height: continue
            if y + self.VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)