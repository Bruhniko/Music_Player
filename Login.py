# MUSIC PLAYER - login By Jessie
# FOR V 0.1.2 DATE: 1/DEC/2025
# Python 3.x

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk

# MAIN LOGIN WINDOW
class RoundedEntry(tk.Canvas):
    def __init__(self, parent, width, height, placeholder, color="#333333", text_color="white", corner_radius=20, is_password=False):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], bd=0, highlightthickness=0)
        self.placeholder = placeholder
        self.placeholder_color = "#888888"
        self.default_fg = text_color
        self.is_password = is_password
        
        self.create_rounded_rect(0, 0, width, height, corner_radius, color)
        
        self.entry = tk.Entry(self, bg=color, fg=self.placeholder_color, 
                              bd=0, font=("Arial", 11), justify='center', insertbackground="white")
        
        self.create_window(width/2, height/2, window=self.entry, width=width-20)
        
        self.entry.insert(0, self.placeholder)
        self.entry.bind("<FocusIn>", self.on_enter)
        self.entry.bind("<FocusOut>", self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r, fill):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, fill=fill)

    def on_enter(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.default_fg)
            if self.is_password:
                self.entry.config(show="•")

    def on_leave(self, event):
        if self.entry.get() == "":
            if self.is_password:
                self.entry.config(show="")
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=self.placeholder_color)
            
    def get(self):
        val = self.entry.get()
        if val == self.placeholder:
            return ""
        return val

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, text, command, bg_color="white", text_color="black", hover_color="#dddddd"):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], bd=0, highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text = text
        
        self.rect_id = self.create_rounded_rect(0, 0, width, height, 20, bg_color)
        
        self.text_id = self.create_text(width/2, height/2, text=text, fill=text_color, font=("Arial", 11, "bold"))
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        
        self.tag_bind(self.text_id, "<Button-1>", self.on_click)
        self.tag_bind(self.text_id, "<Enter>", self.on_hover)
        self.tag_bind(self.text_id, "<Leave>", self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r, fill):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, fill=fill)

    def on_click(self, event):
        if self.command:
            self.command()
            
    def on_hover(self, event):
        self.itemconfig(self.rect_id, fill=self.hover_color)
        self.config(cursor="hand2")

    def on_leave(self, event):
        self.itemconfig(self.rect_id, fill=self.bg_color)

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player - Login")
        self.root.geometry("400x600")
        self.root.configure(bg="#0f0f0f")
        self.root.resizable(False, False)
        
        self.VALID_USERNAME = "admin"
        self.VALID_PASSWORD = "1234"
        
        self.create_ui()
        
    def create_ui(self):

        content_frame = tk.Frame(self.root, bg="#0f0f0f")
        content_frame.pack(expand=True)
        

        tk.Label(content_frame, text="Music Player", bg="#0f0f0f", fg="white", 
                 font=("Arial", 24, "bold")).pack(pady=(0, 30))
        

        try:
            icon_image = Image.open("assets/icon.png")
            icon_image.thumbnail((100, 100))
            icon_photo = ImageTk.PhotoImage(icon_image)
            icon_label = tk.Label(content_frame, image=icon_photo, bg="#0f0f0f")
            icon_label.image = icon_photo 
            icon_label.pack(pady=(0, 30))
        except:
            icon_label = tk.Label(content_frame, text="😸", bg="#0f0f0f",
                                 font=("Arial", 60))
            icon_label.pack(pady=(0, 30))


        

        self.user_field = RoundedEntry(content_frame, width=280, height=50, 
                                     placeholder="Username", color="#1f1f1f", corner_radius=25)
        self.user_field.pack(pady=10)
        

        self.pass_field = RoundedEntry(content_frame, width=280, height=50, 
                                     placeholder="Password", color="#1f1f1f", corner_radius=25, is_password=True)
        self.pass_field.pack(pady=10)
        

        self.login_btn = RoundedButton(content_frame, width=280, height=50, 
                                      text="LOGIN", command=self.login,
                                      bg_color="white", text_color="black", hover_color="#cccccc")
        self.login_btn.pack(pady=30)
        

        tk.Label(content_frame, text="Forgot password?", bg="#0f0f0f", fg="#666666", 
                 font=("Arial", 9), cursor="hand2").pack(pady=(0, 20))

    def login(self):

        user = self.user_field.get()
        password = self.pass_field.get()
        
        if not user or not password:
            messagebox.showwarning("Advertencia", "Por favor ingresa usuario y contraseña")
            return

        if user == self.VALID_USERNAME and password == self.VALID_PASSWORD:
            self.root.destroy()
            self.open_music_player()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def open_music_player(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            music_player_path = os.path.join(current_dir, "Music_Player.py")
            if os.path.exists(music_player_path):
                subprocess.Popen([sys.executable, music_player_path])
            else:
                messagebox.showerror("Error", "No se encontró Music_Player.py")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()