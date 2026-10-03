# 실행·평가·보정 절차

## 내장 도구 실행

기본 profile/evidence/evaluate 도구는 Python 표준 라이브러리로 실행한다. 선택적 로컬 분류 모델만 torch/transformers/safetensors와 공개 가중치가 필요하다. 스킬 경로를 기준으로 입력·출력의 실제 경로를 지정한다. UTF-8 텍스트를 사용하고 PDF/DOCX 추출 품질은 먼저 확인한다.

```text
python scripts/detector.py inspect manuscript.txt --out work/profile.json
python scripts/evidence.py index manuscript.txt --out work/index.json
python scripts/evidence.py validate manuscript.txt work/ledger.json --out work/evidence.json --html work/review.html
python scripts/detector.py import-gptzero response.json --out work/imported.json
python scripts/local_model.py manuscript.txt --language en --explain --out work/local.json
python scripts/evaluate.py labeled-scores.jsonl --threshold 0.5 --data-kind real --out work/metrics.json
python -m unittest discover -s scripts -p "test_*.py" -v
```

실시간 상용 API 호출은 금지하고 코드에서도 차단한다. `gptzero --allow-upload`도 네트워크 요청 없이 실패한다. 공개 모델 다운로드와 공개 벤치마크 자료 읽기만 별도 HTTP 도구로 허용한다. 원문은 외부 탐지기에 전송하지 않는다. 기존 출력·입력 파일은 덮어쓰지 않는다.

저장된 GPTZero 응답의 세 범주가 없거나 숫자가 잘못되면 실패한다. 구형 응답의 단일 점수는 대체하지 않는다. import는 입력 바인딩을 인증하지 않는다. 근거 위치의 일치와 보고서 진위는 별개의 검증이다.

## 레이블과 평가 자료

먼저 목표 변수를 정의한다. `AI-only vs Human-only`와 `AI involvement vs No AI involvement`는 다르다. 사람이 쓴 초안의 맞춤법 교정, 번역, AI 패러프레이즈, AI 초안의 사람 편집은 별도 이력 라벨을 보존한다. 이진 평가로 옮길 때는 규칙을 사전에 문서화한다. 판별하기 어려운 실제 사례를 편의상 0이나 1로 라벨링하지 않는다.

권장 데이터 항목: 문서 ID, 원문 해시, 원본 문서/작성자/주제/프롬프트를 연결하는 group ID, 언어, 장르, 길이, 생성/편집 모델과 버전, 생성 설정, 변형 종류·횟수, 이력 증거, 탐지기 버전, 원점수·확률, 완료/오류 상태. 작성자 관련 속성은 당사자가 제공한 평가 목적 자료가 있을 때만 사용한다.

**JSONL 예시는 합성 형식 설명용이며 실제 성능 자료가 아니다.** 아래처럼 한 행에 한 JSON 객체를 넣는다.

```json
{"doc_id":"demo-human-1","group_id":"source-1","language":"ko","genre":"essay","provenance":"synthetic test fixture","detector_version":"demo-v1","split":"test","label":0,"p_ai":0.2}
{"doc_id":"demo-ai-1","group_id":"source-2","language":"en","genre":"essay","provenance":"synthetic test fixture","detector_version":"demo-v1","split":"test","label":1,"p_ai":0.8}
```

평가 스크립트는 이진 목표의 `p_ai`만 받는다. Turnitin 의심 비중이나 raw perplexity를 넣지 않는다. GPTZero 세 범주 결과는 검증 목표에 적합한 변환을 사전에 정의한 경우에만 사용한다. 실패한 검사는 별도 집계해 누락 비율을 보고하며, 성공한 것만 골라 전체 성능처럼 발표하지 않는다.

## 데이터 분리와 범위

1. 학습, 모델/특징 선택, calibration, 최종 test를 분리한다. 같은 원본의 여러 문단·번역·humanizer 결과가 다른 split에 들어가면 누수다. 작성자·출처·주제·프롬프트 연결을 하나의 group으로 묶는다. 제공 도구는 동일 group의 calibration/test 중복을 거부하지만, 숨겨진 중복·학습 데이터 누수까지 자동 검출하지 않는다.
2. 영어·한국어를 나누고 장르·길이·모델·생성 시기·변형 방식별로 평가한다. 혼합 언어, 짧은 메시지, 논문 초록, 공문, 비원어민 영어, OCR, 사람이 교열한 인간 글 등 어려운 음성 표본을 포함한다.
3. 알려지지 않은 생성모델·humanizer·도메인을 테스트에 남긴다. 같은 탐지기로 고른 문장만 모아 평가하지 않는다. 기존 공개 데이터와 신규 비공개 holdout을 구분한다.
4. API 결과는 원문 해시·버전·실행 시각을 기록한다. 모델이 바뀌면 같은 calibration을 유효하다고 가정하지 않는다.

## 지표 해석

- `false_positive_rate`: 인간 라벨 중 AI로 표시한 비율. `recall`: AI 라벨 중 검출한 비율. `precision`: AI로 표시한 것 중 실제 AI 라벨 비율로, 데이터의 AI 비율에 영향을 받는다.
- AUROC는 순위 구분 능력이다. 잘 보정된 90% 확률을 내는지, 선택 임계값의 오탐률이 낮은지는 별도다. 동점은 0.5 기여로 계산한다. 한 클래스만 있는 집단에서는 AUROC를 산출하지 않는다.
- Brier, log loss, reliability bins, ECE를 같이 본다. ECE는 binning과 표본 수에 민감하다. 스크립트는 10개 동일 폭 bin을 사용하고 log loss에는 1e-15 수치 하한을 쓴다.
- 오탐 0건은 실제 오탐률 0%의 보장이 아니다. FPR과 recall에 95% Wilson 구간을 출력한다. 문서가 서로 종속적이면 이 구간의 독립성 가정이 깨지므로 group bootstrap 등으로 평가한다.
- 저오탐 사용 사례는 TPR@FPR 1% 또는 0.1%를 추가 평가한다. 임계값은 calibration 자료에서 선택하고 고정한 뒤 test에서 실제 달성 FPR·TPR·구간을 함께 보고한다. 희귀 오탐 검증에는 충분한 인간 표본이 필요하다. 본 스크립트는 임계값 선택이나 TPR@FPR 최적화를 수행하지 않는다.
- 판정 보류를 사용한다면 coverage와 보류 표본을 포함한 오류 보고를 함께 남긴다. 낮은 coverage에서의 정확도를 전체 문서 성능처럼 소개하지 않는다.

## 확률 보정과 결합

사후 보정은 독립 calibration 표본과 명시적 라벨 정의를 전제로 한다. Platt/temperature/isotonic 등은 목표와 모델에 맞춰 선택하고 untouched test에서 확인한다. v3는 `train_korean.py`로 학습한 한국어 sigmoid 보정 가중치를 제공한다. 자료·분할·실제 지표는 [korean-model.md](korean-model.md)와 그 실행 JSON을 확인한다. 영어 로컬 모델은 여전히 독립 보정되지 않았다.

여러 탐지기를 결합하려면 동일 입력의 결과, 같은 목표 변수, score 방향·버전, 결측 처리, 상관된 오류를 고려한 학습·보정이 필요하다. 각 업체의 공개 확률 또는 구간 비중을 평균하는 것은 그 대체물이 아니다. 언어별 가중치도 데이터 없이 정하지 않는다.

## 출시·후속 검증 기준

검증 범위와 실제 측정 여부는 [성능 비교](performance-comparison.md)와 [검증 기록](verification.md)에 구분한다. 소규모 영어 pilot이나 과거 공개 결과를 범용 한국어·영어 정확도로 확대하지 않는다. 정확도를 공표하려면 독립적인 실제 holdout, 라벨 이력, split manifest, 실행 기록, 언어/장르별 지표, 오류 사례, 모델 버전을 함께 공개 가능한 형태로 남긴다. 검증된 범위를 벗어난 문서에는 보류 또는 범위 밖 표시를 한다.

통과한 단위 테스트는 소프트웨어 불변 조건의 근거다. 합성 응답/합성 라벨에서의 수치를 detector accuracy로 홍보하지 않는다.

이번 제작의 출처 대조·테스트·수정 사항은 [검증 기록](verification.md)에 남겼다.
