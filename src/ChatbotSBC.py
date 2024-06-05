import tkinter as tk
import json
import userInterface.UserInterface as ui

if __name__ == "__main__": 
    with open('data/chats.json', 'r', encoding='utf-8') as f:
        chats = json.load(f)
    
    # Initialize ui
    root = tk.Tk()
    gui = ui.ChatGUI(root, chats)
    root.mainloop()
