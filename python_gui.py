# from https://realpython.com/python-gui-tkinter/
import tkinter as tk
window = tk.Tk()
label = tk.Label(
    text="Hello, blah",
    fg="white",
    bg="black",
    width=10,
    height=10
    )
label.pack()

button = tk.Button(
    text="Click here!",
    width=25,
    height=5,
    bg="blue",
    fg="yellow",
    )
button.pack()

window.mainloop()
