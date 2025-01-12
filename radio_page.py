import os
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QSlider, QAbstractItemView, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# OpenAI API
from openai_api import request_radio_script
# gTTS + pydub
from gtts import gTTS
from pydub import AudioSegment

# wordbook_manager의 확장 함수
from wordbook_manager import load_wordbooks_with_script_audio


class RadioPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 최종 데이터 (title -> { words, wordbook_path, script_text_path, script_audio_path })
        self.all_data_map = {}
        self.parsed_script_lines = []

        self.media_player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.is_playing = False

        self.setup_ui()
        self.load_wordbooks_into_combobox()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # 상단: 콤보박스(단어장), OpenAI key, '라디오 생성' 버튼
        top_layout = QHBoxLayout()
        self.wordbook_combo = QComboBox()
        self.wordbook_combo.currentIndexChanged.connect(self.on_wordbook_selected)
        top_layout.addWidget(QLabel("단어장 선택:"))
        top_layout.addWidget(self.wordbook_combo)

        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.Password)
        self.openai_key_edit.setPlaceholderText("OpenAI API Key를 입력하세요.")
        top_layout.addWidget(self.openai_key_edit)

        self.generate_button = QPushButton("라디오 생성")
        self.generate_button.clicked.connect(self.on_generate_radio)
        top_layout.addWidget(self.generate_button)

        # 단어 테이블 표시/숨기기 토글 버튼
        self.toggle_table_button = QPushButton("테이블 숨기기")
        self.toggle_table_button.clicked.connect(self.toggle_word_table)
        top_layout.addWidget(self.toggle_table_button)

        # 대본/오디오 재로딩 버튼
        self.reload_button = QPushButton("대본/오디오 재로딩")
        self.reload_button.clicked.connect(self.on_reload)
        top_layout.addWidget(self.reload_button)

        layout.addLayout(top_layout)

        # 중앙: 왼쪽(단어 테이블), 오른쪽(대본 + 체크박스)
        center_layout = QHBoxLayout()

        # 단어 테이블
        self.word_table = QTableWidget()
        self.word_table.setColumnCount(2)
        self.word_table.setHorizontalHeaderLabels(["영단어", "뜻"])
        self.word_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.word_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.word_table.verticalHeader().setVisible(False)
        center_layout.addWidget(self.word_table, stretch=1)

        # 대본 및 체크박스
        right_layout = QVBoxLayout()
        script_lbl = QLabel("생성된 라디오 대본")
        right_layout.addWidget(script_lbl)

        chk_layout = QHBoxLayout()
        self.chk_eng = QCheckBox("영문 대본 보기")
        self.chk_eng.setChecked(True)
        self.chk_eng.stateChanged.connect(self.update_script_text_display)
        self.chk_kor = QCheckBox("한글 대본 보기")
        self.chk_kor.setChecked(True)
        self.chk_kor.stateChanged.connect(self.update_script_text_display)
        chk_layout.addWidget(self.chk_eng)
        chk_layout.addWidget(self.chk_kor)
        chk_layout.addStretch()

        right_layout.addLayout(chk_layout)

        self.script_edit = QTextEdit()
        self.script_edit.setReadOnly(True)
        right_layout.addWidget(self.script_edit, stretch=1)

        center_layout.addLayout(right_layout, stretch=1)
        layout.addLayout(center_layout)

        # 하단: 재생/슬라이더/시간
        bottom_layout = QHBoxLayout()
        self.play_button = QPushButton("재생")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.on_play_pause)
        bottom_layout.addWidget(self.play_button)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.on_slider_moved)
        bottom_layout.addWidget(self.position_slider, stretch=1)

        self.time_label = QLabel("00:00 / 00:00")
        bottom_layout.addWidget(self.time_label)

        layout.addLayout(bottom_layout)

        # 미디어플레이어 시그널
        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

        self.setLayout(layout)

    def load_wordbooks_into_combobox(self):
        """
        wordbook_manager.load_wordbooks_with_script_audio 로드 ->
        self.all_data_map 에 저장 -> 콤보박스에 제목 추가
        """
        words_dir = os.path.join(os.path.dirname(__file__), "words")
        self.all_data_map = load_wordbooks_with_script_audio(words_dir)
        self.wordbook_combo.clear()

        if not self.all_data_map:
            self.wordbook_combo.addItem("불러온 단어장이 없습니다.")
            self.wordbook_combo.setEnabled(False)
        else:
            self.wordbook_combo.setEnabled(True)
            for title in self.all_data_map.keys():
                self.wordbook_combo.addItem(title)

    def on_wordbook_selected(self, idx):
        """
        단어장 콤보박스 선택 -> 테이블 표시 + script_text_path, script_audio_path 있으면 로드
        """
        if idx < 0:
            return
        title = self.wordbook_combo.currentText().strip()
        if title not in self.all_data_map:
            return

        info = self.all_data_map[title]
        # 1) 테이블 표시
        words = info["words"]
        self.word_table.setRowCount(len(words))
        for i, w in enumerate(words):
            self.word_table.setItem(i, 0, QTableWidgetItem(w.get('word', '')))
            self.word_table.setItem(i, 1, QTableWidgetItem(w.get('meaning', '')))
        self.word_table.resizeColumnsToContents()

        # 2) 대본, 음성 초기화
        self.parsed_script_lines = []
        self.script_edit.clear()
        self.play_button.setEnabled(False)
        self.position_slider.setValue(0)
        self.position_slider.setRange(0, 0)
        self.time_label.setText("00:00 / 00:00")
        # None 대신 빈 QMediaContent를 전달해 초기화
        self.media_player.setMedia(QMediaContent())

        # script.txt 존재 시 -> 파싱
        txt_path = info.get('script_text_path')
        if txt_path and os.path.exists(txt_path):
            self.parsed_script_lines = self.parse_script_file(txt_path)
            self.update_script_text_display()

        # 음성 존재 시 -> 미디어 로드
        audio_path = info.get('script_audio_path')
        if audio_path and os.path.exists(audio_path):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))

    def parse_script_file(self, path):
        """
        script.txt 파일을 열어 +영문/-한글 라인 파싱
        """
        lines = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    sign = line[0]
                    content = line[1:].strip()
                    if sign in ["+", "-"]:
                        lines.append((sign, content))
        except Exception as e:
            print(f"parse_script_file error: {e}")
        return lines

    def update_script_text_display(self):
        """
        영문/한글 체크박스 상태에 따라 대본 표시
        """
        show_lines = []
        for s, c in self.parsed_script_lines:
            if s == "+" and self.chk_eng.isChecked():
                show_lines.append(f"+{c}")
            elif s == "-" and self.chk_kor.isChecked():
                show_lines.append(f"-{c}")

        self.script_edit.setPlainText("\n\n".join(show_lines))

    def on_generate_radio(self):
        """
        GPT -> 대본 생성 -> script.txt -> (영문 +만) TTS -> script.wav
        -> UI 반영
        """
        title = self.wordbook_combo.currentText().strip()
        if title not in self.all_data_map:
            QMessageBox.warning(self, "오류", "잘못된 단어장 선택")
            return

        info = self.all_data_map[title]
        words = info["words"]
        if not words:
            QMessageBox.warning(self, "오류", "단어 목록이 없습니다.")
            return

        openai_key = self.openai_key_edit.text().strip()
        if not openai_key:
            QMessageBox.warning(self, "경고", "OpenAI Key 필요")
            return

        # GPT에 넘길 단어 리스트
        word_list = [w['word'] for w in words if w.get('word')]

        folder = os.path.dirname(info["wordbook_path"])
        script_txt = os.path.join(folder, "script.txt")
        script_wav = os.path.join(folder, "script.wav")
        temp_mp3 = os.path.join(folder, "script_temp.mp3")

        def worker():
            try:
                # 1) GPT 라디오 대본 생성
                script_text = request_radio_script(openai_key, word_list)

                # 2) script.txt 저장
                with open(script_txt, 'w', encoding='utf-8') as f:
                    f.write(script_text.strip())

                # 3) +영문만 모아 TTS -> mp3 -> wav
                lines = self.parse_script_text(script_text)
                eng_text = " ".join(c for s, c in lines if s == "+")
                tts = gTTS(eng_text, lang='en')
                tts.save(temp_mp3)

                seg = AudioSegment.from_mp3(temp_mp3)
                seg.export(script_wav, format="wav")
                os.remove(temp_mp3)

                # all_data_map에 저장
                info["script_text_path"] = script_txt
                info["script_audio_path"] = script_wav

                def ui_up():
                    if self.wordbook_combo.currentText().strip() == title:
                        self.parsed_script_lines = lines
                        self.update_script_text_display()
                        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(script_wav)))

                self.call_in_main_thread(ui_up)

            except Exception as e:
                def err():
                    QMessageBox.critical(self, "오류", f"라디오 생성 실패: {e}")
                self.call_in_main_thread(err)

        threading.Thread(target=worker, daemon=True).start()

    def parse_script_text(self, script_text):
        """
        GPT 대본(문자열) -> +영문/-한글 라인 파싱
        """
        result = []
        for line in script_text.splitlines():
            line = line.strip()
            if not line:
                continue
            sign = line[0]
            content = line[1:].strip()
            if sign in ["+", "-"]:
                result.append((sign, content))
        return result

    def on_play_pause(self):
        if self.is_playing:
            self.media_player.pause()
            self.play_button.setText("재생")
            self.is_playing = False
        else:
            self.media_player.play()
            self.play_button.setText("일시정지")
            self.is_playing = True

    def on_slider_moved(self, pos):
        self.media_player.setPosition(pos)

    def on_position_changed(self, pos):
        self.position_slider.setValue(pos)
        dur = self.media_player.duration()
        cur = pos // 1000
        tot = dur // 1000
        self.time_label.setText(f"{self.sec_to_min_sec(cur)} / {self.sec_to_min_sec(tot)}")

    def on_duration_changed(self, dur):
        self.position_slider.setRange(0, dur)

    def on_media_status_changed(self, status):
        from PyQt5.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.LoadedMedia:
            dur = self.media_player.duration()
            self.position_slider.setRange(0, dur)
            tot = dur // 1000
            self.time_label.setText(f"00:00 / {self.sec_to_min_sec(tot)}")
            self.play_button.setEnabled(True)

    def call_in_main_thread(self, func):
        QTimer.singleShot(0, func)

    @staticmethod
    def sec_to_min_sec(sec):
        m, s = divmod(sec, 60)
        return f"{m:02d}:{s:02d}"

    # 테이블 표시/숨기기 토글
    def toggle_word_table(self):
        if self.word_table.isVisible():
            self.word_table.setVisible(False)
            self.toggle_table_button.setText("테이블 보이기")
        else:
            self.word_table.setVisible(True)
            self.toggle_table_button.setText("테이블 숨기기")

    # 대본/오디오 재로딩
    def on_reload(self):
        idx = self.wordbook_combo.currentIndex()
        words_dir = os.path.join(os.path.dirname(__file__), "words")
        self.all_data_map = load_wordbooks_with_script_audio(words_dir)
