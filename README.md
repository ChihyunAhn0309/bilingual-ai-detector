# Bilingual AI Detector

한국어·영어 글의 **AI/사람 분류 추정값과 원문 근거**를 함께 검토하는 Codex skill입니다. 한국어 모델은 포함되어 있으며 Python 표준 라이브러리만으로 오프라인 실행됩니다. 영어 모델은 선택적으로 내려받아 실행합니다. 상용 탐지 API, 유료 크레딧, 호스팅 추론 서비스는 사용하지 않습니다.

An offline Korean/English AI-text analysis skill with estimated class probabilities, exact passage evidence, human counterexplanations, and reproducible evaluation. **It does not certify authorship or guarantee perfect detection.**

현재 버전은 **3.1.0**입니다. 제작과 별도 대화에서 검수했고, 발견된 보고서·입력·결과 검증·프로세스 잠금 문제를 수정한 뒤 다시 시험했습니다. [독립 검수 결과](references/review-public.md)와 [검수한 파일 해시](references/reviewed-files-public.json)를 공개합니다.

## 제공 기능

| 기능 | 한국어 | 영어 |
| --- | --- | --- |
| 모델 | 포함된 약 2 MB 문자 TF-IDF/로지스틱 분류기 | 선택적 약 1.74 GB DeBERTa 체크포인트 |
| 출력 | Human/AI 두 클래스, 별도 holdout sigmoid 보정 | Human/AI/AI-edited/Humanized 네 클래스, 별도 보정 없음 |
| 원문 근거 | 학습 특징의 signed logit 기여와 정확한 위치, 문단 삭제 변화 | 문단 삭제 전후 모델 민감도 |
| 전체 문서 설명 | 스킬이 모든 문단을 읽어 관찰·판단 이유·사람 작성 대안을 작성 | 동일 |
| 긴 문서 | 입력 전체 사용, 학습 길이 밖 경고 | 전체 토큰 창 검사, 창 평균을 문서 작성 확률로 표시하지 않음 |

CLI만으로 상세한 자연어 비평이 자동 작성되는 것은 아닙니다. 스킬을 사용하는 에이전트가 글을 읽고 근거 기록을 작성하며, 스크립트는 모델 수치와 인용 좌표·검토 범위를 확인합니다. Codex/ChatGPT 사용 자체의 요금은 이 프로젝트가 정하지 않습니다.

## 설치와 사용

Python 3.10 이상이 필요합니다. Windows 제작·검수 환경은 Python 3.13입니다. 먼저 저장소를 내려받습니다.

```sh
git clone https://github.com/ChihyunAhn0309/bilingual-ai-detector.git
cd bilingual-ai-detector
python -B -X utf8 scripts/korean_model.py examples/korean.txt --genre unknown --out work/korean-result.json
```

Windows에서는 `python` 대신 `py -3.13`을 사용할 수 있습니다. 출력 파일은 기존 기록을 덮어쓰지 않습니다. 다시 실행할 때는 새 출력 이름을 지정합니다. 한국어 추론에는 `pip install`이나 외부 모델 다운로드가 필요 없습니다.

Codex skill로 사용하려면 저장소 폴더를 `~/.codex/skills/bilingual-ai-detector`에 두세요. `CODEX_HOME`을 따로 설정했다면 그 아래 `skills/bilingual-ai-detector`를 사용합니다. 기존 설치에 변경사항이 있으면 먼저 백업합니다. Codex에서 다음과 같이 요청합니다.

> $bilingual-ai-detector 이 글의 사람/AI 작성 추정 확률을 실제 모델로 계산하고, 모든 문단의 원문 근거와 사람 작성 대안 설명을 보여줘.

새 스킬을 아직 찾지 못하면 새 대화에서 실행합니다. [SKILL.md](SKILL.md)가 실행 지침입니다. 보고서의 인용 검증과 HTML 생성 절차는 [근거 형식](references/evidence-protocol.md)을 따릅니다.

### 선택적 영어 실행

```sh
python -m pip install -r requirements-english.txt
python scripts/prepare_local_model.py models/tropa-mini
python -B -X utf8 scripts/run_english.py examples/english.txt --language en --explain --out work/english-result.json
```

설치는 Python 패키지와 공개 모델을 다운로드합니다. **사용자 원문은 전송하지 않습니다.** 추론은 로컬 파일만 사용합니다. 영어 모델은 메모리가 필요하며 실험용 보조 점수입니다. 보호 CLI는 동시 실행을 제한하고, 런타임 비정상 종료 시 확률을 반환하지 않습니다. 검수 중 관찰된 간헐적 Windows/PyTorch 충돌의 근본 원인이 해결됐다는 뜻은 아닙니다. 정확한 체크포인트·해시·한계는 [영어 모델 안내](references/free-local-model.md)를 확인하세요.

## 실제 평가와 한계

한국어 주제 분리 평가 1,846개에서 정확도 **97.51%**, 사람 글 오탐률 **0.90% (8/885)**였습니다. 에세이 1,714개가 대부분이며 초록 37개·시 95개의 정확도는 각각 91.89%, 87.37%였습니다. 이 결과는 모든 장르나 최신 생성기에 대한 보장이 아닙니다. 한국어의 AI/사람 50% 기준 보정도 사용자의 실제 모집단 분포를 측정한 것은 아닙니다. [한국어 모델 카드와 표본별 기록](references/korean-model.md)

영어 36개 pilot에서 로컬 모델 정확도는 83.33%, 같은 표본의 저장된 GPTZero 판정은 97.22%였습니다. **이 스킬이 GPTZero보다 정확하다는 결론은 없습니다.** 새로운 한국어 결과와 과거 영어 결과를 비교해 우열을 매기지 않습니다. 한국어 GPTZero 동일 표본 비교는 미실시입니다. [조건과 원시 결과](references/performance-comparison.md)

짧은 글, 번역·교열, 공동 작성, 새로운 humanizer·생성 모델에는 알려지지 않은 오류가 있을 수 있습니다. 문단 삭제의 변화량은 그 문단의 AI 작성 확률이 아니며, 흔한 표현의 모델 기여도도 작성 이력의 증명이 아닙니다.

## 검증과 재현

```sh
python -B -X utf8 -m unittest discover -s scripts -p "test_*.py"
```

기본 테스트 56개는 표준 라이브러리로 실행되며 대형 영어 모델 다운로드나 상용 API를 호출하지 않습니다. 한국어 모델의 해시, 저장된 지표의 재계산, 자료 분리, Unicode 원문 좌표, 잘못된 입력, HTML escape 등을 확인합니다. 별도 검수에서는 추가 subprocess 시험 16개·결과 검증 20개와 실제 영어 추론, 한국어 2,598개 재추론 및 전체 재학습을 확인했습니다. 기능 테스트를 탐지 정확도로 해석하지 않습니다. 검증 이력은 [verification.md](references/verification.md)에 있습니다.

한국어 재학습은 별도 선택 기능입니다.

```sh
python -m pip install -r requirements-training.txt
python scripts/prepare_korean_data.py work/korean-data
python scripts/train_korean.py --data-root work/korean-data --output-dir work/korean-retrained
```

원본 학습 데이터는 저장소에 포함하지 않습니다. 고정 revision과 파일 해시를 사용하며 다운로드·학습·추론을 분리합니다. [자료 출처와 이용 조건](THIRD_PARTY_NOTICES.md)을 확인하세요. 이 공개 저장소에는 프로젝트 전체를 포괄하는 오픈소스 라이선스를 아직 부여하지 않았으며, 제3자 자료의 권리를 대신 허가하지 않습니다.
