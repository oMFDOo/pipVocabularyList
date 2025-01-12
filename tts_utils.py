# tts_utils.py
import os
import tempfile
import threading
from gtts import gTTS
from playsound import playsound

def play_tts_in_background(text, lang='en'):
    """
    text(문자열)를 gTTS로 음성 변환 후, 별도의 스레드에서 바로 재생하는 함수.
    playsound 사용 -> Windows, macOS, Linux에서 ffmpeg 없이 사용 가능 (단, OS별 기본 오디오 플레이어 필요).
    """
    def _play():
        temp_path = None
        try:
            # gTTS 객체 생성
            tts = gTTS(text=text, lang=lang)

            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name
                tts.write_to_fp(fp)

            # 음성 재생
            playsound(temp_path)
        except Exception as e:
            print(f"음성 재생 중 오류 발생: {e}")
        finally:
            # 재생이 끝나면 임시 파일 삭제
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    # 데몬 스레드로 실행 -> 메인 종료 시 함께 종료됨
    threading.Thread(target=_play, daemon=True).start()
