import tkinter as tk
import tkinter.font

if __name__ == '__main__':
    root = tk.Tk()
    font = tkinter.font.Font()
    s = input()
    for word in s.split():
        w = font.measure(word)
        print(w)
    print(2)