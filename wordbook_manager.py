# wordbook_manager.py

import os

def parse_wordbook(file_path):
    """
    단어장 파일을 파싱하여 단어와 뜻의 리스트를 반환하고, 단어의 개수를 셉니다.
    
    파일 형식:
    단어
    뜻
    단어
    뜻
    ...
    """
    words = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # 단어와 뜻이 번갈아 나오므로 짝수 개의 라인이어야 함
        if len(lines) % 2 != 0:
            raise ValueError("단어장 파일의 형식이 올바르지 않습니다.")
        
        for i in range(0, len(lines), 2):
            word = lines[i]
            meaning = lines[i+1]
            words.append((word, meaning))
        
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
