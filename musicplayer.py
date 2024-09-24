import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QListWidget,QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.folder_path = ''
        self.init_ui()
        self.position_timer = QTimer(self)
        self.position_timer.timeout.connect(self.update_position)
        
    def init_ui(self):
        self.setWindowTitle('Music Player')
        self.setGeometry(100, 100, 600, 400)
        vbox = QVBoxLayout(self)
        
    # Create a horizontal layout for playback controls
        hbox_playback = QHBoxLayout()
        
        # Buttons with icons
        play_icon = QIcon('icons/play_icon.png')
        pause_icon = QIcon('icons/pause_icon.png')
        resume_icon = QIcon('icons/resume_icon.png')
        stop_icon = QIcon('icons/stop_icon.png')
        load_folder_icon = QIcon('icons/folder_icon.png')
        
        self.play_button = QPushButton(self)
        self.play_button.setIcon(play_icon)
        self.play_button.clicked.connect(self.play_pause_music)
        
        self.pause_button = QPushButton(self)
        self.pause_button.setIcon(pause_icon)
        self.pause_button.clicked.connect(self.pause_music)
        
        self.resume_button = QPushButton(self)
        self.resume_button.setIcon(resume_icon)
        self.resume_button.clicked.connect(self.resume_music)

        self.stop_button = QPushButton(self)
        self.stop_button.setIcon(stop_icon)
        self.stop_button.clicked.connect(self.stop_music)

        load_folder_button = QPushButton('Load Folder', self)
        load_folder_button.setIcon(load_folder_icon)
        load_folder_button.clicked.connect(self.load_folder)

        

        # Create a horizontal layout for playback controls
        hbox_playback = QHBoxLayout()
        hbox_playback.addWidget(self.play_button)
        hbox_playback.addWidget(self.pause_button)
        hbox_playback.addWidget(self.resume_button)
        hbox_playback.addWidget(self.stop_button)

        # Add the load folder button and playback controls to the vertical layout
        vbox.addWidget(load_folder_button)
        vbox.addLayout(hbox_playback)

        # Other widgets (song list, labels, sliders)
        self.song_list = QListWidget(self)
        self.song_list.clicked.connect(self.play_selected_song)
        vbox.addWidget(self.song_list)

        self.file_label = QLabel('No file loaded', self)
        vbox.addWidget(self.file_label)

        self.duration_label = QLabel('Duration: 00:00', self)
        vbox.addWidget(self.duration_label)

        self.position_label = QLabel('Progress: 00:00', self)
        vbox.addWidget(self.position_label)

        hbox_slider = QHBoxLayout()
        self.position_slider = QSlider(Qt.Horizontal)
        self.volume_slider = QSlider(Qt.Vertical)
        hbox_slider.addWidget(self.position_slider)
        hbox_slider.addWidget(self.volume_slider)
        vbox.addLayout(hbox_slider)

        self.volume_label = QLabel('Volume: 50', self)
        vbox.addWidget(self.volume_label)

        self.setLayout(vbox)

        # Apply styling
        self.setStyleSheet("background-color: #f0f0f0;")
        self.play_button.setStyleSheet("background-color: #90ee90;")
        self.pause_button.setStyleSheet("background-color: #ffb6c1;")
        self.resume_button.setStyleSheet("background-color: #add8e6;")
        self.stop_button.setStyleSheet("background-color: #ffcccb;")
        load_folder_button.setStyleSheet("background-color: #afeeee;")
        self.song_list.setStyleSheet("background-color: #ffffff;")
        self.volume_slider.valueChanged.connect(self.change_volume)

        # Create a media player instance
        self.media_player = QMediaPlayer(self)
        self.media_player.setVolume(50)

        # Connect signals to slots
        self.media_player.durationChanged.connect(self.get_duration)
        self.media_player.positionChanged.connect(self.update_slider)


    def update_volume_label(self, value):
        self.volume_label.setText(f'Volume: {value}')

    def update_slider(self, position):
        self.position_slider.setValue(position)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def load_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if self.folder_path:
            self.populate_song_list()

    def populate_song_list(self):
        self.playlist = []
        self.song_list.clear()

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith('.mp3'):
                    file_path = os.path.abspath(os.path.join(root, file))
                    self.playlist.append(file_path)
                    self.song_list.addItem(file_path)


    def play_selected_song(self, item):
        selected_item = self.song_list.currentItem()
        if selected_item:
            selected_song = selected_item.text()
            self.playlist = [selected_song]
            self.current_index = 0
            self.file_label.setText(selected_song)
            self.play_music()

    def play_music(self):
        if self.playlist:
            file_path = self.playlist[self.current_index]
            media_content = QMediaContent(QUrl.fromLocalFile(file_path))
            self.media_player.setMedia(media_content)
            self.media_player.play()
            self.is_playing = True

            self.position_timer.start(1000)

    def update_position(self):
        position = self.media_player.position()
        duration = self.media_player.duration()
        
        if duration > 0:
            self.position_slider.setMaximum(duration)
            self.position_slider.setValue(position)

            current_minutes = position // 60000
            current_seconds = (position % 60000) // 1000
            total_minutes = duration // 60000
            total_seconds = (duration % 60000) // 1000

            self.position_label.setText(f'Progress: {current_minutes:02}:{current_seconds:02}')
            self.duration_label.setText(f'Duration: {total_minutes:02}:{total_seconds:02}')
        else:
            # Handle the case when duration is zero (or less)
            self.position_slider.setMaximum(0)
            self.position_slider.setValue(0)
            self.position_label.setText('Progress: 00:00')

            
    def stop_music(self):
        self.media_player.stop()
        self.is_playing = False

    def play_pause_music(self):
        if not self.is_playing and self.playlist:
            self.play_music()
        else:
            self.media_player.pause()
            self.is_playing = False

    def pause_music(self):
        if self.is_playing:
            self.media_player.pause()
            self.is_playing = False

    def resume_music(self):
        if not self.is_playing:
            self.media_player.play()
            self.is_playing = True

    def change_volume(self, value):
        self.media_player.setVolume(value)
        self.volume_label.setText(f'Volume: {value}')

    def get_duration(self, duration):
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        self.duration_label.setText(f'Duration: {minutes:02}:{seconds:02}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())


    
