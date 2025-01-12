# openai_api.py
import openai

def request_radio_script(openai_key, word_list):
    """
    지정된 OpenAI API Key와 단어 리스트를 바탕으로,
    단어들을 모두 활용한 라디오용 영문 대본 + 한글 번역문을 생성해 반환한다.
    """
    # 1) API 키 설정
    openai.api_key = openai_key

    # 2) 프롬프트 구성
    #    요구사항: "단어장의 단어와 '해당 단어를 모두 조화롭게 사용한 라디오 영문 대본과 한글 뜻을 작성해줘.' 문구를 합쳐서 보낸다."
    prompt = (
        "다음 단어들을 모두 사용하여 라디오 영문 대본을 작성하고, 이어서 한글 번역도 함께 작성해줘:\n\n"
        f"{', '.join(word_list)}\n\n"
        "가능한 자연스럽고 매끄럽게 연결된 라디오 대본을 부탁해. 데이터 인풋으로 쓸거라 영문 대본 시작에는 + 기호를 붙이고, 한글 번역 시작에는 -기호를 붙여줘"
    )

    try:
        # 3) ChatCompletion API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",   # 필요 시 다른 모델 이름
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,         # 창의성 제어
            max_tokens=1024,         # 토큰 제한 (필요시 조정)
        )
        
        # 4) 결과 파싱
        script_text = response["choices"][0]["message"]["content"].strip()
        return script_text

    except Exception as e:
        # 에러 발생 시 예외 전달
        raise RuntimeError(f"OpenAI API 호출에 실패했습니다: {str(e)}")
