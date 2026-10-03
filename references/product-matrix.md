# 상용 탐지기 비교: 공개 원리·언어·점수

확인일: **2026-10-03**. 11개 제품의 공식 자료를 직접 확인했다. 업체가 설명한 원리·성능은 업체 주장으로 구분한다. 비공개 구조·가중치·임계값을 역설계하거나 모두 실측한 자료가 아니다. ‘언어 지원’과 ‘해당 언어에서 독립적으로 검증된 정확도’는 다르다. 기능과 UI는 바뀔 수 있으므로 실제 보고서 버전의 설명을 우선한다.

| 제품 | 공개 원리·출력 의미 | 영어·한국어 적용 | 이 스킬의 처리 |
| --- | --- | --- | --- |
| GPTZero | [2026 기술 보고서](https://arxiv.org/html/2602.13042v1)는 지도학습, Human/AI/Mixed 계층 분류, 문서·문장 공동 학습을 설명한다. [FAQ](https://gptzero.me/faq)의 `class_probabilities`는 범주 확률이다. 정확한 구조·하이퍼파라미터는 비공개다. | [공식 목록](https://support.gptzero.me/articles/1682612063-what-languages-does-gptzero-support)에 영어·한국어 포함. | 초기 perplexity/burstiness 설명만으로 현행 방식을 설명하지 않는다. 세 범주를 보존한다. |
| Turnitin | [공식 가이드](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report): 검사 가능한 긴 산문 중 AI로 의심되는 텍스트의 비중이다. 1~19%는 별표 처리한다. | 같은 문서에 영어·스페인어·일본어·아랍어, 300~30,000단어 조건이 있다. 한국어는 이 목록에 없다. | 문서 전체의 AI 작성 확률로 바꾸지 않는다. 0%도 인간 작성 인증이 아니다. |
| Copyleaks | [AI Logic](https://docs.copyleaks.com/concepts/features/ai-logic)은 AI·인간 패턴의 통계 비교와 구간 설명을 제공한다. 이것이 전체 분류기 공개는 아니다. | [언어 목록](https://docs.copyleaks.com/reference/actions/miscellaneous/ai-detection-supported-languages/)에 영어·한국어. 설명 기능 AI Logic의 6개 언어에는 한국어가 없다. | 한국어에서 설명 필드가 없다는 사실을 탐지 실패나 인간 판정으로 해석하지 않는다. 점수는 사용한 API 필드 정의를 확인한다. |
| Originality.ai | [점수 설명](https://originality.ai/blog/score-meaning): Multi Language confidence와 AI Allowance 설정이 구분된다. Allowance의 허용 비율과 예측 confidence는 서로 다르다. | [Multi Language 안내](https://help.originality.ai/en/article/multiple-languages-how-to-use-multi-language-ai-detection-13e5plo/)에 영어·한국어. 비영어는 해당 모델을 확인한다. | ‘15% allowance’와 ‘AI일 확률 15%’를 혼동하지 않는다. confidence도 AI 단어 비중이 아니다. |
| Pangram | [방식 설명](https://www.pangram.com/knowledge-hub/how-does-pangram-work)은 많은 학습 패턴을 이용하는 신경망 분류기를 설명한다. 단일 문장부호만으로 판별하지 않는다고 한다. | [언어 목록](https://www.pangram.com/knowledge-hub/what-languages-does-pangram-work-on)에 영어·한국어. | 설명상의 공간·군집 비유를 실제 공개된 모델 구조로 확대하지 않는다. 사용 버전의 AI-assisted·구간 수치를 구분한다. |
| Winston AI | [공식 언어 안내](https://help.gowinston.ai/getting-started/which-languages-does-winston-ai-work-with)는 AI 텍스트 탐지의 지원 범위와 언어별 성능 차이를 설명한다. | 영어 포함, 확인한 목록에 한국어 없음. 다른 기능의 언어 범위와 다를 수 있다. | 한국어 입력을 처리했다는 사실만으로 유효한 한국어 탐지라고 주장하지 않는다. 상세 구조는 이 조사에서 확인되지 않았다. |
| ZeroGPT | [FAQ](https://www.zerogpt.com/faq)는 토큰 패턴, burstiness, entropy, 앙상블 특징과 점수·구간 표시를 설명한다. | 광범위 다국어 지원을 주장한다. 한국어별 독립 검증은 이 조사로 확인되지 않았다. | GPTZero와 다른 업체다. 공개 특징 목록을 고정 수식이나 독립 검증 성능으로 바꾸지 않는다. |
| Sapling | [공식 탐지기](https://sapling.ai/ai-content-detector)는 토큰 단위 분류와 문장별 perplexity를 상호 보완적인 방법으로 설명한다. | 영어 예시와 안내가 있다. 이 페이지에서 한국어의 명시적 검증 범위는 확인하지 못했다. | 전체 점수와 문장 하이라이트를 구분한다. ‘확인 못함’은 ‘미지원 확정’이 아니다. |
| QuillBot | [공식 페이지](https://quillbot.com/ai-content-detector)는 예측 가능성·구조 변화·반복을 설명하고 0~100% 결과, 최소 80단어를 안내한다. | 다국어 지원을 설명한다. 한국어별 성능과 사용하는 버전은 별도로 확인해야 한다. | 현재 화면의 범주·분모·설명을 기록한다. 글 비중인지 분류 likelihood인지 불명확하면 추정해 통일하지 않는다. |
| Grammarly | [공식 가이드](https://support.grammarly.com/hc/en-us/articles/28936304999949-AI-Detector-user-guide)는 언어 패턴과 구간 분석 및 AI로 보이는 텍스트의 비율을 설명한다. | 이 문서만으로 한국어별 검증 성능을 확정하지 않는다. | Authorship 과정 기록과 사후 텍스트 분류를 분리한다. AI 교정·재작성의 영향을 고려한다. |
| GPT킬러 | [공식 매뉴얼](https://manual.muhayu.com/montly-gpt-killer-labs)은 Transformer Encoder/공개 LLM을 이용한 생성확률 추론과 텍스트 특성 분석, 구간별 탐지를 설명한다. | 한국어 서비스를 확인했다. 영어 세부 조건은 이 조사에서 확정하지 않았다. | 결과 취합은 어절 기반이다. 표절검사를 함께 선택했을 때 합산될 수 있어 검사 설정을 확인한다. 400자 구간은 매뉴얼의 예시이지 고정 규격이 아니다. |

## 실행 기록에 남길 항목

제품·모델/버전·플랜(알 수 있는 경우), 실제 시각, 제출 원문/해시, 언어, 검사 길이, 추출/전처리, 전체/부분 검사, 원시 값, 값의 정의, 정상 완료 여부, 오류·보류·잘림 여부를 남긴다. 모델 버전을 모르면 모른다고 쓴다. 알려진 서드파티 통계나 과거 같은 파일명으로 실시한 결과를 새 원문의 실측으로 재사용하지 않는다.

## 비용 없는 보고서 해석

v2는 저장된 GPTZero 응답의 `class_probabilities`만 해석한다. 상용 API 실시간 호출은 제거했고 기존 명령도 요청 전에 실패한다. 무료 플랜, 시험판, API 크레딧을 비용 보장의 근거로 삼지 않는다. 위 제품들은 연구·비교 대상이며 이 스킬이 모두 실행하거나 무료 복제하는 서비스가 아니다.

GPTZero의 [공식 설명](https://support.gptzero.me/articles/9585228410-how-do-i-interpret-burstiness-or-perplexity)은 2023년 가을 이후 perplexity/burstiness를 사용하지 않는다고 명시한다. 과거 개념만 재현해 현행 GPTZero를 구현했다고 주장하지 않는다. [2026-09-24의 GPTZero 4o 발표](https://gptzero.me/news/introducing-gptzero-4o/)처럼 버전이 바뀌면 과거 비교 결과도 현행 성능으로 확대할 수 없다.
