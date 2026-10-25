import tkinter as tk
from tkinter import filedialog

import pygame
from mutagen import MutagenError
from mutagen.easyid3 import EasyID3

pygame.init()

class MusicPlayer(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.grid()
        play_button = tk.Button(self, text="PLAY SONG",command=self.play_song,bg='AntiqueWhite1',width=40)
        play_button.grid(row=2,column=0)
        previous_button = tk.Button(self, text="PREVIOUS SONG",command=self.previous_song,bg='AntiqueWhite1',width=40)
        previous_button.grid(row=4,column=0)
        pause_button = tk.Button(self, text="PAUSE/UNPAUSE",command=self.pause_and_unpause_song,bg='AntiqueWhite1',width=40)
        pause_button.grid(row=3,column=0)
        next_song_button = tk.Button(self, text="NEXT SONG",command=self.next_song,bg='AntiqueWhite1',width=40)
        next_song_button.grid(row=5,column=0)
        add_button = tk.Button(self, text="ADD TO LIST",command=self.add_song,bg='AntiqueWhite1',width=40)
        add_button.grid(row=1,column=0)
        self.now_playing_label  = tk.Label(self, fg='Black',font=('Helvetica 12 bold italic',10),bg='ivory2')
        self.now_playing_label.grid(row=6,column=0)
        self.playlist_text = tk.Text(self,wrap=tk.WORD,width=60)
        self.playlist_text.grid(row=8,column=0)
        self.playlist = []
        self.is_paused = False
        self.current_song_index = 0
        self.SONG_END = pygame.USEREVENT + 1
#################################################################################
    def add_song(self):
        try:
            directory = filedialog.askopenfilenames()
            for song_dir in directory:
                print(song_dir)
                self.playlist.append(song_dir)
            self.playlist_text.delete(0.0, tk.END)

            for key, item in enumerate(self.playlist):
                song = EasyID3(item)

                title = song.get("title", ["Unknown Title"])[0]
                artist = song.get("artist", ["Unknown Artist"])[0]

                song_data = f"{key + 1}: {title} - {artist}"

                self.playlist_text.insert(tk.END, song_data + "\n")
        except (MutagenError) as error:
            print(f"{error}")
            return
#################################################################################
    def song_data(self):
        song_path = self.playlist[self.current_song_index]

        try:
            song = EasyID3(song_path)

        except (MutagenError, OSError) as error:
            print(f"Error reading song metadata: {error}")
            return "Unknown Song"

        title = song.get("title", ["Unknown Title"])[0]
        artist = song.get("artist", ["Unknown Artist"])[0]

        return (
            f"Now playing: Nr:{self.current_song_index + 1} "
            f"{title} - {artist}"
        )

#################################################################################
    def play_song(self):
        try:
            directory = self.playlist[self.current_song_index]
            pygame.mixer.music.load(directory)
            pygame.mixer.music.play(1, 0.0)
            pygame.mixer.music.set_endevent(self.SONG_END)
            self.is_paused = False
            self.now_playing_label['text'] = self.song_data()
        except pygame.error as error:
            print(f"Error playing song: {error}")
            return
#################################################################################
    def check_music(self):
        try:
            for event in pygame.event.get():
                if event.type == self.SONG_END:
                    self.next_song()
        except pygame.error as error:
            print(f"{error}")
            return
#################################################################################
    def pause_and_unpause_song(self):
        try:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            elif not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
        except pygame.error as error:
            print(f"{error}")
            return
#################################################################################
    def get_next_song(self):
        if self.current_song_index + 2 <= len(self.playlist):
            return self.current_song_index + 1
        else:
            return 0
#################################################################################
    def next_song(self):
        if not self.playlist:
            return

        self.current_song_index = self.get_next_song()
        self.play_song()
#################################################################################
    def get_previous_song(self):
        if self.current_song_index - 1 >= 0:
            return self.current_song_index - 1
        else:
            return len(self.playlist) - 1
#################################################################################
    def previous_song(self):
        self.current_song_index = self.get_previous_song()
        self.play_song()
#################################################################################
################################################################################# 
window = tk.Tk()
window.geometry("500x500")
window.title("MP3 Music Player")
#################################################################################
app = MusicPlayer(window)
#################################################################################
while True:
    # runs mainloop of program
    app.check_music()
    app.update()