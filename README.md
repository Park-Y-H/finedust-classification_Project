# 🌬️ 서울시 AI 미세먼지 보건 분석 및 관제 시스템
> **서울시민의 호흡기 건강을 위한 통합 솔루션**


### 🛠️ Tech Stack
**AI & Computer Vision**
![YOLOv8](https://img.shields.io/badge/YOLOv8-00FFFF?style=flat-square&logo=ultralytics&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=OpenCV&logoColor=white)

**Backend & Database**
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=Flask&logoColor=white)
![Oracle](https://img.shields.io/badge/Oracle-F80000?style=flat-square&logo=Oracle&logoColor=white)

**Data Processing**
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=Pandas&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-2CA5E0?style=flat-square&logo=python&logoColor=white)

---

## 🎯 1. 기획 의도 및 개발 목표

### 1-1. 기획 의도 (Background)
미세먼지는 체내 배출에 2~3일이 소요되는 1급 발암물질입니다. 단순히 "현재 농도"만 보여주는 기존 서비스의 한계를 넘어, **과거 누적 위험도를 시각화**하고 
**AI 관제(마스크 착용률)**를 통해 실질적인 보건 예방책을 제시하고자 했습니다.

<p align="center">
  <img width="800" alt="미세먼지 자료 1" src="https://github.com/user-attachments/assets/298ff777-7331-4e81-bb8c-d4689b6d0c6b" />
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

## 🏗️ 2. 주요 기능 및 고도화 과정

### Phase 1: 데이터 분석 및 Flask 기반 웹 서비스 구축
* **멀티 API 연동**: 서울시 RealtimeAir, 기상청 APIHub 등 다각도 데이터 수집
* **성능 최적화**: `ThreadPoolExecutor`를 활용해 25개 자치구의 과거 데이터를 **병렬로 수집**, 로딩 속도 70% 이상 개선
* **데이터 지속성**: Oracle DB의 `MERGE INTO` 문을 사용하여 효율적인 데이터 캐싱 및 이력 관리 구현

### Phase 2: 딥러닝 모델 도입 및 서비스 확장
* **AI 실시간 관제**: YOLOv8 기반으로 영상 내 마스크 착용 여부 및 객체(Child/Adult) 분류
* **관제 대시보드**: 실시간 마스크 착용률 통계 및 고위험 상황 경보(Alert) 시스템 연동
* **시스템 통합**: 분석된 미세먼지 수치와 AI 관제 결과를 하나의 Flask 통합 서비스로 제공

---

## 🔥 3. 기술적 난관 및 해결 (Troubleshooting)

### ✅ 대량 API 수집 시 병목 현상 해결
- **Problem**: 25개 구의 3일치 데이터를 순차 호출 시 네트워크 대기 시간으로 인해 서비스 지연 발생.
- **Solution**: `concurrent.futures.ThreadPoolExecutor`를 도입하여 I/O Bound 작업을 병렬화. 사용자 응답 속도를 획기적으로 개선.

### ✅ Oracle DB 데이터 무결성 및 효율 확보
- **Problem**: 빈번한 API 갱신 과정에서 중복 데이터 발생 및 DB I/O 부하 우려.
- **Solution**: 단일 쿼리로 Insert/Update가 가능한 `MERGE` 문을 작성하고, CLOB 데이터 타입 최적화를 위해 `OutputTypeHandler`를 설정하여 대용량 JSON 데이터 처리를 안정화.

### ✅ 실시간 AI 추론 리소스 관리
- **Problem**: 웹 서버 내에서 딥러닝 모델 구동 시 성능 저하 및 UI 프리징 현상.
- **Solution**: 전역 변수 기반의 캐싱 구조(`current_stats`)를 설계하여 모델의 추론 결과와 웹 UI 업데이트 로직을 분리, 안정적인 서비스 제공.

---
