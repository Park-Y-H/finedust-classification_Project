# 🌬️ 서울시 AI 미세먼지 보건 분석 및 관제 시스템
> **서울시민의 호흡기 건강을 위한 통합 솔루션**


### 🛠️ Tech Stack
**AI & Computer Vision**
![YOLOv8](https://img.shields.io/badge/YOLOv8-00FFFF?style=flat-square&logo=ultralytics&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=OpenCV&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)

**Backend & Database**
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=Python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=Flask&logoColor=white)
![Oracle](https://img.shields.io/badge/Oracle-F80000?style=flat-square&logo=Oracle&logoColor=white)

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
단순 수치 제공을 넘어, 다각도 데이터를 분석하여 사용자에게 실질적인 '행동 지침'을 제공하는 것을 목표로 합니다.
* **데이터 군집화(Clustering)**: 현재 및 1~3일 전 농도, 기온, 지역 생산성 지표 등을 활용한 데이터 군집화 수행
* **위험 등급 분류**: 실제 환경 기준과 비교 검증을 거쳐 **안전·보통·위험·고위험**의 4단계 등급 체계 구축
* **시각적 정보 전달**: 서울 지도 기반의 색상 표시를 통해 지역별 위험도를 직관적으로 확인 가능하도록 구현
* **맞춤형 가이드**: 등급별 안전 행동 지침 및 상세 원인 분석 대시보드 제공

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
| FR-009 | 인터랙션 | 챗봇 질의응답 | 자연어 질의를 기반으로 지역별 상태 정보를 제공한다. | Medium | 완료 | LLM API |
| FR-010 | 관제 | 마스크 착용 관제 | AI 영상 분석을 기반으로 마스크 착용률 통계를 표시한다. | Medium | 완료 | YOLO 모델 |

### 2-2. 비기능적 요구사항 (Non-Functional Requirements)
| 요구사항 ID | 항목 | 설명 | 기준 |
|:---|:---|:---|:---|
| NFR-001 | 성능 | 캐시 기반 DB 조회로 응답 속도 개선 | 주요 화면 3초 이내 |
| NFR-002 | 보안 | 사용자 비밀번호 해싱 저장 | Werkzeug 해싱 사용 |
| NFR-003 | 보안 | 민감한 설정 정보 환경변수 관리 | .env 사용 |
| NFR-004 | 안정성 | API 장애 시 기존 캐시 활용 | 서비스 중단 방지 |
| NFR-005 | 확장성 | 기능별 모듈 분리(유지보수 용이) | Blueprint/Service 구조 |

---

## 🏗️ 3. 주요 기능 및 고도화 과정

### 시스템 아키텍처 (System Architecture)
본 프로젝트는 데이터 수집(Collection), 분석(Analysis), 서비스(Interface) 계층을 논리적으로 분리하여 설계되었습니다. Flask 서버를 중심으로 각 기능을 Blueprint로 모듈화하고, 데이터 캐싱 및 병렬 처리를 통해 고가용성과 응답 속도를 최적화했습니다.

![서울시 AI-미세먼지 보건 분석 시스템 아키텍처](https://github.com/user-attachments/assets/b504cd53-8937-40b8-b9af-f34931032e09)

### Phase 1: 데이터 분석 및 Flask 기반 웹 서비스 구축
* **멀티 API 연동**: 서울시 RealtimeAir, 기상청 APIHub 등 다각도 데이터 수집
* **성능 최적화**: `ThreadPoolExecutor`를 활용해 25개 자치구의 과거 데이터를 **병렬로 수집**, 로딩 속도 70% 이상 개선
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

## 🔥 4. 기술적 난관 및 해결 (Troubleshooting)

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
