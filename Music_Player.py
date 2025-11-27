# MUSIC PLAYER By Jessie
# V 0.1.o DATE: 14/NOV/2025
# Python 3.x

# Import LIBRARIES
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
from pygame import mixer
from PIL import Image, ImageTk
import os
from pathlib import Path
from mutagen.id3 import ID3
from mutagen.wave import WAVE
from mutagen.flac import FLAC
import io
import threading
import time

# Main Config
mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("MUSIC PLAYER")
        self.root.geometry("1400x800")
        self.root.configure(bg="#0f0f0f")

        # Variables
        self.playlist = []
        self.current_track = 0
        self.is_playing = False
        self.current_song_path = None
        self.supported_formats = (".mp3", ".wav", ".flac")
        self.music_folder = None

        # FIXED: SLIDER ISSUE
        self.slider_dragging = False
        self.playback_start_time = 0
        self.playback_seek_time = 0
        self.last_slider_value = 0

        # Generate UI
        self.create_ui()
        self.start_update_thread()
    
    # Main UI Creation
    def create_ui(self):

        main_frame = Frame(self.root, bg="#0f0f0f")
        main_frame.pack(fill=BOTH, expand=True)

        # UPPER BAR
        top_bar = Frame(main_frame, bg="#1a1a1a", height=50)
        top_bar.pack(fill=X)
        top_bar.pack_propagate(False)

        title = Label(top_bar, text="🎵 MUSIC PLAYER (Alpha v0.1.o)", bg="#1a1a1a", 
                     fg="white", font=("Arial", 16, "bold"))
        title.pack(side=LEFT, padx=20, pady=10)

        # MAIN CONTENT FRAME
        content_frame = Frame(main_frame, bg="#0f0f0f")
        content_frame.pack(fill=BOTH, expand=True)

        # LEFT SIDEBAR
        sidebar = Frame(content_frame, bg="#1a1a1a", width=220)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        # SEARCH BAR
        search_frame = Frame(sidebar, bg="#1a1a1a")
        search_frame.pack(fill=X, padx=10, pady=10)
        Label(search_frame, text="🔍 Search", bg="#1a1a1a", fg="#888888", 
             font=("Arial", 9)).pack(anchor=W)
        self.search_entry = Entry(search_frame, bg="#2a2a2a", fg="white", 
                                 font=("Arial", 10))
        self.search_entry.pack(fill=X, pady=(5, 0))

        # FOLDER BUTTON
        folder_btn = Button(sidebar, text="📂 Open Folder", command=self.load_folder,
                           bg="#333333", fg="white", font=("Arial", 10), 
                           relief=FLAT, padx=10, pady=8)
        folder_btn.pack(fill=X, padx=10, pady=(0, 10))

        # CATEGORIES
        categories = ["Artist", "Genre", "Folder", "Playlist"]
        for cat in categories:
            btn = Button(sidebar, text=cat, bg="#1a1a1a", fg="#888888",
                        font=("Arial", 9), relief=FLAT, anchor=W, padx=10, pady=8)
            btn.pack(fill=X)

        # RIGHT AND CENTER FRAMES
        center_frame = Frame(content_frame, bg="#0f0f0f")
        center_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        # UPPER SECTION: INFO Y CONTROLS
        top_section = Frame(center_frame, bg="#0f0f0f")
        top_section.pack(fill=BOTH, expand=True, pady=(0, 10))

        # ALBUM COVER
        cover_frame = Frame(top_section, bg="#2a2a2a", width=280, height=280)
        cover_frame.pack(side=LEFT, padx=(0, 20))
        cover_frame.pack_propagate(False)

        self.cover_label = Label(cover_frame, bg="#2a2a2a", fg="#666666",
                                font=("Arial", 11), text="Album Cover")
        self.cover_label.pack(expand=True)

        # INFO AND CONTROLS PANEL
        info_panel = Frame(top_section, bg="#0f0f0f")
        info_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 20))

        # SONG INFO
        self.artist_label = Label(info_panel, text="Artist", bg="#0f0f0f",
                                 fg="#888888", font=("Arial", 12))
        self.artist_label.pack(anchor=W, pady=(0, 5))

        self.title_label = Label(info_panel, text="Song Title", bg="#0f0f0f",
                                fg="white", font=("Arial", 18, "bold"),
                                wraplength=300)
        self.title_label.pack(anchor=W, pady=(0, 10))

        self.album_label = Label(info_panel, text="Album", bg="#0f0f0f",
                                fg="#666666", font=("Arial", 10))
        self.album_label.pack(anchor=W, pady=(0, 20))

        # PLAYBACK CONTROLS
        controls_frame = Frame(info_panel, bg="#0f0f0f")
        controls_frame.pack(anchor=W, pady=10)

        self.prev_btn = Button(controls_frame, text="⏮", command=self.previous,
                              bg="#333333", fg="white", font=("Arial", 18),
                              width=3, relief=FLAT)
        self.prev_btn.pack(side=LEFT, padx=5)

        self.play_btn = Button(controls_frame, text="▶", command=self.play_pause,
                              bg="#4CAF50", fg="white", font=("Arial", 18),
                              width=3, relief=FLAT)
        self.play_btn.pack(side=LEFT, padx=5)

        self.next_btn = Button(controls_frame, text="⏭", command=self.next,
                              bg="#333333", fg="white", font=("Arial", 18),
                              width=3, relief=FLAT)
        self.next_btn.pack(side=LEFT, padx=5)

        # PROGRESS SLIDER
        progress_frame = Frame(info_panel, bg="#0f0f0f")
        progress_frame.pack(fill=X, pady=20)

        self.time_label = Label(progress_frame, text="0:00", bg="#0f0f0f",
                               fg="#888888", font=("Arial", 9))
        self.time_label.pack(side=LEFT, padx=(0, 10))

        self.progress_slider = Scale(progress_frame, from_=0, to=100, orient=HORIZONTAL,
                                    bg="#333333", fg="#4CAF50", length=200,
                                    command=self.on_slider_change)
        self.progress_slider.pack(side=LEFT, fill=X, expand=True)

        # SLODER EVENTS
        self.progress_slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.duration_label = Label(progress_frame, text="0:00", bg="#0f0f0f",
                                   fg="#888888", font=("Arial", 9))
        self.duration_label.pack(side=LEFT, padx=(10, 0))

        # VOLUME CONTROL
        volume_frame = Frame(info_panel, bg="#0f0f0f")
        volume_frame.pack(anchor=W, pady=10)

        Label(volume_frame, text="🔊 Vol", bg="#0f0f0f", fg="#888888",
             font=("Arial", 10)).pack(side=LEFT, padx=(0, 10))
        self.volume_slider = Scale(volume_frame, from_=0, to=100, orient=HORIZONTAL,
                                  bg="#333333", fg="#4CAF50", length=150,
                                  command=self.set_volume)
        self.volume_slider.set(70)
        self.volume_slider.pack(side=LEFT)

        # METADATA PANEL
        metadata_panel = Frame(top_section, bg="#1a1a1a", width=280)
        metadata_panel.pack(side=RIGHT, fill=BOTH)
        metadata_panel.pack_propagate(False)

        Label(metadata_panel, text="📊 INFO", bg="#1a1a1a", fg="white",
             font=("Arial", 11, "bold")).pack(anchor=W, padx=15, pady=(15, 10))

        # FRAME W SCROLLBAR
        scroll_frame = Frame(metadata_panel, bg="#1a1a1a")
        scroll_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        scrollbar_meta = ttk.Scrollbar(scroll_frame)
        scrollbar_meta.pack(side=RIGHT, fill=Y)

        self.metadata_text = Text(scroll_frame, bg="#2a2a2a", fg="#888888",
                                 font=("Courier", 8), height=30, width=32,
                                 relief=FLAT, bd=0, padx=8, pady=8,
                                 yscrollcommand=scrollbar_meta.set)
        scrollbar_meta.config(command=self.metadata_text.yview)
        self.metadata_text.pack(fill=BOTH, expand=True)
        self.metadata_text.config(state=DISABLED)

        # SONG LIST / PLAYLIST
        list_frame = Frame(center_frame, bg="#0f0f0f")
        list_frame.pack(fill=BOTH, expand=True)

        Label(list_frame, text="📋 Playlist", bg="#0f0f0f", fg="white",
             font=("Arial", 11, "bold")).pack(anchor=W)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a1a1a", foreground="white",
                       fieldbackground="#1a1a1a", borderwidth=0)
        style.configure("Treeview.Heading", background="#2a2a2a", foreground="white")
        style.map("Treeview", background=[("selected", "#4CAF50")])

        tree_frame = Frame(list_frame, bg="#0f0f0f")
        tree_frame.pack(fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.playlist_tree = ttk.Treeview(tree_frame, columns=("Artist", "Duration"),
                                         show="tree headings", yscrollcommand=scrollbar.set,
                                         height=10)
        scrollbar.config(command=self.playlist_tree.yview)

        self.playlist_tree.column("#0", width=250, anchor="w")
        self.playlist_tree.column("Artist", width=150, anchor="w")
        self.playlist_tree.column("Duration", width=100, anchor="center")

        self.playlist_tree.heading("#0", text="Song")
        self.playlist_tree.heading("Artist", text="Artist")
        self.playlist_tree.heading("Duration", text="Duration")

        self.playlist_tree.bind("<Double-1>", self.on_track_select)
        self.playlist_tree.pack(fill=BOTH, expand=True)

    def on_slider_press(self, event):
        # IS SLIDER BEING DRAGGED
        self.slider_dragging = True

    def on_slider_release(self, event):
        # IS SLIDER RELEASED
        self.slider_dragging = False
        slider_value = self.progress_slider.get()
        self.seek_song(slider_value)

    def on_slider_change(self, val):
        # SLIDER VALUE CHANGED
        pass

    def load_folder(self):
        # LOAD MUSIC FOLDER
        folder = filedialog.askdirectory(title="Selecciona carpeta de música")
        if folder:
            self.music_folder = folder
            self.playlist.clear()
            self.playlist_tree.delete(*self.playlist_tree.get_children())

            for file in sorted(os.listdir(folder)):
                if file.lower().endswith(self.supported_formats):
                    file_path = os.path.join(folder, file)
                    self.playlist.append(file_path)

            self.refresh_playlist()
            if self.playlist:
                messagebox.showinfo("Success", f"{len(self.playlist)} Loaded songs from folder.")

    def refresh_playlist(self):
        # UPDATE PLAYLIST DISPLAY
        self.playlist_tree.delete(*self.playlist_tree.get_children())

        for idx, song_path in enumerate(self.playlist):
            metadata = self.get_metadata(song_path)
            name = metadata.get("title", Path(song_path).stem)
            artist = metadata.get("artist", "Unknown")
            duration = metadata.get("duration_str", "0:00")

            self.playlist_tree.insert("", END, text=name, 
                                     values=(artist, duration))

    def get_metadata(self, file_path):
            # METADATA EXTRACTION
        metadata = {
            "title": Path(file_path).stem,
            "artist": "Unknown",
            "album": "Unknown",
            "cover": None,
            "format": "",
            "bitrate": 0,
            "sample_rate": 0,
            "channels": 0,
            "duration": 0,
            "duration_str": "0:00"
        }

        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == ".mp3":
                metadata["format"] = "MP3"
                try:
                    tags = ID3(file_path)
                    metadata["title"] = str(tags.get("TIT2", Path(file_path).stem))
                    metadata["artist"] = str(tags.get("TPE1", "Unknown"))
                    metadata["album"] = str(tags.get("TALB", "Unknown"))

                    for frame in tags.getall("APIC"):
                        metadata["cover"] = frame.data
                        break
                except:
                    pass

                try:
                    from mutagen.mp3 import MP3
                    audio = MP3(file_path)
                    metadata["bitrate"] = audio.info.bitrate // 1000
                    metadata["sample_rate"] = audio.info.sample_rate
                    metadata["channels"] = audio.info.channels
                    metadata["duration"] = int(audio.info.length)
                except:
                    pass

            elif file_ext == ".flac":
                metadata["format"] = "FLAC"
                try:
                    tags = FLAC(file_path)
                    metadata["title"] = tags.get("title", [Path(file_path).stem])[0]
                    metadata["artist"] = tags.get("artist", ["Unknown"])[0]
                    metadata["album"] = tags.get("album", ["Unknown"])[0]
                    metadata["bitrate"] = tags.info.bitrate // 1000 if tags.info.bitrate else 0
                    metadata["sample_rate"] = tags.info.sample_rate
                    metadata["channels"] = tags.info.channels
                    metadata["duration"] = int(tags.info.length)

                    if tags.pictures:
                        metadata["cover"] = tags.pictures[0].data
                except:
                    pass

            elif file_ext == ".wav":
                metadata["format"] = "WAV"
                try:
                    from mutagen.wave import WAVE
                    audio = WAVE(file_path)
                    metadata["title"] = audio.get("title", [Path(file_path).stem])[0]
                    metadata["artist"] = audio.get("artist", ["Unknown"])[0]
                    metadata["album"] = audio.get("album", ["Unknown"])[0]
                    metadata["sample_rate"] = audio.info.sample_rate
                    metadata["channels"] = audio.info.channels
                    metadata["duration"] = int(audio.info.length)
                except:
                    pass

            mins, secs = divmod(metadata["duration"], 60)
            metadata["duration_str"] = f"{int(mins)}:{int(secs):02d}"

        except:
            pass

        return metadata

    def format_duration(self, seconds):

        # TIME FORMAT

        mins, secs = divmod(int(seconds), 60)
        return f"{mins}:{secs:02d}"

    def update_metadata_display(self):
        """Actualizar panel de metadatos"""
        if self.current_song_path and self.current_track < len(self.playlist):
            metadata = self.get_metadata(self.current_song_path)

            info_text = f"""━━━━━━━━━━━━━━━━━━━

📁 INFO

TITLE:
{metadata.get('title', 'N/A')[:25]}

ARTIST:
{metadata.get('artist', 'N/A')[:25]}

ALBUM:
{metadata.get('album', 'N/A')[:25]}

━━━━━━━━━━━━━━━━━━━

🎵 PROPERTIES

FORMAT:
{metadata.get('format', 'N/A')}

LENGTH:
{metadata.get('duration_str', 'N/A')}

BITRATE:
{metadata.get('bitrate', 0)} kbps

FRECUENCY:
{metadata.get('sample_rate', 0)} Hz

CHANNELS:
{metadata.get('channels', 0)}

━━━━━━━━━━━━━━━━━━━

📂 FILE

PATH:
{Path(self.current_song_path).name[:25]}

SIZE:
{self.get_file_size(self.current_song_path)}

━━━━━━━━━━━━━━━━━━━"""

            self.metadata_text.config(state=NORMAL)
            self.metadata_text.delete("1.0", END)
            self.metadata_text.insert("1.0", info_text)
            self.metadata_text.config(state=DISABLED)

    def get_file_size(self, file_path):
        # GET FILE SIZE ON MB
        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        except:
            return "N/A"

    def on_track_select(self, event):
        # SELECT SONG FROM PLAYLIST
        selection = self.playlist_tree.selection()
        if selection:
            self.current_track = self.playlist_tree.index(selection[0])
            self.play()

    def play(self):
        # PLAY SELECTED SONG
        if self.current_track < len(self.playlist):
            try:
                song_path = self.playlist[self.current_track]
                mixer.music.load(song_path)
                mixer.music.play()
                self.is_playing = True
                self.current_song_path = song_path
                self.play_btn.config(text="⏸", bg="#FF6B6B")
                self.playback_start_time = time.time()  # NUEVO: registrar inicio
                self.playback_seek_time = 0  # NUEVO: reset seek time
                self.update_metadata_display()
                self.update_display()
            except Exception as e:
                messagebox.showerror("Error", f"No se puede reproducir: {e}")

    def play_pause(self):
        # PLAY OR PAUSE SONG
        if not self.playlist:
            messagebox.showwarning("Warning", "Sin canciones cargadas")
            return

        if self.is_playing:
            mixer.music.pause()
            self.is_playing = False
            self.play_btn.config(text="▶", bg="#4CAF50")
        else:
            if mixer.music.get_busy():
                mixer.music.unpause()
                self.playback_start_time = time.time()  # NUEVO: reiniciar contador
            else:
                self.play()
            self.is_playing = True
            self.play_btn.config(text="⏸", bg="#FF6B6B")

    def next(self):
        # NEXT SONG
        if self.playlist:
            self.current_track = (self.current_track + 1) % len(self.playlist)
            self.play()
            if self.playlist_tree.get_children():
                self.playlist_tree.selection_set(self.playlist_tree.get_children()[self.current_track])

    def previous(self):
        # PREVIOUS SONG
        if self.playlist:
            self.current_track = (self.current_track - 1) % len(self.playlist)
            self.play()
            if self.playlist_tree.get_children():
                self.playlist_tree.selection_set(self.playlist_tree.get_children()[self.current_track])

    def set_volume(self, val):
        # SET VOLUME
        mixer.music.set_volume(float(val) / 100)

    def seek_song(self, val):
        # SEEK SONG TO POSITION
        try:
            if mixer.music.get_busy() and self.is_playing:
                total_duration = self.get_metadata(self.current_song_path).get("duration", 1)
                if total_duration > 0:
                    seek_pos = (float(val) / 100) * total_duration
                    mixer.music.set_pos(seek_pos)

                    # NUEVO: Actualizar tiempos de playback
                    self.playback_start_time = time.time()
                    self.playback_seek_time = seek_pos
        except:
            pass

    def get_current_playback_time(self):
        # CALCULATE CURRENT PLAYBACK TIME
        if not self.is_playing or not self.playback_start_time:
            return 0

        elapsed = time.time() - self.playback_start_time
        return self.playback_seek_time + elapsed

    def start_update_thread(self):
        #UPDATE THREAD
        thread = threading.Thread(target=self.update_loop, daemon=True)
        thread.start()

    def update_loop(self):
        #UPDATE LOOP
        while True:
            try:
                self.update_display()
                time.sleep(0.1)
            except:
                pass

    def update_display(self):
        #UPDATE DISPLAY INFO
        try:
            if self.current_song_path and self.current_track < len(self.playlist):
                metadata = self.get_metadata(self.current_song_path)

                # UPDATE LABELS
                self.title_label.config(text=metadata.get("title", "Unknown"))
                self.artist_label.config(text=metadata.get("artist", "Unknown"))
                self.album_label.config(text=f"📀 {metadata.get('album', 'Unknown')}")

                # UPDATE ALBUM COVER
                if metadata.get("cover"):
                    try:
                        img = Image.open(io.BytesIO(metadata["cover"]))
                        img.thumbnail((280, 280))
                        photo = ImageTk.PhotoImage(img)
                        self.cover_label.config(image=photo, text="")
                        self.cover_label.image = photo
                    except:
                        self.cover_label.config(image="", text="Album Cover")
                else:
                    self.cover_label.config(image="", text="Album Cover")

                # UPDATE PROGRESS SLIDER
                if mixer.music.get_busy() and not self.slider_dragging:
                    current_pos = self.get_current_playback_time()
                    total_duration = metadata.get("duration", 1)

                    if total_duration > 0:
                        # LENGTH ADJUSTMENT
                        if current_pos > total_duration:
                            current_pos = total_duration

                        progress = (current_pos / total_duration) * 100
                        self.progress_slider.set(int(progress))
                        self.time_label.config(text=self.format_duration(current_pos))
                        self.duration_label.config(text=metadata.get("duration_str", "0:00"))

                # SONG ENDED - NEXT
                if not mixer.music.get_busy() and self.is_playing:
                    self.next()
        except:
            pass

# START APPLICATION XO
if __name__ == "__main__":
    root = Tk()
    app = MusicPlayer(root)
    root.mainloop()