# 제작·검증 기록

검토일: 2026-10-03. 완성된 문서에 대해 생성 작업과 분리하여 사실 대조를 수행했다. 다음 표는 반복되는 주장을 묶은 검증 기록이다. 원문 대조는 주장·출처의 일치를 확인한 것이며, 외부 모델의 성능을 재현한 것이 아니다.

## 출처 대조

| 검토한 주장 | 원자료·위치 | 결과 |
| --- | --- | --- |
| GLTR의 통계 기반 탐지 보조 | [ACL 원문](https://aclanthology.org/P19-3019/) | 일치. 현재 탐지 성능으로 확대하지 않음. |
| DetectGPT의 로그확률·교란·곡률 | [원 논문](https://arxiv.org/abs/2301.11305) | 일치. 실제 모델 계산 필요를 명시. |
| Fast-DetectGPT의 조건부 곡률·샘플링 | [원 논문](https://arxiv.org/abs/2310.05130), [원저자 구현](https://github.com/baoguangsheng/fast-detect-gpt) | 일치. 구현의 예시 확률을 본 스킬의 결과로 사용하지 않음. |
| Binoculars의 두 모델 비교 | [ICML 논문](https://proceedings.mlr.press/v235/hans24a.html), [원저자 구현](https://github.com/ahans30/Binoculars) | 일치. 구현도 영어 이외 언어의 한계를 밝힘. |
| Ghostbuster의 약한 모델 특징·분류기 학습 | [원 논문](https://arxiv.org/abs/2305.15047) | 일치. 원 생성모델 확률과 참조 모델 사용을 구분. |
| RADAR의 탐지기·패러프레이저 적대 학습 | [원 논문](https://arxiv.org/abs/2307.03838) | 일치. 모든 재작성에 대한 보장으로 해석하지 않음. |
| KatFishNet의 특징·평가값 | [PDF 표 3, 8쪽](https://aclanthology.org/2025.acl-long.1030.pdf) | 94.88/73.10/75.62 및 AUROC 확인. 범용 accuracy 표현 배제. |
| 생성 시 토큰 워터마크의 원리 | [원 논문](https://arxiv.org/abs/2301.10226) | 일치. Unicode 문자 검사와 구분. |
| RAID의 다양한 평가 조건 | [ACL 원문](https://aclanthology.org/2024.acl-long.674/) | 일치. 논문/현재 저장소의 데이터 규모는 섞지 않음. |
| MULTITuDE 11개 언어에 한국어 없음 | [언어 목록](https://aclanthology.org/2023.emnlp-main.616/) | 일치. 한국어 성능 증거로 쓰지 않음. |
| M4의 미지 도메인·생성모델 일반화 문제 | [EACL 원문](https://aclanthology.org/2024.eacl-long.83/) | 일치. |
| 비원어민 영어의 오탐 편향 연구 | [원 논문](https://arxiv.org/abs/2304.02819) | 일치. 당시 표본/제품 범위로 한정. |
| 재작성·분포 거리와 탐지의 한계 | [원 논문](https://arxiv.org/abs/2303.11156) | 일치. 무조건적인 탐지 불가능 주장으로 확대하지 않음. |
| 신경망의 정확도와 확률 보정의 차이 | [ICML 원문](https://proceedings.mlr.press/v70/guo17a.html) | 일치. 초기 버전은 자체 보정 미실시; v3 한국어의 별도 보정은 아래 추가 검증에 구분. |
| GPTZero의 계층/공동 학습·세 범주·비공개 세부 구조 | [기술 보고서 §3.2](https://arxiv.org/html/2602.13042v1), [FAQ](https://gptzero.me/faq) | 일치. 업체 보고로 표시. |
| GPTZero 영어·한국어 지원 및 API 요청 형식 | [언어 목록](https://support.gptzero.me/articles/1682612063-what-languages-does-gptzero-support), [개발자 페이지](https://gptzero.me/developers) | 문서 계약 확인. 실서비스 호출은 미실시. |
| Turnitin의 산문 비중·언어·길이·별표 처리 | [공식 가이드](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report) | 일치. 사람 확률로 보수 변환하지 않음. |
| Copyleaks 탐지와 설명 기능의 언어 범위 차이 | [지원 목록](https://docs.copyleaks.com/reference/actions/miscellaneous/ai-detection-supported-languages/), [AI Logic](https://docs.copyleaks.com/concepts/features/ai-logic) | 일치. 한국어 탐지 지원과 한국어 설명 지원 구분. |
| Originality confidence와 allowance 구분 | [점수 설명](https://originality.ai/blog/score-meaning), [언어 안내](https://help.originality.ai/en/article/multiple-languages-how-to-use-multi-language-ai-detection-13e5plo/) | 현재 안내 반영. 옛 단일 점수 설명으로 단순화하지 않음. |
| Pangram 분류기·한국어 지원 | [방식](https://www.pangram.com/knowledge-hub/how-does-pangram-work), [언어](https://www.pangram.com/knowledge-hub/what-languages-does-pangram-work-on) | 업체 설명과 일치. 세부 가중치는 미확인. |
| Winston AI 목록에 한국어 없음 | [언어 안내](https://help.gowinston.ai/getting-started/which-languages-does-winston-ai-work-with) | 확인한 AI text detection 목록으로 한정. |
| ZeroGPT의 특징 계열·광범위 언어 주장 | [FAQ](https://www.zerogpt.com/faq) | 업체 설명과 일치. 한국어 독립 정확도 미확인. |
| Sapling의 토큰 분류·문장 perplexity | [공식 페이지](https://sapling.ai/ai-content-detector) | 일치. 한국어 명시적 검증 범위는 미확인으로 표시. |
| QuillBot 설명·80단어 조건 | [공식 페이지](https://quillbot.com/ai-content-detector) | 일치. 사용 버전의 점수 정의·한국어 성능은 별도 확인하도록 함. |
| Grammarly의 구간별 분석·텍스트 비중 | [공식 사용자 가이드 FAQ](https://support.grammarly.com/hc/en-us/articles/28936304999949-AI-Detector-user-guide) | 일치. 문서 작성 주체의 확률로 해석하지 않음. |
| GPT킬러의 모델 계열·어절 기반 취합·표절검사 합산 | [공식 매뉴얼](https://manual.muhayu.com/montly-gpt-killer-labs) | 업체 설명과 일치. 400자 고정 규격 주장은 배제. |
| 공개 스킬 6개의 역할·의존성·점수 성격 | [원저자 링크를 포함한 비교표](skill-comparison.md) | 각각 SKILL.md 원문 확인. 그 스킬의 주장·점수를 검증된 성능으로 승격하지 않음. |
| 로컬 humanizer 계열의 편집 목적 | 해당 로컬 SKILL.md와 관련 탐지 설명 | 관련 부분 대조. 기존 파일을 변경하거나 과거 실측을 재사용하지 않음. |

문체 관찰의 대안 설명, 추가 탐지 요금 없는 실행 범위, 판정 보류 및 보고 양식은 설계 결정이다. 실측 사실처럼 제시하지 않았다. 정확한 문서별 작성 확률이나 100% 탐지 성능을 증명하는 자료는 확보하지 않았으며 그러한 주장은 포함하지 않았다.

## v2 추가 주장 대조

| 검토 주장 | 근거 | 결과 |
| --- | --- | --- |
| 공개 영어 1,089개 결과와 버전 | Epoch AI 글, 고정 commit의 results/all_detectors.csv | 로컬 재집계 값과 원 보고 수치 일치. 최신 실서비스 호출은 아님. |
| 현 GPTZero를 perplexity/burstiness만으로 설명할 수 없음 | 공식 Support Center의 autumn 2023 변경 안내 | 일치. 원 벤치마크 글의 낡은 방법 설명은 배제. |
| 무료 모델 영어/네 클래스/라이선스/mean pooling | 고정 revision의 README, config.json, serving_head.json, NOTICE | 일치. 제작자 성능 주장은 자체 검증과 구분. |
| 공개 모델 가중치 동일성 | Hugging Face LFS SHA256와 실제 다운로드 해시 | 일치. 원격 Python 실행 없음. |
| 단순 임계값 증가가 성능 개선은 아님 | 이번 36개 동일 표본 두 고정 임계값의 실제 결과 | 30/36 → 28/36. 우위 주장 배제. |
| 한국어 범용 확률의 검증 부족 | Desklib/Oculus/Munche/KatFishNet의 실제 범위 | 한국어 확률 제공 불가를 명시. ‘검토한 범위’의 결론이지 존재 가능한 모든 모델의 부재 주장은 아님. |
| 상세 설명이 GPTZero 이상의 정확도를 증명함 | 뒷받침 자료 없음, 실제 pilot은 반대 방향 | 그런 주장 배제. |

## v2 소프트웨어와 행동 검증 기록

- `quick_validate.py`: 스킬 형식 검사 통과.
- 단위 테스트 **35개 통과**: 합성 입력, 수치 계산, 문서 좌표, Unicode/BOM/CRLF, HTML escape, 비용 차단, 표본 선택과 실패 분모 처리 등을 검사했다. 테스트 통과율을 탐지 accuracy로 쓰지 않는다.
- 기존 GPTZero 실시간 명령은 키와 업로드 플래그가 있어도 외부 요청 전에 실패한다. 저장된 결과만 해석한다.
- 영어 공개 가중치 로드, 실제 4-class 추론, 두 문단의 삭제 전후 점수 차이를 실행했다. 처음에는 로컬 메모리 부담과 Transformers 5의 prepare_for_model 제거가 드러나 메타 초기화·스레드 제한·검증한 DeBERTa 토큰 구성을 적용했다. 수정 후 실행 성공. 합성 시연은 정확도 평가로 사용하지 않는다.
- 실제 공개 영어 36개 pilot을 완료했다. 버전·표본·해시·원점수·두 사전 고정 임계값·같은 표본의 외부 저장 verdict는 [benchmark-results.json](benchmark-results.json)에 보존했다. 실제 결과는 [성능 비교](performance-comparison.md)에 있다.
- 별도 에이전트가 v2를 읽고 한국어 3문단 전체를 실제 도구로 분석했다. 원문 보존·인용·해시·문단 검토율을 확인했고 외부 호출 없이 동작했다. 이 행동 검증은 작성 주체의 정답 검증이 아니다.
- 독립 검토에서 보고서의 영문 내부 키가 독자에게 노출되는 문제가 발견돼 한국어 표시명으로 수정했다. 완성된 HTML을 로컬 브라우저에서 실제로 렌더링해 한국어, 문단 카드와 하이라이트를 확인했다.
- 이전 버전 검토에서 발견한 BOM 제거 문제를 유지 수정하고 원문 좌표 덮어쓰기 회귀도 검사했다. 패키지 내부 상대 링크와 소스 문법을 확인했다.

**v2에서 검증하지 않은 것:** 범용 한국어 탐지 accuracy/FPR, 최신 GPTZero 4o와의 직접 비교, 모든 humanizer·장르·신모델에 대한 강건성, 독립적인 확률 보정. 36개 영어 pilot은 작고 공개되어 학습 중복을 배제할 수 없다. 전체 결론의 신뢰도는 ‘실행·좌표·수치 재계산은 높음, 범용 작성 판별 정확도는 미확립’이다.

## v3 한국어 추가 검증

2026-10-03 실제로 한국어 문자 분류기를 학습하고 별도 calibration 그룹으로 sigmoid를 맞췄다. [모델 카드](korean-model.md), [실행 결과](korean-validation.json), 표본별 예측과 분할 기록을 함께 배포한다. 이전 절의 한국어 확률 미지원은 v2의 상태다.

- 원본 12,894행, 중복 제거 후 12,844행. 학습 6,621 / 선택 1,718 / 보정 1,907 / 최종 평가 1,846 / 주제를 공유하는 별도 전이 평가 752. 모든 학습·선택·보정·최종 평가 그룹의 교집합이 없으며 원본 test-v2는 어떤 학습 단계에도 들어가지 않았음을 분할 기록에서 검사했다.
- 사전 지정한 6개 후보의 선택 결과와 보정 값을 고정한 후 평가했다. 최종 평가를 보고 모델을 다시 조정하지 않았다. 최종 모델은 표면 특징의 가중치가 0이며 문자 특징이 예측을 결정한다.
- 주제 분리 최종 평가 정확도 97.51%, 인간 오탐 8/885. 에세이 1,714개가 전체 결과를 지배한다. 초록·시는 표본이 작고 성능이 더 낮으며 모델 카드에서 따로 공개했다. 이를 범용 정확도로 발표하지 않는다.
- 보정 후 Brier/ECE는 개선되었으나 정확도는 97.72%→97.51%로 소폭 감소했다. 학습과 별도의 자료를 사용했다는 의미의 holdout 보정이며 외부 기관의 독립 검증은 아니다.
- 표준 라이브러리로 내보낸 추론과 sklearn 파이프라인을 최종·전이 평가 각각 첫 25개에서 비교했다. 최대 절대 차이 4.45e-16 이하. 저장된 모든 평가 예측으로 accuracy/FPR/AUROC/Brier/log loss/ECE를 다시 계산해 기록과 일치함을 검사했다.
- 단위 테스트 총 **45개 통과**. v2 테스트에 오프라인 한국어 추론, 확률 합, logit 재구성, Unicode/공백 변환의 정확한 원문 위치, 삭제 변화량, 잘못된 언어·입력·가중치, 결과와 원문 해시 연결, 분할 누수·원본 test 보존 검사를 추가했다. 테스트 통과율은 탐지 정확도가 아니다.
- Python `-S`로 site-packages를 로드하지 않고 실제 한국어 CLI 실행에 성공했다. 입력 전체의 모델 점수와 문단별 삭제 결과가 반환됐다. 상용 탐지 API 호출 0회.
- 별도 에이전트가 갱신된 스킬로 3문단 원문을 실제 분석했다. 사람/AI 추정값과 원문 전체 검토, AI 방향·사람 방향 문자 기여, 문단 삭제 변화를 연결했다. 실행 기록에서 원문 불변·확률 합·좌표·기여 재구성·3/3문단 검토·외부 HTML 리소스 부재를 확인했다. 이 합성 기능 시연은 탐지 정확도 평가에 넣지 않았다.

미검증: 한국어에서 GPTZero와의 동일 표본 비교, 현대 모든 생성 모델·humanizer·공동 작성·새 장르·실제 이용자의 분포에 대한 정확도와 확률 보정. 이 한계를 숨긴 ‘완벽한 탐지’ 또는 ‘개인 작성 이력의 정확한 확률’이라는 주장은 하지 않는다.

## v3.1 독립 출시 검수 및 수정

제작과 별도 Codex 대화에서 원자료·가중치·소스를 직접 읽고 실행한 [공개 검수 요약](review-public.md), [기계 판독 결과](review-public.json), [검수 파일 해시](reviewed-files-public.json), [검수 문서 해시](review-artifacts-public.json)를 포함한다. 외부 기관의 인증이나 새로운 모집단의 독립 성능 평가라는 뜻은 아니다.

- 최종 기본 단위 테스트 56개, 별도 subprocess 시험 16개, 결과 스키마 시험 20개가 통과했다.
- 영어 HTML의 미보정·실험용·오탐 경고와 JSON 메타데이터, UTC 측정 시각을 유지하도록 수정했다. 명백한 비라틴·빈 입력을 사전 거부하며 이 검사를 영어 자동 식별이라고 하지 않는다.
- 한국어 기본 가중치 SHA256 고정, 잘못된 모델 루트·숫자·스케일 거부를 추가하고 손상 fixture로 검증했다.
- 영어 보호 CLI는 실제 worker가 잠금을 소유하고, 실패·누락·불완전한 수치·잘못된 원문 연결을 최종 결과로 저장하지 않는다. 감독 프로세스 종료 뒤 살아 있는 worker의 경합과 native 종료 코드 주입을 실제 subprocess로 재검증했다. 기존 결과와 원문은 보존한다.
- 실제 영어 체크포인트를 보호 CLI에서 실행해 이전 네 클래스 점수와 차이 0, 문단 삭제 3개를 확인했다. 영어 36개 공개 pilot의 재추론 점수도 기존 기록과 같았다.
- 한국어 평가·전이 2,598개 전부를 다시 계산했고 저장 예측과 최대 차이는 1.45e-15 미만이었다. 원자료 12,844개의 해시·라벨·주요 분할 비중복을 확인했다. 다시 학습한 모델·분할·평가 예측은 바이트 단위로 같았다.
- 추론의 네트워크 차단을 확인했으며 상용 탐지 API·유료 추론·클라우드 GPU를 쓰지 않았다. 학습 원문과 비공개 검수 로그, 선택적 대형 영어 가중치는 공개 패키지에 넣지 않는다.

남은 한계: Windows/PyTorch의 간헐적 native crash 원인은 미확정이다. 실행 보호의 검증을 근본 원인 해결이나 모든 환경의 안정성 보장으로 표시하지 않는다. 데이터·학습 산출물의 권리 범위와 프로젝트 비 OSS 공개 범위는 [제3자 고지](../THIRD_PARTY_NOTICES.md)에 구분했다. 검수 manifest 이후 변경한 파일은 이 검수 링크를 추가한 README와 본 기록뿐이며, 실행 코드·모델은 검수한 해시를 유지한다.
