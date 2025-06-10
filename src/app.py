
import tkinter as tk
import tkinter.ttk as ttk
from . import network as network
from . import view as view

class Browser:
    def __init__(self, width, height):
        self.root = tk.Tk()
        self.root.minsize(width=200, height=200)
        self.root.title('My browser')
        self.root.bind_all('<Button-1>', lambda event: event.widget.focus_set())
        self.root.geometry('{}x{}'.format(width, height))

        self.view = view.View(self.root, width, height - 100)

    def run(self):
        self.renderUI()
        tk.mainloop()

    def on_entry_click(self, event, addr, default_text):
        if addr.get() == default_text:
            addr.delete(0, 'end')
            addr.config(fg='black')
    
    def on_focusout(self, event, addr, default_text):
        if addr.get() == '':
            addr.insert(0, default_text)
            addr.config(fg='gray')

    def search_web(self, addr, default_text):
        if addr.get() != default_text:
            url = network.URL(addr.get())
            self.view.content = network.Socket(url).load_content()
            self.view.scroll = 0
            self.view.load()

    def select_all(self, event, addr):
        addr.focus_set()
        addr.select_range(0, 'end')
        return 'break'
        
    def renderUI(self):
        header = tk.Frame(height=100, background='gray70')
        header.pack(fill='x', side='top')
        header.pack_propagate(False)

        header_bottom = tk.Frame(header, height=50, background='gray70')
        header_bottom.pack(side='bottom', fill='x')

        header_top = tk.Frame(header, height=50, background='gray70')
        header_top.pack(side='top', fill='x')

        addr = tk.Entry(header_bottom, fg='gray')
        default_text = 'Start searching the web by writing an address'
        addr.insert(0, default_text)
        addr.bind('<FocusIn>', lambda event : self.on_entry_click(event, addr, default_text))
        addr.bind('<FocusOut>', lambda event : self.on_focusout(event, addr, default_text))
        addr.bind('<Control-a>', lambda event : self.select_all(event, addr))
        addr.bind('<Return>', lambda event : self.search_web(addr, default_text))

        self.search_icon = tk.PhotoImage(file='assets/magnifier.png')
        search = tk.Button(header_bottom, image=self.search_icon, command=lambda : self.search_web(addr, default_text))
        search.pack(side='left', padx=(100, 0), pady=10)
        
        addr.pack(side='left', fill='x', expand=True, padx=(0, 10), pady=10)

        self.view.create_view()