# 기존 탐지 스킬과 humanizer 검토

확인일: 2026-10-03. 다음 6개 공개 스킬의 원저자 저장소/원문을 읽고 비교했다. 외부 스킬을 설치하거나 그 명령을 실행한 것이 아니다. 아래는 자체 작성한 비교이며 기존 스킬 본문을 복제하지 않았다. 인기도·별 개수·벤치마크 없는 숫자는 탐지 성능의 근거가 아니다.

| 공개 스킬 | 실제 역할 | 채택한 점 | 채택하지 않은 추론 |
| --- | --- | --- | --- |
| [Valpep/wiki-ai-detector](https://github.com/Valpep/wiki-ai-detector/blob/main/SKILL.md) | 어휘 밀도·의미 과장·정형 구조 등의 문체 체크리스트 | 단어 하나보다 문맥과 반복 구조를 보는 관찰 | 특정 어휘 개수나 구조를 강한 저자 판별력으로 고정하는 방식 |
| [hannsxpeter/authenticity-check](https://github.com/hannsxpeter/authenticity-check/blob/main/SKILL.md) | 0~100 자연스러움 판단과 구간 이유, 별도 Unicode 관찰 | 원문 위치·대안 설명·문자 코드 확인, 분석과 편집 분리 | 자연스러움 점수의 작성 확률화, 문체 밀도를 AI-first/Mixed 이력으로 확정 |
| [mattc95/ai-detector-skill](https://github.com/mattc95/ai-detector-skill/blob/main/SKILL.md) | GPTHumanizer API에 의존하는 여러 범주 분류 | 실제 반환 확률·오류·미완료 구분 | 스킬 자체에 학습 모델이 내장되었다거나 API 없이 같은 확률을 산출한다는 추정 |
| [lynote-ai/ai-text-detector](https://github.com/lynote-ai/ai-text-detector/blob/main/SKILL.md) | 로컬 CLI 실행 후 score·confidence·signals·caveats 보고 | 재현 가능한 실행 경로와 근거 중심 출력 | 반환 score를 한국어에도 보정된 저자 확률이라고 간주 |
| [aragossa/ai-tell-detector](https://github.com/aragossa/ai-tell-detector/blob/main/en/ai-tell-detector/SKILL.md) | 영어/러시아어 문체 패턴 검토 | 원문 행에 연결된 관찰과 단일 점수의 한계 | 영어·러시아어 규칙을 한국어 검증 성능으로 확대 |
| [resemble-ai/detect-skill](https://github.com/resemble-ai/detect-skill/blob/master/SKILL.md) | 미디어와 별도의 text detection API 작업 | 완료된 응답만 해석, predicted class의 confidence와 AI 확률 구분 | 미디어 점수의 텍스트 적용, 업체 자체 수치를 독립 검증 성능으로 인용 |

Resemble 스킬의 text confidence는 예측한 클래스에 대한 신뢰도라고 설명되어 있다. `human, confidence=0.97`을 읽었을 때 AI 97%로 반전하는 오류를 피한다. 반대 클래스 확률은 API 정의를 확인하기 전 자동 생성하지 않는다. 한국어 범위도 별도 확인한다.

## 로컬 humanizer 계열에서 얻은 점

현재 환경의 `bilingual-humanizer`, `humanizer`, `humanizer-ko`, `humanizer-kr`, `korean-humanizer`를 관련 부분 중심으로 비교했다. 이들은 자연스러운 문장, 번역투·반복·정형 구조를 다루는 편집 지침이다. 일부 지침에 연구 수치가 있어도 편집 규칙의 탐지 정확도를 검증한 것은 아니다.

- `bilingual-humanizer`의 작성 이력·탐지 점수·자연스러움 구분을 유지한다. 관련 문서의 원출처를 다시 확인했으며 기존의 실측 사례를 새 스킬의 벤치마크로 가져오지 않았다.
- 한국어 계열의 어미·조사·명사화·띄어쓰기 관찰은 장르별 검토 질문으로 활용한다. ‘다양한’, ‘해당’, 쉼표나 특정 어미를 금지어 또는 저자 증거로 삼지 않는다.
- KatFishNet의 94.88을 모든 한국어 문서의 accuracy로 설명하는 것은 원 논문 표 3과 맞지 않는다. 실제 지표와 장르를 [연구 검토](research-methods.md)에 명시한다.
- 자연스럽게 고친 글의 생성 이력은 사라지지 않는다. humanizer가 제거하는 문체 패턴과 탐지기가 판단하려는 작성 과정은 동일한 목표 변수가 아니다.

## 최종 설계 판단

문체 체크리스트, 실제 분류 모델, 외부 API, 생성 과정 증거를 서로 대체하지 않는다. 편집 결과를 칭찬하거나 의심을 강화하기 위해 퍼센트를 움직이지 않는다. 스킬의 강점은 **언어별 관찰·실제 측정·수치 해석·오류 검증을 일관되게 수행하는 절차**에 있다. 프롬프트 자체가 새 고성능 탐지 모델을 학습했다는 주장은 하지 않는다.
