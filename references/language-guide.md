# 한국어·영어 분석 기준

이 문서의 판단 절차는 스킬의 설계 원칙이다. 연구에서 관찰한 집단 차이를 개별 글의 확률이나 고정 임계값으로 바꾸지 않는다.

## 한국어

한국어 원문으로 판단한다. 영어 번역본을 검사해서 원래 한국어의 작성 이력을 추론하지 않는다. 한글 음절 수, 공백 기준 어절 수, 형태소 수, 모델 토큰 수를 구분한다. 영어 300단어 조건을 한국어 300자 조건으로 바꾸지 않는다.

| 관찰 | 확인할 내용 | 오탐을 막는 대안 설명 |
| --- | --- | --- |
| 띄어쓰기·문장부호 | 같은 구문의 띄어쓰기 선택, 쉼표의 위치와 기능, 연결어미 뒤 쉼표 | 교열, 기관 편집 지침, 영어 번역문, 열거·인용문 |
| 품사 조합 | 형태소 분석기를 실제 실행한 경우에만 품사 n-gram 다양성을 측정 | 전문 분야 어휘, 형태소 분석 오류, 길이 차이 |
| 종결어미·주체 | 높임·시제·주체·설명의 목적과 어미가 맞는지 | 공문·논문은 일관된 격식체가 정상 |
| 명사화·번역투 | ‘~에 대해’, ‘~을 통해’, 추상명사 연결이 내용을 흐리는지 | 법률·학술 관습, 번역, 편집자의 문체 |
| 구조 반복 | 문단별 도입·열거·결론이 내용과 무관하게 반복되는지 | 과제 형식, 보고서 템플릿, 교육받은 논설 구조 |

KatFishNet은 띄어쓰기, 품사 조합, 문장부호를 연구한 실제 분류 방식이다. 단순 쉼표 개수 세기는 그 재현이 아니다. 논문 표 3의 94.88은 에세이 punctuation 모델의 평균 AUROC×100이며, 시 73.10·초록 75.62와 구분한다. 본 스킬의 정확도가 아니다. [논문 표 3](https://aclanthology.org/2025.acl-long.1030.pdf)

로컬 프로파일러는 형태소 분석을 실행하지 않는다. `surface_type_token_ratio`는 공백 단위 표면형의 다양성으로, 품사 다양성이나 정보 엔트로피가 아니다. 띄어쓰기 오류 수와 ‘정상적인 쉼표 비율’도 계산하지 않는다.

## English

Assess the original language, genre and intended audience. Repeated transitions, vague attribution, inflated significance, uniform structure and redundant restatement can justify editorial observations. They cannot by themselves identify the authoring process.

In particular, do not penalize simple vocabulary, low sentence-length variation, formulaic exam answers or careful grammar as evidence of AI. Consider language learning, professional editing, accessibility choices and institutional templates without guessing which applies to the author. A 2023 study documented false-positive bias on its non-native English samples; those rates do not describe all current products. [Liang et al.](https://arxiv.org/abs/2304.02819)

Treat familiar “AI words” and punctuation as weak context-dependent observations. Check a cluster against what the passage is doing. A real example, emotional anecdote, typo or fragmented sentence can also be generated. Do not ask an LLM whether it remembers generating the passage; conversational recognition is not provenance.

## 혼합 언어·짧은 글·변형된 글

- 한국어 문장 속 영어 제품명은 별도 영어 문서가 아니다. 독립적인 영어 문단이 충분히 있으면 부분별로 검토하되 문맥과 경계를 유지한다.
- 프로파일러의 Hangul/Latin 비중은 문자 구성 정보다. Latin 문자를 쓴다고 영어라는 뜻은 아니다. 언어 판단을 직접 확인한다.
- 짧은 글은 정보가 부족하다. 모든 탐지기에 통용되는 최소 길이를 만들지 말고 해당 도구의 요건을 적용한다. 분량이 길다는 이유만으로 신뢰도가 높다고 단정하지 않는다.
- 인용문·코드·목록·표·시·OCR 오류는 일반 산문용 모델의 적용 범위를 벗어날 수 있다. 단락 단위 확률을 낼 때도 별도 검증이 필요하다.
- 사람이 쓴 초안을 AI로 교정한 경우, AI 초안을 사람이 고친 경우, 번역·공동 집필은 구분할 가설이다. 텍스트만으로 그 방향을 확정하지 않는다.
- humanizer 처리로 표면 신호가 줄어도 작성 이력은 바뀌지 않는다. 반대로 격식을 갖춘 인간 글에 신호가 많아도 AI 작성이 입증되지 않는다.
- 제로폭 문자·BOM·결합문자·방향 제어 문자에는 정상적인 이유가 있다. 발견한 코드포인트와 위치만 보고하며 이를 AI 워터마크라고 부르지 않는다. 통계적 워터마크 검증은 해당 생성 체계와 검출기, 키·토크나이저 등 별도 조건이 필요하다.

## 증거 표 작성

`위치 | 원문 발췌 | 관찰 | 사람 글에서도 가능한 설명 | 판단에 미치는 한계`

위치는 프로파일러의 1-based line 또는 0-based Python Unicode code-point offset을 명시한다. UTF-16 위치와 혼동하지 않는다. 알려진 작성 이력은 별도 표에 `제공된 기록 / 검증한 범위 / 확인할 수 없는 범위`로 적는다. 사후 생성한 파일 해시는 입력 동일성에 관한 것이며 작성자나 작성 시각을 입증하지 않는다.


## 한국어 모델과 언어 관찰의 분리

v3 한국어 분류기는 [한국어 모델 카드](korean-model.md)에 적힌 문자 패턴을 학습한다. 쉼표 개수나 합니다체를 규칙으로 합산해 확률화하는 방식이 아니다. 한국어 원문에 실행하고 사람이 쓴 경우의 대안 설명을 별도로 유지한다. 학습 어휘 기여, 문단 삭제 민감도와 분석자의 문체 관찰을 구별한다.
