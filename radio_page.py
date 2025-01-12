import os
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QSlider, QAbstractItemView, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, QUrl, QTimer, QSize
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QFont, QIcon

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

        # 이미지 파일 경로
        self.start_img_path = os.path.join(os.path.dirname(__file__), "assets", "audio_start_btn.png")
        self.stop_img_path = os.path.join(os.path.dirname(__file__), "assets", "audio_stop_btn.png")

        self.setup_ui()
        self.load_wordbooks_into_combobox()

    def setup_ui(self):
        self.setStyleSheet("""
            QPushButton {
                color: #fff;
                background-color: #45b1e9;
                border: 1px solid #ffffffff;
                border-radius: 6px;
                padding: 10px;
                width: 100%;
            }
            QPushButton:hover {
                background-color:#229bd8;
            }
            QLabel {
                font-size: 15px;
            }
            QLineEdit {
                height: 20px;
                border: 2px solid #45b1e9;
                border-radius: 6px;
                padding: 5px;
                font-family: 'Pretendard'; 
                font-size: 14px;
            }
            QTableWidget {
                border: 2px solid #45b1e9;
                border-radius: 6px;
            }
            QListWidget {
                border: 2px solid #45b1e9;
                border-radius: 6px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(15, 5, 30, 30)
        
        # (1) 상단 타이틀, 설명
        layout.addSpacing(20)
        title_label = QLabel("실전 듣기")
        title_label_font = QFont("esamanru Bold")
        title_label.setFont(title_label_font)
        title_label.setStyleSheet("color: #458EE9; font-size: 30px;")
        desc_label = QLabel("내 단어장의 단어를 사용한 라디오를 생성하고 들어봐요!")
        desc_label.setStyleSheet("font-family: 'Pretendard Light'; margin-bottom: 10px; font-size: 15px;")
        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        # 상단: 콤보박스(단어장), OpenAI key, '라디오 생성' 버튼 등
        top_layout = QHBoxLayout()
        self.wordbook_combo = QComboBox()
        self.wordbook_combo.currentIndexChanged.connect(self.on_wordbook_selected)
        self.wordbook_combo.setStyleSheet("font-family: 'Pretendard'; font-size: 16px; margin-left: 10px; min-width: 250px;")
        left_label = QLabel("단어장 선택")
        left_label.setStyleSheet("font-family: 'esamanru Light'; font-size: 23px; color: #458EE9;")
        top_layout.addWidget(left_label)
        top_layout.addWidget(self.wordbook_combo)

        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.Password)
        self.openai_key_edit.setPlaceholderText("OpenAI API Key를 입력하세요.")
        self.openai_key_edit.setStyleSheet("font-family: 'Pretendard Bold'; font-size: 16px;")
        top_layout.addWidget(self.openai_key_edit)

        self.generate_button = QPushButton("라디오 생성")
        self.generate_button.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.generate_button.clicked.connect(self.on_generate_radio)
        top_layout.addWidget(self.generate_button)

        # 단어 테이블 표시/숨기기 토글 버튼
        self.toggle_table_button = QPushButton("단어 가리기")
        self.toggle_table_button.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.toggle_table_button.clicked.connect(self.toggle_word_table)
        top_layout.addWidget(self.toggle_table_button)

        # 대본/오디오 재로딩 버튼
        self.reload_button = QPushButton("파일 새로고침")
        self.reload_button.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.reload_button.clicked.connect(self.on_reload)
        top_layout.addWidget(self.reload_button)

        layout.addLayout(top_layout)

        # 중앙: 왼쪽(단어 테이블), 오른쪽(대본 + 체크박스)
        center_layout = QHBoxLayout()

        # 단어 테이블
        self.word_table = QTableWidget()
        self.word_table.setColumnCount(2)
        self.word_table.setHorizontalHeaderLabels(["영단어", "뜻"])
        self.word_table.setStyleSheet("font-family: 'Pretendard'; font-size: 16px; max-width: 300px;")
        self.word_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.word_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.word_table.verticalHeader().setVisible(False)
        center_layout.addWidget(self.word_table, stretch=1)

        # 대본 및 체크박스
        right_layout = QVBoxLayout()
        script_lbl = QLabel("라디오 대본")
        script_lbl.setStyleSheet("font-family: 'esamanru Bold'; font-size: 23px; color: #458EE9;")
        right_layout.addWidget(script_lbl)

        chk_layout = QHBoxLayout()
        self.chk_eng = QCheckBox("영문 대본 보기")
        self.chk_eng.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.chk_eng.setChecked(True)
        self.chk_eng.stateChanged.connect(self.update_script_text_display)
        self.chk_kor = QCheckBox("한글 대본 보기")
        self.chk_kor.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.chk_kor.setChecked(True)
        self.chk_kor.stateChanged.connect(self.update_script_text_display)
        chk_layout.addWidget(self.chk_eng)
        chk_layout.addWidget(self.chk_kor)
        chk_layout.addStretch()

        right_layout.addLayout(chk_layout)

        self.script_edit = QTextEdit()
        self.script_edit.setReadOnly(True)
        self.script_edit.setStyleSheet("font-family: 'Pretendard'; font-size: 18px; border: 2px solid #45b1e9; border-radius: 6px;")
        right_layout.addWidget(self.script_edit, stretch=1)

        center_layout.addLayout(right_layout, stretch=1)
        layout.addLayout(center_layout)

        # 하단: 재생 버튼(이미지 아이콘), 슬라이더, 시간 레이블
        bottom_layout = QHBoxLayout()

        # 버튼 자체를 이미지 아이콘으로 사용하기 위해 setIcon() 이용
        self.play_button = QPushButton("")
        self.play_button.setEnabled(False)
        self.play_button.setFixedSize(50, 50)
        # 초기 상태(정지)에서는 재생 버튼 이미지로 설정
        self.play_button.setStyleSheet("background-color: #ffffff; border: 1px solid #ffffff;")
        self.play_button.setIcon(QIcon(self.start_img_path))
        self.play_button.setIconSize(QSize(50, 50))
        self.play_button.clicked.connect(self.on_play_pause)
        bottom_layout.addWidget(self.play_button)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.on_slider_moved)
        bottom_layout.addWidget(self.position_slider, stretch=1)

        self.time_label = QLabel("00:00 / 00:00")
        bottom_layout.addWidget(self.time_label)

        layout.addLayout(bottom_layout)

        # 미디어플레이어 시그널 연결
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

        # 버튼 상태 초기화
        self.play_button.setEnabled(False)
        self.is_playing = False
        # 버튼 이미지를 재생 이미지로 변경
        self.play_button.setIcon(QIcon(self.start_img_path))

        self.position_slider.setValue(0)
        self.position_slider.setRange(0, 0)
        self.time_label.setText("00:00 / 00:00")
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
        """
        재생/일시정지 버튼 클릭 시 아이콘을 토글합니다.
        오디오가 정지 중이면 '재생' 아이콘(assets/audio_start_btn.png)
        재생 중이면 '정지' 아이콘(assets/audio_stop_btn.png)으로 변경합니다.
        """
        if self.is_playing:
            # 재생 중이면 일시정지하고 재생 아이콘으로 변경
            self.media_player.pause()
            self.is_playing = False
            self.play_button.setIcon(QIcon(self.start_img_path))
        else:
            # 정지 중이면 재생 시작하고 정지 아이콘으로 변경
            self.media_player.play()
            self.is_playing = True
            self.play_button.setIcon(QIcon(self.stop_img_path))

    def on_slider_moved(self, pos):
        self.media_player.setPosition(pos)

    def on_position_changed(self, pos):
        self.position_slider.setValue(pos)
        dur = self.media_player.duration()
        cur = pos // 1000
        tot = dur // 1000
        self.time_label.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
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
            self.toggle_table_button.setText("단어 가리기")

    # 대본/오디오 재로딩
    def on_reload(self):
        idx = self.wordbook_combo.currentIndex()
        words_dir = os.path.join(os.path.dirname(__file__), "words")
        self.all_data_map = load_wordbooks_with_script_audio(words_dir)
        # 다시 콤보박스 선택 로직 수행
        if idx >= 0:
            self.on_wordbook_selected(idx)
        self.update()
        self.repaint()
