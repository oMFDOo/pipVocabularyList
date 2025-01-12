# 삡(Pip) 단어장!

![네? 왜 없졍](./documents/logo.png)
> 영어에 꽂혀버려 영어 어플만 3개 구독중임에도 느껴진 갈망을 모앗다!

> 진짜 갑자기 너무 갖고 싶은 기능을 3일간 구현하였다!!

<br><br>

## 대강 기능 어필!

### 😂 PC용 나만의 괜찮은 단어장 없나?
: 내가 외울거 외운거 딱딱 정리해서 보고싶은데 방법없나?

![네? 왜 없졍](./documents/단어구경.gif)
 - 메모장에 간단히 적으면 단어장 출력 완성!
 - 부지런한 당신 예문도 넣었다면 그것도 모아준다!
 - 화면 살짝 가리고 단어만 먼저 뜻만 먼저 골라 보자!
 - 뭐야 뜻이 하나 더 있어? 수정 가능~!

<br><br>

### 링딩동마냥 반복식 주입하면 외워지지 않을까? 🤔
: 좋아 학습을 해보자!!

![네? 왜 없졍](./documents/학습%20시작.gif)
> 이 쪼꼬미는 뭘까?


<br><br>

### 무한 반복 쪼꼬미 단어장 등장!! 🤷‍♀️
: 화면 구석 조그마하게 항상 떠있는 나만의 단어장!

![네? 왜 없졍](./documents/pip%20단어.gif)

 - 단어도 읽어줘~
 - 계속 반복도 해줘~
 - 예문도 보여줘~
 - 출근해서 퇴근까지 틀어놓으면 뭐지 들어는 봤는데? 가능하지 않을까!!
 

<br><br>

### 👻 자만하는 나를 위한 실전 검증!
: 어디 직접 외운 단어로 구성된 라디오를 알아듣는지 테스트 해보시지!

[Link text](https://github.com/user-attachments/assets/3427885d-b1d0-4c81-8a94-967d6fe900fc)
> 아닛! 단어장을 선택해서 라디오를 만들어준다구? (클릭해서 영상을 확인하세요!)

<br><br>


[Link text](https://github.com/user-attachments/assets/3ad33cfe-e5ae-4c79-94e6-1087fd67d425)

 > 좋아! 직접 라디오를 생성해보자!! (클릭해서 영상을 확인하세요!)
 - 대본 생성에 [OpenAI API](https://openai.com/index/openai-api/)가 들어서 5$ 정도만 구매해도 한참 쓴다...!! 이건 투자할 수 있따!
 - 단어를 고르고, 생성하기 누른 뒤 새로고침을 연타하세요!
 - 한글/영어/단어 아는게 많을 수록 인터페이스가 단촐할 것입니다...
 - 계속 다른 대본을 만들어서 검증해보세요!

<br><br>

### 윈도우, 맥, 리눅스 지원 🙊
|구분||||
|:--:|:--:|:--:|:--:|
|Windows|![image](https://github.com/user-attachments/assets/3f7bb958-0725-44f0-ba7f-e931340bb333)|![image](https://github.com/user-attachments/assets/3360e6cb-81f9-4c1f-a4e4-1315cf1e5eaf)|![image](https://github.com/user-attachments/assets/61337217-aca0-4c9a-bf59-48599d71bf8c)|
|Mac|내일 찍어야징|||
|Linux|![Screenshot From 2025-01-13 00-23-15](https://github.com/user-attachments/assets/61de2993-0cb3-435e-b6b5-08e1d1875b22)|![Screenshot From 2025-01-13 00-22-31](https://github.com/user-attachments/assets/7efb828b-f9d8-48ed-9173-4e6d251531ea)|![Screenshot From 2025-01-13 00-23-23](https://github.com/user-attachments/assets/8bbaf022-395d-4523-af00-d01237b0cd0b)|








## 실행법 및 주의사항

### 설치 및 실행
 1) **[Conda](https://www.anaconda.com/download) 다운로드**
 
 2) **코드 가져오기** <br>
  : `zip` 다운로드든 어떻게든 가져오기
 ```sh
 git clone https://github.com/oMFDOo/pipVocabularyList.git
 ```


 3) **가상환경 생성**
 ```sh
 conda env create -f enviroment.yml
 ```

 3) 코드 실행
 ```sh
 python main.py
 ```

<br>

### ❗❗❗단어 추가❗❗❗
: 단어를 파일로 추가할 때는 이렇게 써야한다..! 둘 중 하나의 양식만 충족하면 된다!<br> 또한 파일명이 단어장 이름으로 추가된다. 그래도 제목은 수정 가능하니 안심!

1) **단어만 추가**
```py
# 영단어
# 뜻
ameliorate  
개선하다, 향상시키다
```


2) **단어+예문 추가**
```py
# 영단어
# 뜻
# -영문 예문 +한국어 뜻
ameliorate  
개선하다, 향상시키다  
-The manager worked to ameliorate the company+매니저는 회사를 개선하기 위해 노력했다  
```



<br><br>


## 미래의 포부!

### 내가 더 부지런할 때 만들것
 > 정말 취미로 만든것이라, 당분간 다른 개인 공부의 문제로 개발 중단함

- [ ] 단어 생성 : 테마를 고르고 단어를 생성해주는 기능
- [ ] pip 고도화 : 불투명도나 다크모드 조정 있으면 좋을 듯 하다
- [ ] 볼륨조절 : 윈도우는 시스템 볼륨 조절 가능한데 mac이나 linux는 어렵단 말이다!
- [ ] 예문생성 : 솔직히 예문까지 적어넣기 귀찮으니까...
- [ ] 인종추가 : 호주, 영국, 남성/여성 옵션 추가 - 이건 너무 무거워 질 거 같아서 정말 고민
- [ ] API키 저장 : 매번 붙여넣기 귀찮타
- [ ] 무료 전환 : 대본 삽입 기능만 있다면 완전 무료가 되긴하니까...
- [ ] 단어 삭제 : 파일 exe로 뽑아서 안 쓸거라 지금은 문제 없지만 꽤 거슬릴 일
- [ ] 창끄기 : 없이도 잘 갖고논게 용함
- [ ] mac 다크모드 연동 : mac에 다크모드 설정되어 있으면 창 일부가 까매지고 글자는 안 보이는 훌륭한 일들이 생긴다.
