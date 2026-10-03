# 선택적 영어 로컬 모델

한국어는 패키지에 포함된 별도 [한국어 모델](korean-model.md)을 사용한다. 이 문서는 큰 영어 체크포인트의 설치·실행만 다룬다.

## 포함한 선택지

[tropa-mini / wasitaigeneratedcom/ai-text-detector-small](https://huggingface.co/wasitaigeneratedcom/ai-text-detector-small/tree/f1795c86806e6838d4afa33d0b1427f8430c9615)는 Apache-2.0로 공개된 영어 DeBERTa 기반 모델이다. 약 1.74 GB 가중치를 로컬에서 실행한다. Human/AI/AI-edited/Humanized 네 클래스와 mean pooling 분류기를 사용한다. 모델 카드의 성능 수치는 개발자 측 결과이며 여기서 검증된 성능과 분리한다.

고정 revision: `f1795c86806e6838d4afa33d0b1427f8430c9615`.
가중치 SHA256: `4a1561fadf44ec72934edd6158ff8c76e9388ade1384dbeeea6eb15f93251087`.

API키·추론 서버·유료 계정은 필요 없다. Python 3.10+, torch, transformers, safetensors, tokenizers가 필요하다. 제작 환경의 Python 3.13에 있던 패키지를 사용하며 자동 패키지 설치·클라우드 대체 실행은 하지 않는다. 메모리가 부족하면 정밀 근거 분석으로 계속하고 모델 점수는 실패로 표시한다.

```text
python scripts/prepare_local_model.py models/tropa-mini
python -B -X utf8 scripts/run_english.py manuscript.txt --language en --explain --out work/local-result.json
```

다운로더는 고정된 공개 모델 파일만 받는다. 사용자 글을 전달하지 않는다. `.part`는 미완료 다운로드이며 정상 가중치로 사용하지 않는다. 로더는 `local_files_only=True`, `trust_remote_code=False`, 오프라인 환경을 사용한다. 다운로드한 Python을 실행하지 않으며 safetensors를 엄격한 키/shape 조건으로 로드한다. 메타 디바이스 초기화로 중복 가중치 메모리를 줄인다.

## 실행 보호와 지원 범위

권장 진입점 `run_english.py`는 로컬 자식 프로세스에서 `local_model.py`를 실행한다. 실제 모델 작업이 운영체제 파일 잠금을 소유하므로 감독 프로세스만 종료되어도 살아 있는 모델 작업의 잠금은 유지된다. 같은 임시 디렉터리를 공유하는 CLI의 중복 실행을 거부하며, 잠금 파일이 남아 있어도 실행 중인 잠금이 없으면 다음 실행이 가능하다. 낮은 수준의 `local_model.py` CLI도 잠금을 사용하지만, 비정상 종료 감지·최종 결과 검증은 `run_english.py`가 제공한다. 직접 `LocalDetector` Python 라이브러리 호출에는 이 실행 보호가 없다.

독립 Windows 검수에서 PyTorch `torch_cpu.dll`의 간헐적 native access violation이 관찰됐다. 단독 재실행과 36문서 pilot은 성공했지만 원인은 확정하지 않았다. 보호 CLI는 종료 코드, 모델·원문 메타데이터, 확률의 유한성·합, 모든 창의 좌표·토큰 범위, 문단 삭제 수치의 일관성을 검사한다. 실패하면 최종 결과를 저장하지 않고 `authorship_probabilities: null` 오류를 낸다. 이전 결과 파일은 덮어쓰거나 재사용하지 않는다. 이는 실패 처리 개선이며 네이티브 충돌 자체의 근본 해결이나 모든 환경의 안정성 보장이 아니다. 검증된 환경 버전은 [tested-environment.json](tested-environment.json)에 기록되어 있다. requirements의 모든 버전 조합을 시험한 것은 아니다.

입력은 실제 영어인지 먼저 확인한다. 공백·숫자뿐인 글, 한글 및 대부분의 비라틴 문자 글은 미리 거부한다. 문자 비율 검사는 영어와 프랑스어·독일어 등의 라틴 문자 언어를 구분하는 언어 식별기가 아니다.

## 실제 확인한 성능 한계

이 모델은 **실험용 보조 점수**로 취급한다. 이 패키지의 36개 영어 pilot에서 기본 임계값 정확도는 30/36, 인간 오탐은 3/12였다. 두 인간 표본에서 AI 관여 점수가 0.998 이상인데도 오탐이었다. 높은 모델 점수가 검증된 작성 확률을 보장하지 않는 실제 사례다. 모델 카드의 낮은 FPR을 이 환경에 그대로 적용하지 않는다. [전체 비교와 원시 결과](performance-comparison.md)를 참조한다.

## 결과 읽기

- 한 창에 들어가는 입력: 모델이 반환한 네 클래스 확률을 그대로 보인다. 두 값이 필요하면 AI 관여 = AI + AI-edited + Humanized, Human-only = Human으로 함께 표기한다. 독립 보정된 개인 작성 확률이 아니다.
- 긴 입력: 768 토큰 한도에서 겹치는 창으로 모든 토큰을 검사한다. 창마다 원문 위치·길이·점수를 보이고, 문서 전체 확률은 산출하지 않는다. 평균은 평가용 점수로 쓸 수 있지만 보정된 문서 확률이 아니다.
- `--explain`: 한 창의 문서를 대상으로 원문 문단을 하나씩 제거해 점수 변화를 측정한다. 원문 파일은 바꾸지 않는다. 기본 최대 40개, 미측정 수를 기록한다. 문단 하나뿐인 문서를 삭제하면 빈 글이므로 계산하지 않는다.
- 양의 점수 차이는 삭제 후 AI 관여 점수가 낮아졌다는 뜻이다. 원인으로 AI 작성이 증명된 것이 아니며, 길이와 문맥 변동의 영향을 함께 설명한다.

## 한국어 지원 한계와 검토한 대안

이 영어 모델을 한국어·한국어 혼합 문서에 적용하지 않는다. 다국어라는 이름만으로 한국어 성능을 인정하지 않는다. 한국어는 언어별 근거 분석과 실제 제공된 결과 해석을 지원하며, v3에서는 별도로 내장한 [한국어 분류기](korean-model.md)가 보정된 Human/AI 추정 확률을 계산한다. 이 영어 체크포인트를 한국어에 쓰는 것은 아니다.

- [Desklib v1.01](https://huggingface.co/desklib/ai-text-detector-v1.01): 모델 카드가 영어용임을 명시한다. 한국어 대안으로 채택하지 않았다.
- [Oculus multilingual](https://huggingface.co/danibor/oculus-v2.0-multilingual): 공개 지원 목록에 한국어가 없고 GPTZero soft labels로 증류했다고 설명한다. 그 사실이 GPTZero와 동등한 정확도를 뜻하지 않는다.
- [Munche](https://huggingface.co/Baragi-AI/Munche-768-AI-Detector): 한국어 장르소설 대상, gated 기반 모델과 입력 길이 제한이 있다. 범용 한국어 모델로 일반화하지 않았다.
- [KatFishNet](https://github.com/Shinwoo-Park/katfishnet): 한국어 언어학적 특징과 공개 실험·데이터는 중요한 연구 기반이다. 배포 가능한 범용 확률 모델과 완전한 새 모델/장르 검증이 자동 제공되는 것은 아니다. 논문의 AUROC를 이 스킬의 정확도로 옮겨 쓰지 않는다.

한국어 모델의 향후 확대는 라벨 출처, 라이선스, author/topic/generation-group 단위 train/calibration/test 분리, 현대 모델·장르·번역·교정·humanizer별 독립 검증을 갖춘 뒤 한다. 영어 모델을 억지로 번역 입력에 적용하거나 몇 가지 특징에 임의 가중치를 붙여 확률을 만들어내는 방식은 성능 개선이 아니다.
