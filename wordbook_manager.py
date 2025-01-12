import os

def parse_wordbook(file_path):
    """
    단어장 파일을 파싱하여 (영단어, 뜻, 예문) 리스트를 반환하고, 단어의 개수를 셉니다.
    
    파일 형식:
        단어
        뜻
        예문 (선택 사항, '-example +korean example' 형태)
        ...
    """
    words = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        i = 0
        while i < len(lines):
            word = lines[i]
            meaning = lines[i+1] if i+1 < len(lines) else ""
            example = ""
            # i+2 라인이 '-'로 시작하면 예문
            if i+2 < len(lines) and lines[i+2].startswith('-'):
                example_line = lines[i+2]
                # '-hello +안녕' 형태 처리
                if '+' in example_line:
                    parts = example_line[1:].split('+', 1)  # 맨 앞 '-' 제거 후 '+' 기준 분리
                    if len(parts) == 2:
                        example = f"-{parts[0].strip()}+{parts[1].strip()}"
                    else:
                        example = example_line
                else:
                    example = example_line
                i += 3
            else:
                i += 2

            words.append({'word': word, 'meaning': meaning, 'example': example})

        word_count = len(words)
        return words, word_count

    except Exception as e:
        print(f"Error parsing wordbook '{file_path}': {e}")
        return [], 0


def load_wordbooks(directory):
    """
    지정된 디렉토리(및 하위 폴더)에서 모든 _wordbook.txt 파일을 찾아
    parse_wordbook으로 단어를 읽어 반환합니다.

    Returns:
      wordbooks (dict): {title: [ {word, meaning, example}, ... ], ...}
      word_counts (dict): {title: 단어 개수, ...}
    """
    wordbooks = {}
    word_counts = {}

    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return wordbooks, word_counts

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('_wordbook.txt'):
                file_path = os.path.join(root, filename)
                words, count = parse_wordbook(file_path)
                if count > 0:
                    # 예: filename = "오늘 외울 거!_wordbook.txt"
                    # -> base = "오늘 외울 거!_wordbook"
                    # -> title = "오늘 외울 거!"  (마지막 _wordbook 제거)
                    base = os.path.splitext(filename)[0]  # "오늘 외울 거!_wordbook"
                    if base.endswith('_wordbook'):
                        title = base[:-len('_wordbook')]
                    else:
                        title = base  # 혹시나 _wordbook이 제대로 없을 경우 대비

                    wordbooks[title] = words
                    word_counts[title] = count
                else:
                    print(f"Failed to load wordbook: {filename}")

    return wordbooks, word_counts


def load_wordbooks_with_script_audio(directory):
    """
    (추가) 
    지정된 디렉토리(및 하위 폴더)에서 _wordbook.txt 파일을 찾고, 
    parse_wordbook으로 단어 목록을 얻어두는 동시에,
    동일 폴더에 script.txt, script.wav(또는 script_temp.mp3)가 있으면 그 경로를 함께 저장.

    반환 예시:
    {
      "오늘 외울 거!": {
          "words": [ {word, meaning, example}, ... ],
          "wordbook_path": ".../오늘 외울 거!_wordbook.txt",
          "script_text_path": ".../script.txt" (없으면 None),
          "script_audio_path": ".../script.wav" or ".../script_temp.mp3" (없으면 None)
      },
      ...
    }
    """
    results = {}

    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return results

    for root, dirs, files in os.walk(directory):
        for filename in files:
            # _wordbook.txt 로 끝나는 파일만
            if filename.endswith('_wordbook.txt'):
                file_path = os.path.join(root, filename)
                words, count = parse_wordbook(file_path)
                if count > 0:
                    # 파일명 파싱 -> title
                    base = os.path.splitext(filename)[0]  # "오늘 외울 거!_wordbook"
                    if base.endswith('_wordbook'):
                        title = base[:-len('_wordbook')]
                    else:
                        title = base

                    results[title] = {
                        "words": words,
                        "wordbook_path": file_path,
                        "script_text_path": None,
                        "script_audio_path": None
                    }
                else:
                    print(f"Failed to load wordbook: {filename}")

    # script.txt / script.wav / script_temp.mp3 체크
    for title, info in results.items():
        folder = os.path.dirname(info["wordbook_path"])
        script_txt = os.path.join(folder, "script.txt")
        script_wav = os.path.join(folder, "script.wav")
        script_mp3 = os.path.join(folder, "script_temp.mp3")

        if os.path.exists(script_txt):
            info["script_text_path"] = script_txt

        # 우선순위로 script.wav -> 없으면 script_temp.mp3
        if os.path.exists(script_wav):
            info["script_audio_path"] = script_wav
        elif os.path.exists(script_mp3):
            info["script_audio_path"] = script_mp3

    return results
