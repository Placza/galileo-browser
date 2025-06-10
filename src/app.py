#The app file is for rendering the GUI and linking the browser's logic with it

import tkinter as tk
import tkinter.ttk as ttk
from . import network as network
from . import view as view

class Browser:
    def __init__(self, width, height):
        #Initialize the window
        self.root = tk.Tk()
        self.root.minsize(width=200, height=200)
        self.root.title('My browser')
        self.root.bind_all('<Button-1>', lambda event: event.widget.focus_set()) #Makes so that when any part of the GUI gets clicked, it gets focused
        self.root.geometry('{}x{}'.format(width, height))

        self.view = view.View(self.root, width, height - 100) #View is a canvas element that renders the website and contains elements relevante to that function

    #Runs the main loop
    def run(self):
        self.renderUI()
        tk.mainloop()

    #When the search bar is clicked, remove the default text and make it black
    def on_entry_click(self, event, addr, default_text):
        if addr.get() == default_text:
            addr.delete(0, 'end')
            addr.config(fg='black')
    
    #When the search bar isn't focused, set the default text and make it gray
    def on_focusout(self, event, addr, default_text):
        if addr.get() == '':
            addr.insert(0, default_text)
            addr.config(fg='gray')

    #Connects to the internet and loads the view's content
    def search_web(self, addr, default_text):
        if addr.get() != default_text:
            url = network.URL(addr.get())
            self.view.content = network.Socket(url).load_content()
            self.view.scroll = 0 #Make so that the view is put at top of the page
            self.view.load()

    #When the search bar is in focus and the user presses Ctrl+A, it selects the entire inputed text
    def select_all(self, event, addr):
        addr.focus_set()
        addr.select_range(0, 'end')
        return 'break'
        
    def renderUI(self):
        #The header: the gray panel at top
        #The header is devideed into two parts: header_bottom and header_top
        header = tk.Frame(height=100, background='gray70')
        header.pack(fill='x', side='top')
        header.pack_propagate(False)

        #Holds buttons
        header_bottom = tk.Frame(header, height=50, background='gray70')
        header_bottom.pack(side='bottom', fill='x')

        #Holds the search bar and search button
        header_top = tk.Frame(header, height=50, background='gray70')
        header_top.pack(side='top', fill='x')

        #The search bar in which you can write addresses
        addr = tk.Entry(header_bottom, fg='gray')
        default_text = 'Start searching the web by writing an address'
        addr.insert(0, default_text)
        addr.bind('<FocusIn>', lambda event : self.on_entry_click(event, addr, default_text))
        addr.bind('<FocusOut>', lambda event : self.on_focusout(event, addr, default_text))
        addr.bind('<Control-a>', lambda event : self.select_all(event, addr))
        addr.bind('<Return>', lambda event : self.search_web(addr, default_text))

        #The search button which executes the search_web method when clicked
        self.search_icon = tk.PhotoImage(file='assets/magnifier.png')
        search = tk.Button(header_bottom, image=self.search_icon, command=lambda : self.search_web(addr, default_text)) #Excecute the search_web if clicked
        search.pack(side='left', padx=(100, 0), pady=10)
        
        addr.pack(side='left', fill='x', expand=True, padx=(0, 10), pady=10)

        #This creates the view
        self.view.create_view()