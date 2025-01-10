# wordbook_manager.py

import os

def parse_wordbook(file_path):
    """
    단어장 파일을 파싱하여 단어, 뜻, 예문의 리스트를 반환하고, 단어의 개수를 셉니다.
    
    파일 형식:
    단어
    뜻
    예문 (선택 사항, 한 줄로 '-example +korean example')
    단어
    뜻
    예문 (선택 사항)
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
            if i+2 < len(lines) and lines[i+2].startswith('-'):
                example_line = lines[i+2]
                # 예문을 '-' 제거 후 '+'로 분리
                if '+' in example_line:
                    parts = example_line[1:].split('+', 1)  # '-' 제거 후 분리
                    if len(parts) == 2:
                        example = f"-{parts[0].strip()}+{parts[1].strip()}"
                    else:
                        example = example_line  # '+'가 없는 경우 그대로
                else:
                    example = example_line  # '+'가 없는 경우 그대로
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
    지정된 디렉토리에서 모든 단어장 파일을 로드하여 반환합니다.
    
    Args:
        directory (str): 단어장 파일들이 저장된 디렉토리 경로.
    
    Returns:
        dict: 단어장 제목을 키로 하고 단어 리스트를 값으로 하는 딕셔너리.
        dict: 단어장 제목을 키로 하고 단어 수를 값으로 하는 딕셔너리.
    """
    wordbooks = {}
    word_counts = {}
    
    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return wordbooks, word_counts
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            words, count = parse_wordbook(file_path)
            if count > 0:
                title = os.path.splitext(filename)[0]
                wordbooks[title] = words
                word_counts[title] = count
            else:
                print(f"Failed to load wordbook: {filename}")
    
    return wordbooks, word_counts
