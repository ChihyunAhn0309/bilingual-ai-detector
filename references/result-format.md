# 결과와 퍼센트의 의미

## 수치 계약

| 이용 가능한 근거 | 허용되는 수치 | 금지되는 변환 |
| --- | --- | --- |
| 문체를 읽은 관찰만 있음 | 실제 센 문자·문장·반복 횟수 | ‘AI 83%, 사람 17%’처럼 직관을 확률화 |
| 분류기의 binary class probabilities | 정의와 조건을 붙인 AI/Human 보고값 | 실제 작성 이력의 확정 확률로 인증 |
| Human/AI/Mixed 분류 확률 | 세 범주를 그대로 표시 | Mixed를 Human으로 합치거나 버린 뒤 재정규화 |
| 탐지 구간 비중 | 검사 대상 산문 중 의심 구간 비중 | 100에서 빼서 ‘사람 작성 확률’이라 부르기 |
| predicted class + confidence | 해당 클래스의 모델 신뢰도 | 스키마 근거 없이 반대 클래스 확률 생성 |
| logit, perplexity, 곡률, ratio, risk score | 이름·방향·단위를 유지한 원시 점수 | 0~100으로 바꾸면 확률이라고 주장 |
| 적합한 독립 검증·보정 있음 | 검증 분포에 한정한 추정 확률·검증 지표 | 임의 사용자·언어·새 모델까지 일반화 |

모델 정확도, AUROC, 특정 임계값의 precision, 개별 문서 class probability, AI 텍스트 비중은 서로 다르다. 숫자의 표시 정밀도는 증거 정밀도가 아니다. 실제 응답의 원값을 보존하고 사용자 표에는 보통 정수 또는 소수점 한 자리면 충분하다.

확률 합이 반올림으로 99.9나 100.1이 되면 반올림이라고 적는다. 내부 값이 유효 범위를 벗어나거나 합이 맞지 않으면 계산하지 않고 스키마 오류로 표시한다. `null`은 0%가 아니다.

## 한국어: 기본 실행 결과

v3의 `korean_model.py`를 실행해 **사람 작성 추정 확률 X%, AI 작성 추정 확률 Y%**를 실제 반환값으로 채운다. X/Y는 자리표시자이며 임의 숫자를 넣지 않는다. 모델 버전, 정확한 입력 해시, 별도 보정의 기준 분포(AI 50%, 세 장르 균등), 적용 범위 경고를 함께 설명한다. 평가 정확도를 이 문서의 신뢰도로 바꾸지 않는다. 자세한 기준은 [한국어 모델 카드](korean-model.md)에 있다.

보고서 HTML에 `--model-result work/korean-result.json`을 전달하면 입력 해시와 두 클래스 합을 검사한 뒤 실제 수치를 표시한다. 이 값과 문체 관찰, logit 특징 기여도, 문단 삭제 변화량을 구분한다. 문단 삭제 변화량의 단위는 %p이며 문단별 AI 작성 확률이 아니다.

## 실행 실패 또는 적용 불가능으로 실제 측정이 없는 경우

> 이 글만으로 AI 작성 여부를 확정하기 어렵습니다. [주요 관찰]이 있지만 [사람 글에서도 가능한 설명]도 있습니다.
>
> AI 작성 확률: **산출 불가** / 사람 작성 확률: **산출 불가**
> 검사 방식: 원문 분석과 로컬 특징 측정. 외부 탐지 모델은 실행하지 않았습니다.

이어 필요한 만큼 근거 표를 제공한다. 관찰 신호가 적으면 억지로 채우지 않는다. 실제 점수가 필요하면 적용 가능한 무료 로컬 모델을 실행한다. 한국어는 내장 모델을 먼저 실행한다. 모델 손상·잘못된 언어·입력 오류 등 실제 산출 실패가 있으면 이유를 명시한다. 장르 밖이라는 이유만으로 측정한 값이 없었던 것처럼 숨기지 않고 범위 밖 추정이라고 표시한다. 상용 API나 유료 키를 해결책으로 요구하지 않는다. 단순히 퍼센트가 없다는 이유로 분석 전체를 중단하지 않는다.

## 한국어: 세 범주 결과가 있는 경우

다음 숫자는 **표시 형식만 설명하는 가상 예시**다. 실제 분석 결과에 재사용하지 않는다.

| 문서 | 탐지기 보고 AI | Human | Mixed | 해석 |
| --- | ---: | ---: | ---: | --- |
| 한국어 글 A | 65% | 20% | 15% | 이 탐지기는 AI 범주를 가장 높게 분류함 |

`AI 관여 범주(AI+Mixed) 80%, Human-only 20%`는 범주 정의가 이를 허용할 때만 보조 표기로 쓴다. 이것은 ‘본문의 80%를 AI가 작성했다’라는 의미가 아니다. 세 범주 원값도 보여 준다.

표 아래에 탐지기·모델 버전(불명은 불명), 측정 시각, 입력 원문/해시 또는 제출 범위, 언어·장르 적용 조건, 독립 보정 여부를 짧게 적는다. 다수 결과는 각각의 정의를 적고 상충 이유를 설명한다.

## English equivalent

With no measured detector output: “AI-authorship probability: unavailable. Human-authorship probability: unavailable. This is a text-based review, not a calibrated classifier result.” Follow with concrete observations and plausible alternative explanations.

With measured output: “Provider-reported class probabilities: AI …%, Human …%, Mixed …%. These are the named detector's classifications for the submitted version, not proof of its writing history.” Supply model/date/coverage and known validation limits.

## 자체 보정의 요건

보정은 수치를 임의로 보수적으로 낮추는 행위가 아니다. 원점수와 진짜 라벨이 있는 별도 calibration set으로 Platt/temperature/isotonic 등의 변환을 맞추고, untouched test set에서 Brier·log loss·reliability diagram 등을 확인해야 한다. [Guo et al.](https://proceedings.mlr.press/v70/guo17a.html)

검증 데이터의 AI 비율이 실제 사용 환경과 다르면 사후 확률도 달라질 수 있다. 혼합·번역·교정 등 라벨 정의도 일치해야 한다. calibration 도구를 쓰지 않은 결과를 `보정됨`이라 표시하지 않는다. `evaluate.py`는 **평가만 하며 보정 모델을 학습하지 않는다**. v3의 `train_korean.py`는 별도 calibration 그룹에 sigmoid를 실제로 학습했고 그 가중치가 한국어 모델에 포함되어 있다. 영어 체크포인트에는 이 보정을 적용하지 않는다.

## 상세 설명형 기본 출력

1. 문서별 종합 판단과 실제 점수의 의미. 없으면 AI/사람 각각 산출 불가.
2. 글 전반 분석: 구조, 논증·구체성, 목소리, 리듬·반복, 언어별 특성, 출처·이력.
3. 문단별 표: P1… 위치 / 원문 발췌 / 관찰 / AI 유사 해석 / 사람 글의 대안 / 강도·근거 종류. 신호가 없으면 중립 평가.
4. 핵심 근거 상세 설명과 반대 근거. 문서 전체에서 반복된다는 주장에는 실제 여러 위치.
5. 전체 검토 문단 수와 제외·미검토 범위.

긴 글은 채팅에 핵심을 설명하고 원문 전체 하이라이트 HTML을 함께 제공한다. HTML 색과 검토율은 확률이 아니다. 정확한 ledger 계약은 [evidence-protocol.md](evidence-protocol.md)를 따른다. 모델 삭제 실험은 `점수 변화 +12 percentage points`처럼 기록하고 분석자가 붙인 문체 해석과 구분한다. 가상 수치를 실제 결과로 재사용하지 않는다.

영어 로컬 모델은 Human/AI/AI-edited/Humanized 네 범주를 유지한다. AI 관여 합산을 보이면 원래 네 값도 함께 표시한다. 여러 창으로 나뉜 문서에서는 창별 점수를 설명하고, 보정되지 않은 창 평균을 문서 작성 확률로 표시하지 않는다.
