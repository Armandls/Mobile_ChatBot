import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import procesing.SentenceInterpretation as sentence
from procesing.ResponseDevelopment import ResponseDevelopment as response
import json
import requests as req
from io import BytesIO

class MessageBubble(tk.Frame):
    def __init__(self, master, text, sender, **kwargs):
        super().__init__(master, **kwargs)
        self.sender = sender

        # If the user writes a message, this one will appear in blue color.
        if self.sender == "user":
            bg_color = "blue"
            fg_color = "white"
            anchor = "e" 
            image_path = r"data\user.png" 

        # If the bot writes a message, this one will appear in white color.
        else:
            bg_color = "white"
            fg_color = "black"
            anchor = "w" 
            image_path = r"data\logo.png"

        # Create a frame for the bubble and add the image and the text.
        self.bubble_frame = tk.Frame(self)
        self.bubble_frame.pack(padx=5, pady=2, anchor=anchor)

        image = Image.open(image_path)
        image.thumbnail((50, 50)) 
        photo = ImageTk.PhotoImage(image)
        
        self.image_label = tk.Label(self.bubble_frame, image=photo)
        self.image_label.image = photo 
        self.image_label.pack(side=tk.LEFT if self.sender == "bot" else tk.RIGHT) 
        
        self.label = tk.Label(self.bubble_frame, text=text, bg=bg_color, fg=fg_color, wraplength=1200, justify="left", font=("Roboto", 13))
        self.label.pack(ipadx=8 , padx=10, pady=5, anchor=anchor) 

class MessageBubblePhone(tk.Frame):
    def __init__(self, master, text, phoneImage, **kwargs):
        super().__init__(master, **kwargs)
        
        bg_color = "white"
        fg_color = "black"
        anchor = "w" 
        image_path = r"data\logo.png"
        
        # Create a frame for the bubble and add the image and the text.
        self.bubble_frame = tk.Frame(self)
        self.bubble_frame.pack(padx=5, pady=2, anchor=anchor)

        image = Image.open(image_path)
        image.thumbnail((50, 50)) 
        photo = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(self.bubble_frame, image=photo)
        self.image_label.image = photo 
        self.image_label.pack(side=tk.LEFT) 
        
        response = req.get(phoneImage)
        imgData = response.content
        img = Image.open(BytesIO(imgData))
        img.thumbnail((200, 200))
        self.imgTk = ImageTk.PhotoImage(img)
        
        self.label = tk.Label(self.bubble_frame, text=text, bg=bg_color, fg=fg_color, wraplength=1200, justify="left", font=("Roboto", 13))
        self.phone_label = tk.Label(self.bubble_frame, image=self.imgTk, bg=bg_color, fg=fg_color, wraplength=1200, justify="left", font=("Roboto", 13))        
        self.label.pack(ipadx=8 , padx=10, pady=5, anchor=anchor) 
        self.phone_label.pack(ipadx=8 , padx=10, pady=5, anchor=anchor) 
           
class ChatGUI:
    def __init__(self, master, chats):
        self.chats = chats
        self.firstMesage = True
        self.numChats = len(self.chats.get("chats")) + 1
        self.currentChat = - 1
        
        # Prepare the window and put the name of the chatbot.
        self.master = master
        self.response_developer = response(self)
        master.title("Ringo")

        # Load the logo and resize it.
        img = Image.open(r"data\logo.png")
        img = img.resize((100, 50)) 
        self.photo = ImageTk.PhotoImage(img)

        # Create the frames for the header, the main window, the menu, the chat and the input.
        self.header_frame = tk.Frame(master)
        self.header_frame.pack(fill=tk.X)

        self.header_label = tk.Label(self.header_frame, image=self.photo)
        self.header_label.pack(fill=tk.X)

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.menu_frame = tk.Frame(self.main_frame, width=200, bg="lightgrey")
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.chat_frame = tk.Frame(self.main_frame)
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create the chat window with the conversation and the input.
        self.open_button_text = tk.StringVar()
        self.open_button_text.set("Close sidebar")
        self.open_button = tk.Button(self.chat_frame, textvariable=self.open_button_text, command=self.toggle_menu)
        self.open_button.config(width=15, bg="lightblue", fg="black", font=("Roboto", 15, "bold"), relief=tk.RAISED)
        self.open_button.pack(fill=tk.X, pady=5)

        self.conversation_frame = tk.Frame(self.chat_frame)
        self.conversation_frame.pack(fill=tk.BOTH, expand=True)

        self.conversation_canvas = tk.Canvas(self.conversation_frame, width=800, height=400)
        self.conversation_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        

        self.conversation_inner_frame = tk.Frame(self.conversation_canvas)
        self.conversation_canvas.create_window((100,0), window=self.conversation_inner_frame, anchor="nw")

        self.configureScroll(True)

        # Create the input field and the send button.
        self.input_frame = tk.Frame(self.chat_frame)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.default_text = "Write here..."
        self.entry = ttk.Entry(self.input_frame, style="Rounded.TEntry", width=50)
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entry.insert(0, self.default_text)

        self.entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.entry.bind("<FocusOut>", self.on_entry_focus_out)
        
        # Add the event to send the message when the user presses the Enter key.
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, bg="lightblue", fg="black", font=("Roboto", 15, "bold"), relief=tk.RAISED)
        self.send_button.pack(side=tk.LEFT, padx=(10, 0), pady=5, ipadx=10)

        self.menu_open = False
        self.menu_buttons = []  

        # Add the menu buttons.
        self.add_menu_title("Old conversations")
        self.add_menu_button_top("New conversation +", 0)
        for index, chat in enumerate(chats.get("chats")):
            self.add_menu_button_bottom(chat.get("name"), index + 1)

        self.printWelcome()
        self.style = ttk.Style()
        self.style.theme_use("clam")  
        self.style.configure("Rounded.TEntry", borderwidth=0, relief="flat", foreground="grey", background="white", padding=5)
        self.style.map("Rounded.TEntry", foreground=[("active", "black"), ("!disabled", "black")], background=[("active", "#BBDEFB"), ("!disabled", "white")])
    
    # Function to scroll the conversation when the user uses the mouse wheel.
    def on_mousewheel(self, event):
        self.conversation_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Function to add a new button to the menu.
    def add_menu_title(self, title):
        label = tk.Label(self.menu_frame, text=title, bg="lightgrey", fg="black", font=("Roboto", 15, "bold"))
        label.pack(fill=tk.X, pady=5)

    # Function to add a new button to the top of the menu.
    def add_menu_button_top(self, title, index):
        if len(title) > 20:
            title = title[:20] + "..."
        button = tk.Button(self.menu_frame, text=title, command=lambda idx=index: self.menu_button_clicked(idx))
        button.config(width=15, bg="lightblue", fg="black", font=("Roboto", 12, "bold"), relief=tk.RAISED)
        button.pack(fill=tk.X)
        button.config(width=20)
        button.index = index
        self.menu_buttons.append(button)

    # Function to add a new button to the bottom of the menu.
    def add_menu_button_bottom(self, title, index):
        if len(title) > 20:
            title = title[:20] + "..."
        button = tk.Button(self.menu_frame, text=title, command=lambda idx=index: self.menu_button_clicked(idx))
        button.config(width=15, bg="lightblue", fg="black", font=("Roboto", 12, "bold"), relief=tk.RAISED)
        button.pack(fill=tk.X, side=tk.BOTTOM)  
        button.index = index
        self.menu_buttons.append(button)

    # Function to handle the event when a menu button is clicked.
    def menu_button_clicked(self, index):
        if index == 0:
            self.firstMesage = True
            self.currentChat = self.numChats
            self.conversation_inner_frame.destroy()
            self.conversation_canvas.destroy()
            self.conversation_canvas = tk.Canvas(self.conversation_frame, width=800, height=400)
            self.conversation_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.conversation_inner_frame = tk.Frame(self.conversation_canvas)
            self.conversation_canvas.create_window((100,0), window=self.conversation_inner_frame, anchor="nw") 
            self.configureScroll()   
            self.printWelcome()        
            self.response_developer.loadContext({})
        else:
            self.currentChat = index
            self.firstMesage = False
            self.conversation_inner_frame.destroy()
            self.conversation_canvas.destroy()
            self.conversation_canvas = tk.Canvas(self.conversation_frame, width=800, height=400)
            self.conversation_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.conversation_inner_frame = tk.Frame(self.conversation_canvas)
            self.conversation_canvas.create_window((100,0), window=self.conversation_inner_frame, anchor="nw")
            self.configureScroll()
            
            self.printWelcome()
            for message in self.chats.get("chats")[index - 1].get("messages"):
                if "phoneImage" in message:
                    self.display_phone(message.get("content"), message.get("phoneImage"), save = False)
                else:
                    self.display_message(message.get("content"), message.get("author"))
                
            self.response_developer.loadContext(self.chats.get("chats")[index - 1].get("context"))
            
    def configureScroll(self, first = False):
        if not first:
            self.conversation_scrollbar.destroy()
            
        self.conversation_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.conversation_inner_frame.bind("<Configure>", self.on_inner_frame_configure)
        # Create the scrollbar for the conversation.
        self.conversation_scrollbar = ttk.Scrollbar(self.conversation_frame, orient=tk.VERTICAL, command=self.conversation_canvas.yview)
        self.conversation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.conversation_canvas.configure(yscrollcommand=self.conversation_scrollbar.set)

    # Function to toggle the menu.
    def toggle_menu(self):
        if not self.menu_open:
            self.menu_frame.pack_forget()
            self.open_button_text.set("Open sidebar")
            self.menu_open = True
        else:
            self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
            self.open_button_text.set("Close sidebar")
            self.menu_open = False

    def on_entry_focus_in(self, event):
        if self.entry.get() == self.default_text:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground="black")  

    def on_entry_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.default_text)
            self.entry.config(foreground="grey")  

    # Function that simulates a message send by the user
    def send_message(self, event=None):
        message = self.entry.get()
        if message != self.default_text and len(message) != 0:  
            self.entry.delete(0, tk.END)
            self.display_message(message, "user")
            if self.firstMesage:
                self.add_menu_button_bottom(message, self.numChats)
                self.firstMesage = False
                self.chats.get("chats").append({
                    "name": message, 
                    "messages": [{
                        "author": "user",
                        "content": message,
                    }],
                    "context": "{}"    
                })
                self.currentChat = self.numChats
                self.numChats +=1
            else: 
                self.chats.get("chats")[self.currentChat - 1].get("messages").append({
                    "author": "user",
                    "content": message
                })
                
            processed_input = sentence.process_input(message)
            self.response_developer.developResponse(processed_input)
            json.dump(self.chats, open("data/chats.json", "w"), indent=4) 
            
    # Function that simulates a message send by the bot
    def send_response(self, response, save = True):
        self.display_message(response, "bot")
        if save:
            self.chats.get("chats")[self.currentChat - 1].get("messages").append({
                "author": "bot",
                "content": response
            })
            json.dump(self.chats, open("data/chats.json", "w"), indent=4)

    # Function that display one message
    def display_message(self, message, sender):
        bubble = MessageBubble(self.conversation_inner_frame, text=message, sender=sender)
        bubble.pack(anchor="e" if sender == "user" else "w", padx=5, pady=5, fill="x")
        
        self.conversation_canvas.update_idletasks() 
        self.conversation_canvas.yview_moveto(1.0)
    
    def display_phone(self, message, phoneImage, save = True):
        bubble = MessageBubblePhone(self.conversation_inner_frame, text=message, phoneImage=phoneImage)
        bubble.pack(anchor = "w", padx=5, pady=5, fill="x")
        
        self.conversation_canvas.update_idletasks() 
        self.conversation_canvas.yview_moveto(1.0)
        if save:
            self.chats.get("chats")[self.currentChat - 1].get("messages").append({
                "author": "bot",
                "content": message,
                "phoneImage": phoneImage
            })

    # Function that upload a entierly conversation
    def upload_conversation(self, file_path):
        with open(file_path, "r") as file:
            for line in file:
                self.conversation.insert(tk.END, line)

    def on_inner_frame_configure(self, event):
        self.conversation_canvas.configure(scrollregion=self.conversation_canvas.bbox("all"))

    def printWelcome(self):
        self.send_response("""Hi! I'm Ringo and my mission is to guide you in the process of choosing a new phone You can consider the following specifications and requirements:\n
        · Brand
        · Battery
        · Screen size
        · Resolution
        · RAM
        · Internal storage capacity
        · Operating System
        · Generation (3G, 4G, 5G)
        · Price                                                      
        """, save = False)
        self.send_response("Let me know what you need!", save = False)
        
    def saveContext(self, context):
        self.chats.get("chats")[self.currentChat - 1]["context"] = context
        json.dump(self.chats, open("data/chats.json", "w"), indent=4) 
        print(self.chats.get("chats")[self.currentChat - 1]["context"])
