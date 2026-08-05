# 🌬️ 서울시 AI 미세먼지 보건 분석
> **서울시민의 호흡기 건강을 위한 통합 솔루션**

* **한줄 소개**: 공공 API 시계열 데이터와 AI 모델을 결합한 서울시 자치구별 미세먼지 보건 위험도 예측 및 실시간 마스크 관제 웹 서비스
* **개발 인원**: 1인 (개인 프로젝트)
* **담당 역할**: 공공 데이터 파이프라인 구축, Oracle DB 모델링, RandomForest/YOLOv8 모델 연동, 정규식 및 DB 캐시 기반 AI 챗봇 파이프라인 구축, Flask 백엔드 아키텍처 설계

### 🛠️ Tech Stack
**AI & Computer Vision**
![YOLOv8](https://img.shields.io/badge/YOLOv8-00FFFF?style=flat-square&logo=ultralytics&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=OpenCV&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)

**Backend & Database**
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=Python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=flat-square&logo=Flask&logoColor=white)
![Oracle](https://img.shields.io/badge/Oracle-19c-F80000?style=flat-square&logo=Oracle&logoColor=white)
![PyCharm](https://img.shields.io/badge/PyCharm-000000?style=flat-square&logo=PyCharm&logoColor=white)

**Data Handling & Automation**
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![APScheduler](https://img.shields.io/badge/APScheduler-6DA55F?style=flat-square&logo=python&logoColor=white)

**Frontend & Tools**
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

---

## 🎯 1. 기획 의도 및 개발 목표

### 1-1. 기획 의도 (Background)
미세먼지는 체내 배출에 2~3일이 소요되는 1급 발암물질입니다. 단순히 "현재 농도"만 보여주는 기존 서비스의 한계를 넘어, **과거 누적 위험도를 시각화**하고 **AI 관제(마스크 착용률)**를 통해 실질적인 보건 예방책을 제시하고자 했습니다.

<p align="center">
  <img width="500" alt="미세먼지 자료 1" src="https://github.com/user-attachments/assets/298ff777-7331-4e81-bb8c-d4689b6d0c6b" />
  <br>
  <em>[미세먼지 자료 1] 미세먼지 성분 구성 및 건강에 미치는 영향 분석</em>
</p>

<p align="center">
  <img width="600" alt="미세먼지 자료 2" src="https://github.com/user-attachments/assets/60534f76-999e-4053-abbc-9399da19e7b1" />
  <br>
  <em>[미세먼지 자료 2] 미세먼지 노출 후 지속되는 위험성 인지 필요성</em>
</p>

---

### 1-2. 개발 목표 (Objectives)
단순한 수치 중계를 넘어, AI 모델과 시계열 분석을 통해 서울시민의 호흡기 건강권을 선제적으로 보호하는 '지능형 보건 관제 시스템' 구축을 목표로 합니다.
* **정밀 위험도 예측**: 미세먼지의 체내 잔류 특성을 반영하여, 단순 현재 수치가 아닌 누적 시계열 데이터와 지역 산업 특성을 결합한 RandomForest 기반 4단계(안전~고위험) 예측 엔진을 구현합니다.
* **실시간 방역 지표 수치화**: 마스크 착용률을 실시간 객체 탐지하여, 추상적인 보건 수칙을 구체적인 '지역별 마스크 관제 통계' 데이터로 변환합니다.
* **개인화된 맞춤형 보건 정보 제공**: 지역별 실시간 데이터와 연동된 LLM 챗봇 파이프라인을 구축하여 맞춤형 행동 가이드를 제공합니다.

---

## 📋 2. 요구사항 정의서 (Requirements Specification)

프로젝트 개발을 위해 정의한 기능적 요구사항과 서비스의 품질을 보장하기 위한 비기능적 요구사항입니다.

### 2-1. 기능적 요구사항 (Functional Requirements)
| ID | 분류 | 기능명 | 상세 설명 | 중요도 | 상태 | 비고 |
|:---|:---|:---|:---|:---|:---|:---|
| FR-001 | 회원관리 | 회원가입 | 사용자 정보, 관심 지역, 비밀번호를 입력받아 계정을 생성한다. | High | 완료 | 비밀번호 해싱 |
| FR-002 | 회원관리 | 로그인 | 아이디와 비밀번호를 검증하고 사용자 세션을 생성한다. | High | 완료 | 세션 기반 인증 |
| FR-003 | 데이터 수집 | 대기질 데이터 수집 | 외부 공공 API를 연동하여 실시간 대기질 데이터를 수집한다. | High | 완료 | API 인증키 사용 |
| FR-004 | 분석/예측 | 미세먼지 위험도 예측 | 수집 데이터와 지역 특성 데이터를 기반으로 위험도를 예측한다. | High | 완료 | 머신러닝 예측 모델 |
| FR-005 | 조회 | 대시보드 | 지도, 차트, 지표를 통해 서울시 대기질 현황을 시각화한다. | High | 완료 | DB 캐시 활용 |
| FR-006 | 조회 | 분석 페이지 | 자치구별 대기질 상세 데이터와 추세를 확인한다. | High | 완료 | - |
| FR-007 | 조회 | 비교 페이지 | 여러 자치구의 대기질 데이터를 비교 차트로 확인한다. | Medium | 완료 | - |
| FR-008 | 자동화 | 데이터 자동 갱신 | 정해진 주기에 따라 대기질 및 예측 결과를 자동 갱신한다. | High | 완료 | APScheduler (15분) |
| FR-009 | 관제 | 마스크 착용 관제 | AI 영상 분석을 기반으로 마스크 착용률 통계를 표시한다. | Medium | 완료 | YOLO 모델 |
| FR-010 | 인터랙션 | 챗봇 질의응답 | 자연어 질의를 기반으로 지역별 상태 정보를 제공한다. | Medium | 완료 | LLM API |


### 2-2. 비기능적 요구사항 (Non-Functional Requirements)
| 요구사항 ID | 항목 | 설명 | 기준 |
|:---|:---|:---|:---|
| NFR-001 | 성능 | 캐시 기반 DB 조회로 응답 속도 개선 | 주요 화면 3초 이내 |
| NFR-002 | 보안 | 사용자 비밀번호 해싱 저장 | Werkzeug 해싱 사용 |
| NFR-003 | 보안 | 민감한 설정 정보 환경변수 관리 | .env 사용 |
| NFR-004 | 안정성 | API 장애 시 기존 캐시 활용 | 서비스 중단 방지 |
| NFR-005 | 확장성 | 기능별 모듈 분리(유지보수 용이) | Blueprint/Service 구조 |

---

## 🗂️ 3. 기능 명세서 (Feature Specification)

각 모듈별 세부 기능의 입력(Input)과 출력(Output), 그리고 시스템의 세부 동작을 정의한 명세서입니다.

### 3-1. 회원 관리 (Authentication & User)
| 기능명 | 설명 | 입력 (Input) | 출력 (Output) / 시스템 동작 |
|:---|:---|:---|:---|
| **회원가입** | 사용자 신규 계정 생성 | 이름, 이메일, 비밀번호, 관심지역 | `Werkzeug` 단방향 패스워드 해싱 후 `USERS` 테이블 레코드 저장 |
| **로그인** | 사용자 인증 및 세션 수립 | 이메일, 비밀번호 | DB 해시값 검증 후 Flask Session 생성 및 대시보드로 이동 |
| **로그아웃** | 사용자 세션 종료 | 없음 (로그아웃 버튼 클릭) | 세션 무효화(Clear) 및 로그인 페이지로 리다이렉트 |
| **관심지역 설정** | 대시보드 및 챗봇 기본 지역 지정 | 자치구 선택 (Dropdown) | `USERS.REGION` 컬럼 갱신 및 유저 맞춤형 컨텍스트 데이터 제공 |

### 3-2. 미세먼지 분석 서비스 (Air Quality Analysis)
| 기능명 | 설명 | 입력 (Input) | 출력 (Output) / 시스템 동작 |
|:---|:---|:---|:---|
| **실시간 대기질 조회** | 자치구별 실시간 대기 오염 정보 조회 | 자치구명 | 해당 지역의 실시간 `PM10`, `PM2.5` 등 수치 반환 |
| **위험도 예측** | RandomForest 기반 4단계 위험 등급 도출 | 실시간/과거 시계열, 기온, 산업 비율 | **안전·보통·위험·고위험** 예측 등급 데이터 생성 |
| **지도 시각화** | 예측 결과 기반 서울시 지도 UI 구현 | 위험 등급 결과 데이터 | 자치구별 등급에 따른 단계별 색상 시각화 레이어 렌더링 |
| **상세 분석 조회** | 자치구별 환경 세부 지표 제공 | 자치구명 | 과거 대기질 추이 차트 및 종합 분석 리포트 화면 출력 |
| **지역 비교** | 자치구 간 데이터 대조 | 선택한 자치구 목록 | 자치구별 대기질 비교 분석 시각화 그래프(Chart.js 등) 제공 |

### 3-3. AI 마스크 관제 서비스 (Computer Vision Control)
| 기능명 | 설명 | 입력 (Input) | 출력 (Output) / 시스템 동작 |
|:---|:---|:---|:---|
| **객체 탐지** | CCTV 영상 내 사람 객체 실시간 인식 | 비디오 스트리밍 프롬프트 | `YOLOv8` 모델 기반 바운딩 박스(Bounding Box) 및 객체 정보 추출 |
| **마스크 분류** | 인식된 사람의 마스크 착용 여부 판별 | 탐지된 인물 이미지 크롭본 | 마스크 착용(Masked) / 미착용(Unmasked) 레이블 분류 |
| **연령 분류** | 인식된 객체의 연령대 세부 분류 | 탐지된 인물 이미지 크롭본 | 성인(Adult) / 아동(Child) 객체 카테고리 분류 |
| **착용률 계산** | 실시간 및 누적 통계 연산 수행 | 실시간 탐지 결과 | 객체 ID 기반 중복 제거 로직 적용 후 자치구별 실시간 착용률(%) 도출 |
| **위험 알림** | 미착용자 급증 시 고위험 경보 발생 | 실시간 계산 통계 수치 | 마스크 착용률이 임계치 미만일 경우 관리자 화면 경고 메시지(Alert) 출력 |

### 3-4. AI 챗봇 서비스 (Natural Language Processing)
| 기능명 | 설명 | 입력 (Input) | 출력 (Output) / 시스템 동작 |
|:---|:---|:---|:---|
| **지역 추출** | 사용자 질문 내 핵심 키워드 파싱 | 사용자 자연어 질문 메시지 | 정규식(`re.search`)을 활용해 질문에서 자치구명("OO구") 추출 |
| **환경 정보 조회** | 추출된 지역의 데이터 컨텍스트 확보 | 파싱된 자치구명 (없을 시 관심지역) | `DISK_DASHBOARD_CACHE` 테이블에서 해당 지역 최신 분석 정보 래핑 |
| **LLM 질의 생성** | 프롬프트 엔지니어링 수행 | 사용자 질문 + 환경 데이터 컨텍스트 | LLM이 맥락을 이해하고 할루시네이션을 방지할 수 있는 최적화된 Prompt 구성 |
| **답변 생성** | 자연어 형태의 맞춤형 보건 지침 안내 | 구성된 최적화 Prompt | `RunPod LLM API`를 호출하여 정제된 자연어 가이드 답변 반환 |

### 3-5. 데이터 관리 및 자동화 (Pipeline & Scheduler)
| 기능명 | 설명 | 입력 (Input) | 출력 (Output) / 시스템 동작 |
|:---|:---|:---|:---|
| **API 데이터 수집** | 공공 데이터포털 대기 정보 연동 | 외부 Open API 엔드포인트 | 수집 병목을 제거하기 위해 `ThreadPoolExecutor` 기반 병렬 JSON 데이터 수집 |
| **데이터 전처리** | 분석 및 학습용 정형 데이터화 | 외부 API 수집 원본 JSON | 이상치 처리, 누락 데이터 대응 및 표준 내부 딕셔너리 구조 변환 |
| **DB 캐시 저장** | 대시보드 로딩 속도 최적화 | 전처리 및 분석 완료 데이터 | Oracle `MERGE INTO` 쿼리를 활용해 `DISK_DASHBOARD_CACHE` 단일 행 적재 |
| **스케줄링** | 주기적 시스템 데이터 갱신 자동화 | 백그라운드 스케줄 타임 트래거 | `APScheduler`를 활용해 15분 주기로 데이터 수집-예측-캐싱 파이프라인 무한 루프 구동 |
| **통계 이력 저장** | 시계열 통계 및 AI 데이터 누적 관리 | 실시간 대기질 및 관제 통계 데이터 | 트렌드 분석을 위해 분석용 통계 테이블(`AIR_QUALITY_HOURLY` 등)에 데이터 축적 |

---

## 🏗️ 4. 주요 기능 및 고도화 과정

### 시스템 아키텍처 (System Architecture)
본 프로젝트는 데이터 수집(Collection), 분석(Analysis), 서비스(Interface) 계층을 논리적으로 분리하여 설계되었습니다. Flask 서버를 중심으로 각 기능을 Blueprint로 모듈화하고, 데이터 캐싱 및 병렬 처리를 통해 고가용성과 응답 속도를 최적화했습니다.

![서울시 AI-미세먼지 보건 분석 시스템 아키텍처](https://github.com/user-attachments/assets/b504cd53-8937-40b8-b9af-f34931032e09)

---

### 🗄️ 데이터베이스 모델링 (ERD)
실제 웹사이트는 실시간 API 데이터를 임시 캐시에 담아 가볍게 띄우고, 상단의 복잡한 통계 테이블들은 AI 모델 학습을 위한 데이터셋으로 활용했습니다.

![서울시 AI-미세먼지 보건 분석 시스템 아키텍처](https://github.com/user-attachments/assets/2cd2e70c-9506-4872-8f27-306c6176283d)


### Phase 1: 데이터 분석 및 Flask 기반 웹 서비스 구축
* **멀티 API 연동**: 서울시 RealtimeAir, 기상청 APIHub 등 다각도 데이터 수집
* **성능 최적화**: `ThreadPoolExecutor`를 활용해 25개 자치구의 과거 데이터를 **병렬로 수집**, 로딩 속도 개선
* **DB 캐싱 구조 구축**: 수집한 API 데이터와 예측 결과를 Oracle DB에 JSON 형태로 저장하고, APScheduler를 통해 서버 시작 시 1회 및 15분 주기로 자동 갱신

### Phase 2: 머신러닝 및 딥러닝 모델 도입
* **미세먼지 위험도 예측:**: 실시간 PM10/PM2.5, 과거 농도, 기온, 지역 산업 비율 데이터를 기반으로 RandomForest 모델을 활용해 자치구별 위험도 예측
* **AI 실시간 관제**: YOLOv8 기반으로 영상 내 마스크 착용 여부 및 객체(Child/Adult) 분류
* **관제 대시보드**: 실시간 마스크 착용률 통계 및 고위험 상황 경보(Alert) 시스템 연동
* **시스템 통합**: 분석된 미세먼지 수치, 예측 위험도, AI 관제 결과를 하나의 Flask 통합 서비스로 제공

### Phase 3: LLM 기반 맞춤형 챗봇 기능 확장
* **지역 기반 질의 처리**: 사용자의 질문에서 정규식을 활용해 “OO구” 형태의 지역명을 추출하고, 지역명이 없을 경우 로그인 사용자의 관심 지역을 기본값으로 사용
* **RunPod LLM API 연동**: 지역별 PM10, 위험도, 분석 정보를 프롬프트에 삽입한 뒤 RunPod 기반 LLM API에 전달하여 자연어 답변 생성
* **응답 품질 제어**: max_new_tokens, temperature, repetition_penalty, stop 조건을 조정하고 반복 문장 제거 로직을 적용하여 짧고 일관된 답변 제공

---

## ✨ 5. 주요 기능 (Main Features)

### 5-1. 서울시 미세먼지 위험도 시각화

![서울시 미세먼지 위험도](https://github.com/user-attachments/assets/fb3664ae-f598-4fae-a802-ce9619444c7f)

지표 선택 및 다차원 시각화 기능 
  1. 사용자가 '종합 보건 위험 등급', '미세먼지(PM10)', '초미세먼지(PM2.5)' 원하는 지표를 선택할 수 있도록 
  버튼 UI를 구현하였습니다. 
  2. 선택된 지표에 따라 중앙의 서울시 지도(카카오맵 API 연동) 내 자치구별 영역 색상이 동적으로 변경되도록 시각화 레이어를 구성하였습니다. 
  3. 좌측 영역에 최근 3일간의 미세먼지 및 초미세먼지 농도 추이 차트를 배치하여 직관적인 오염도 변화 흐름을 제공합니다. 
  4.우측 패널에는 선택한 자치구(예: 중구)의 AI 모델 분석 근거를 연동하여, RandomForest 기반의 4단계 
  위험 등급(안전•보통•위험•고위험) 및 주변 병원정보를 실시간으로 출력하도록 구현하였습니다.

APScheduler 기반 백그라운드 자동 갱신 기능 
  1. 실시간 대기질 데이터와 AI 예측 결과를 상시 최신 상태로 유지하기 위해 백그라운드 스케줄러를 구축하였습니다. 
  2. 서버 시작 시 즉시 1회 데이터를 동기화하고, 이후 15분 주기로 공공 API 수집 및 예측 모델 연산 파이프라인이 무한 루프로 구동되도록 설정하였습니다.


### 5-2. YOLOv8 기반 AI 마스크 착용 탐지

![AI 마스크 탐지](https://github.com/user-attachments/assets/b200d8ca-516e-4d95-95ce-78999016b8c8)

YOLOv8 AI 서버 연동 및 실시간 착용률 산출 기능  
  1. 외부 AI 추론 서버(/api/predict_mask)로부터 실시간 객체 탐지 결과(id_list, cls_list)를 비동기로 수신하여 분석 파이프라인을 구축하였습니다. 
  2. 객체 고유 ID(Object ID) 기반 중복 제거 로직을 적용하여 동일 인원이 프레임마다 반복 집계되는 오류를 방지하고, 전체 누적 방역 지표 및 취약계층(아동) 준수율을 산출합니다.
  

### 5-3. 지역 기반 AI 챗봇 서비스

![AI 챗봇](https://github.com/user-attachments/assets/9ce360f0-c50d-4034-b8f8-efbb52fbae04)

정규식 기반 지역 추출 및 RAG 프롬프트 엔지니어링 
  1. 사용자의 질문 텍스트에서 정규식(re.search)을 활용해 특정 자치구(예: '중구') 키워드를 동적으로 추출하고, Oracle DB 캐시에서 해당 지역의 실시간 대기질 및 AI 분석 데이터를 연동하도록 구현하였습니다. 
  2. 외부 LLM(RunPod API) 호출 시, 추출된 데이터 컨텍스트를 프롬프트에 주입(RAG 구조)하여 환각 현상을 방지하고, 정확한 수치 기반의 친절한 보건 상담 답변을 생성하도록 설계하였습니다.

---

## 🛠️ 6. 핵심 구현 로직 (Key Implementation)

### 6-1. Flask App Factory & Blueprint 구조
애플리케이션을 기능별로 모듈화하여 유지보수성을 극대화했습니다. 서버 실행 시 예측 모델과 데이터를 메모리에 로드하여 응답 속도를 개선했습니다.

```python
def create_app():
    app = Flask(__name__)
    # AI 모델 및 분석 데이터 서버 시작 시 로드
    app.model = joblib.load('models/rf_model.pkl')
    app.scaler = joblib.load('models/scaler.pkl')
    # Blueprint 단위 모듈화
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(chatbot_views.bp)
    app.register_blueprint(mask_views.bp)
    # 스케줄러 자동 실행
    start_scheduler(app)

    return app
```

### 6-2. 공공 API 데이터 수집 및 전처리
서울시 Open API(RealtimeCityAir)와 기상청 데이터를 연동하여 구별 대기질 정보를 수집하였습니다.
수집된 원본 JSON 데이터는 서비스 전반에서 일관되게 사용할 수 있도록 표준화된 딕셔너리 구조로 변환하였으며, 예외 처리 및 측정 시간 정보도 함께 관리하도록 설계했습니다.

```python
res = requests.get(url, timeout=5)
data = res.json()

for item in rows:
    gu = item['MSRSTN_NM']

    air_dict[gu] = {
        'pm10': float(item.get('PM')) if item.get('PM') else None,
        'pm25': float(item.get('FPM')) if item.get('FPM') else None,
        'o3': float(item.get('OZON')) if item.get('OZON') else None,
        'no2': float(item.get('NTDX')) if item.get('NTDX') else None,
        'so2': float(item.get('SPDX')) if item.get('SPDX') else None,
        'co': float(item.get('CBMX')) if item.get('CBMX') else None
    }
```

### 6-3. RandomForest 기반 미세먼지 위험도 예측
실시간 대기질 데이터와 과거 시계열 정보, 지역 산업 특성을 결합하여 RandomForest 기반 위험도 예측 모델을 구축하였습니다.

```python
input_dict = {
    'AVG_PM10': c_pm10,
    'PM10_LAG1': pm10_hist[2],
    'PM10_LAG2': pm10_hist[1],
    'PM10_LAG3': pm10_hist[0],

    'AVG_PM25': c_pm25,
    'PM25_LAG1': pm25_hist[2],
    'PM25_LAG2': pm25_hist[1],
    'PM25_LAG3': pm25_hist[0],

    'DUST_TEMP_INTERACTION': c_pm10 * (30 - calc_temp),

    'MANU_RATIO': row_data.get('MANU_RATIO', 0),
    'TRANS_RATIO': row_data.get('TRANS_RATIO', 0),
    'HEALTH_RATIO': row_data.get('HEALTH_RATIO', 0)
}

input_df = pd.DataFrame([input_dict])[cols]

scaled_input = scaler.transform(input_df)

prediction = int(
    model.predict(scaled_input)[0]
)
```
DUST_TEMP_INTERACTION = c_pm10 * (30 - calc_temp)
미세먼지 농도와 기온 간 상호작용 특성을 추가하여 계절 및 기상 변화가 위험도에 미치는 영향을 반영했습니다.

### 6-4. APScheduler 기반 데이터 자동 갱신
실시간 대기질 데이터와 AI 예측 결과를 최신 상태로 유지하기 위해 APScheduler 기반 자동 갱신 시스템을 구축하였습니다.

```python
def start_scheduler(app):

    def update_cache_with_context():
        with app.app_context():
            update_dashboard_cache()

    update_cache_with_context()

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=update_cache_with_context,
        trigger="interval",
        minutes=15,
        id="dust_update_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()
```

### 6-5. REST API 기반 AI 마스크 관제 시스템
직접 학습한 YOLOv8 모델의 탐지 결과를 별도의 AI 서버에서 생성하고, Flask 웹 서비스와 REST API 방식으로 연동하여 실시간 관제 시스템을 구축하였습니다.

```python
res = requests.get(
    "http://localhost:5001/api/predict_mask",
    timeout=0.5
)

data = res.json()

ids = data.get("id_list", [])
clss = data.get("cls_list", [])
```
YOLOv8 탐지 서버에서 객체 ID 및 분류 결과를 수신합니다.


```python
for cls, obj_id in zip(clss, ids):
    if obj_id not in counted_ids:
        counted_ids.add(obj_id)
        current_stats["accum_total"] += 1
        if cls in [0, 3]:
            current_stats["accum_masked"] += 1
        if cls in [3, 4]:
            current_stats["accum_child_total"] += 1
            if cls == 3:
                current_stats["accum_child_masked"] += 1
)
```
객체 ID 기반 중복 제거를 수행하여 동일 인원이 반복 집계되는 문제를 방지하였으며, 전체 착용률과 아동 착용률을 별도로 계산하도록 구현하였습니다.


```python
if current_stats["accum_total"] > 0:
    current_stats["total_rate"] = int(
        (current_stats["accum_masked"] /
         current_stats["accum_total"]) * 100
    )
)
```
탐지 결과를 기반으로 실시간 마스크 착용률을 계산하여 관제 대시보드에 제공합니다.

### 6-6. 지역 기반 AI 챗봇
RunPod LLM API를 활용하여 사용자의 지역과 실시간 대기질 데이터를 반영한 맞춤형 질의응답 서비스를 구현하였습니다.

```python
match = re.search(r'([가-힣]+구)', user_message)

target_gu = (
    match.group(1)
    if match
    else session.get('user_region', '중구')
)
```
사용자 질문에서 지역명을 정규식으로 추출하며, 지역명이 없는 경우 로그인 시 저장된 사용자 지역 정보를 기본값으로 사용하도록 구현했습니다.


```python
analysis_context = (
    f"{target_gu}의 현재 미세먼지(PM10) 농도는 {pm10}이며, "
    f"통합 상태는 '{risk_label}'입니다."
)
```
DB에 저장된 실시간 분석 데이터를 기반으로 지역별 환경 정보를 생성합니다.


```python
response = requests.post(
    RUNPOD_API_URL,
    json=payload,
    timeout=300
)
```
생성된 컨텍스트와 사용자 질문을 결합하여 RunPod LLM API에 전달하고 자연어 답변을 생성합니다.

---


## 🔥 7. 기술적 난관 및 해결 (Troubleshooting)

### ✅ 대량 API 수집 시 병목 현상 해결
- **Problem**: 25개 구의 3일치 데이터를 순차 호출 시 네트워크 대기 시간으로 인해 서비스 지연 발생.
- **Solution**: concurrent.futures.ThreadPoolExecutor를 도입해 I/O Bound 작업을 병렬화하고, 25개 자치구 데이터를 동시에 수집하도록 개선.

### ✅ Oracle DB 데이터 무결성 및 효율 확보
- **Problem**: 빈번한 API 갱신 과정에서 중복 데이터 발생 및 DB I/O 부하 우려.
- **Solution**: Oracle MERGE 문을 활용해 Insert/Update를 단일 쿼리로 처리하고, CLOB OutputTypeHandler를 설정하여 대용량 JSON 캐시 데이터를 안정적으로 저장 및 조회.

### ✅ 실시간 AI 추론 리소스 관리
- **Problem**: 웹 서버 내에서 딥러닝 모델 구동 시 성능 저하 및 UI 프리징 현상.
- **Solution**: 마스크 감지 AI 서버와 Flask 웹 서버를 분리하고, Flask에서는 추론 결과 API를 주기적으로 수집해 current_stats 전역 캐시에 저장. UI는 캐시 데이터를 조회하도록 구성하여 안정성 확보.

### ✅ LLM 챗봇 응답의 신뢰성과 속도 개선
- **Problem**: 사용자 질문마다 외부 API와 LLM을 모두 직접 호출하면 응답 속도가 느려지고, 최신 데이터 기준이 불안정해질 수 있음.
- **Solution**: APScheduler로 15분마다 갱신되는 Oracle DB 캐시를 챗봇의 데이터 소스로 사용. 사용자의 질문에서 지역명을 추출한 뒤, 해당 지역의 최신 미세먼지 분석 결과만 프롬프트에 포함하여 LLM 답변의 범위와 근거를 제한.
---
