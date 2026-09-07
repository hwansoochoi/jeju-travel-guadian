# 스마트 세이프 트래블 가디언 (Safe Travel Guardian)
## 기술 개발 명세서 & 시스템 구현 아키텍처 (Technical Specification)

본 문서는 **스마트 세이프 트래블 가디언** 플랫폼의 iOS 및 Android 모바일 네이티브 애플리케이션, 클라우드 백엔드, 웹 기반 통합 관제 시스템(Admin Dashboard)의 구축 방법, OS별 기술적/법적 제약 분석, 개발 난이도 및 소요 공수(MM)를 정의한 공식 엔지니어링 명세서입니다.

---

## 1. 시스템 전체 아키텍처 (System Architecture)

```
[ 모바일 클라이언트 ]
  ├─ iOS App (Swift 6, SwiftUI, CoreLocation, CoreBluetooth, CallKit)
  └─ Android App (Kotlin, Jetpack Compose, Foreground Service, Nearby Connections)
          │ (HTTPS / WSS / mTLS)
          ▼
[ API Gateway & Security Layer ] (Kong / Cloudflare / Envoy)
          │
[ 마이크로서비스 백엔드 ]
  ├─ Location & Tracking Engine (Go / Redis Geo / Kalman Filter)
  ├─ Risk Radar & Geofencing (FastAPI / PostGIS 공간 인덱싱)
  ├─ Emergency Dispatcher (Kafka / RabbitMQ / WebRTC)
  └─ Public Data Pipeline (Airflow / Celery - 기상청, 천문연, 해양조사원, 경찰청)
          │
[ 데이터베이스 계층 ]
  ├─ Spatial DB: PostgreSQL 16 + PostGIS (궤적, 안심포인트, 지오펜스)
  ├─ In-Memory Cache: Redis 7 (실시간 핑, 세션, 라스트 핑)
  └─ Object Storage: AWS S3 / MinIO (스텔스 녹음 음성 파일, 암호화 보관)
          │
[ 통합 관제탑 (Admin Dashboard) ]
  └─ Web Admin (Next.js 15, React 19, Mapbox GL JS, TailwindCSS, WebSockets)
```

---

## 2. 모바일 플랫폼(iOS / Android) 및 관제 시스템 개발 명세

### 2.1 iOS 클라이언트 개발 명세
- **언어/프레임워크**: Swift 6, SwiftUI, Combine / Swift Concurrency
- **위치 관제**: `CoreLocation`
  - 평상시: `startMonitoringSignificantLocationChanges` (기지국/Wi-Fi 기반 배터리 소모 1% 미만)
  - 올레길/위험구역 진입 시: `kCLLocationAccuracyBestForNavigation` (초정밀 GPS 자동 승격)
- **오프라인 BLE 메시**: `CoreBluetooth`
  - 기지국 통신 두절 감지 시 앱이 `CBPeripheralManager`와 `CBCentralManager`를 동시 활성화하여 백그라운드 BLE 비콘 및 패킷 송수신 릴레이 구동
- **무음 돌파 사이렌**: `AVAudioSession`
  - `.playback` 카테고리 + `.duckOthers` 설정
  - 정식 출시 시 Apple의 **`Critical Alerts` (긴급 재난 경보)** Entitlement 승인 필요
- **잠금화면 상태 중계**: `ActivityKit` (Live Activities & Dynamic Island)
  - 2단계 체크인 타이머, 현재 안심 구간, 배터리 상태를 잠금화면 위젯으로 실시간 표시

### 2.2 Android 클라이언트 개발 명세
- **언어/프레임워크**: Kotlin 2.x, Jetpack Compose, Coroutines/Flow
- **백그라운드 지속 보장**: `Foreground Service` + `TYPE_LOCATION`
  - 배터리 최적화 예외(Doze Mode Whitelist) 권한 획득
- **오프라인 통신**: `Google Nearby Connections API`
  - Wi-Fi Direct 및 BLE 기반 P2P 스타(Star)/메시(Mesh) 토폴로지 구성
- **무음/방해금지 돌파 사이렌**:
  - `NotificationManager.isNotificationPolicyAccessGranted()`
  - 방해금지(DND) 모드를 임시 해제하거나 `AudioAttributes.USAGE_ALARM` 채널 스트림으로 최대 볼륨 사운드 방출
- **스텔스 SOS 감지**:
  - `AccessibilityService` 또는 `MediaSession` 볼륨/미디어 버튼 리스너를 통해 화면 꺼짐 상태의 물리키 연속 클릭 캡처

### 2.3 통합 관제 시스템 (Web Admin Dashboard) 개발 명세
- **프레임워크**: Next.js 15 (App Router), TypeScript, TailwindCSS, Zustand
- **실시간 GIS 지도 엔진**: `Mapbox GL JS` 또는 `Kakao Maps API v2`
  - WebGL 기반 대용량 렌더링 (동시 접속 수만 명의 핀 클러스터링 및 히트맵 처리)
- **실시간 데이터 스트리밍**: `WebSocket / Socket.io`
  - 조난, 10분 정체, 코스 이탈, 피어 SOS 발생 시 0.2초 이내 관제 화면 팝업 경보
- **119 상황실 연동 지령서 모듈**:
  - 국가지점번호 자동 변환 라이브러리(`UTM-K` 좌표계 변환)
  - 원클릭 119 E-Call 지령 패킷 발권 및 관할 소방본부/해경 API 자동 전송

---

## 3. OS별 기술적·법적 제약 및 불가능/제한 항목 심층 검토

| 기능 항목 | Android 구현 가능 여부 | iOS (iPhone) 구현 가능 여부 | 기술적·법적 한계 및 실무 우회 해결책 |
|---|---|---|---|
| **1. 주머니 속 스텔스 SOS (전원 5회 클릭)** | **가능 (우회)**<br>접근성 서비스(Accessibility)로 전원/볼륨키 가로채기 가능 | **불가능 (OS 원천 차단)**<br>Apple 샌드박스 정책상 화면 꺼짐 상태에서 전원키 가로채기 불가 (Apple 자체 긴급구조 112와 충돌) | **[iOS 우회 해결책]**<br>① iOS '뒷면 탭하기(Back Tap)' 손쉬운 사용 기능 연동 (폰 뒷면 3회 두드리기 시 SOS 트리거)<br>② 잠금화면 라이브 액티비티 위젯에 원터치 SOS 슬라이더 노출<br>③ 애플워치 액션 버튼(Action Button) 단축어 연동 |
| **2. 무음모드 강제 돌파 120dB 사이렌** | **가능**<br>`NotificationManager` 방해금지 해제 및 Alarm 채널 볼륨 강제 최대화 | **제한적 (사전 승인 필수)**<br>물리 무음 토글 스위치 켜짐 시 일반 앱의 오디오 출력은 차단됨 | **[iOS 우회 해결책]**<br>① Apple Developer 공식 `Critical Alerts` (중대 경보) 특별 권한 신청 (소방/의료/재난 목적 정식 심사 승인 필요)<br>② 미승인 시 `AVAudioSession.Category.playback`을 활성화하여 벨소리 외 미디어 볼륨 최대 재생 유도 |
| **3. 숙소 Wi-Fi 몰카 IP 스캐닝** | **제한적**<br>Android 11+부터 개인정보 보호로 ARP 테이블 MAC 주소 마스킹 | **제한적**<br>iOS 14+부터 로컬 네트워크 검색 시 사용자 명시적 팝업 동의 필수 | **[우회 해결책]**<br>ARP 테이블을 통한 제조사 식별 대신, **mDNS/Bonjour 프로토콜 기반 RTSP(554), ONVIF(8080) 비디오 스트리밍 포트 오픈 여부만 집중 스캔**하는 지능형 네트워크 진단 방식으로 전환 |
| **4. 성범죄자 주거지 지도 노출** | **기술적 가능** | **기술적 가능** | **[법적 불가 및 우회책]**<br>⚠️ **아동·청소년의 성보호에 관한 법률 제55조 제5항 및 제65조**: 성범죄자 신상정보를 정보통신망을 통해 공개/재배포 시 **5년 이하의 징역 또는 5천만원 이하의 벌금**.<br>➔ **해결책**: 성범죄자의 개별 이름/상세주소를 지도에 노출하지 않고, 경찰청/지자체의 **'야간 치안 위험등급 지오펜스(안전 취약 구역)'** 폴리곤 데이터로 익명 가공하여 반경 진입 시 주의 알림만 발송 |

---

## 4. 모듈별 개발 난이도, 개발 기간 및 소요 공수(MM) 산정표

### 4.1 개발 난이도 및 WBS (Work Breakdown Structure)

| 대분류 | 서브 모듈명 | 상세 개발 내용 | 기술 난이도 | 개발 기간 |
|---|---|---|---|---|
| **모바일 iOS** | 초절전 궤적추적 | Significant Change + 칼만필터 GPS 자동 승격 | **상** | 1.5개월 |
| | BLE 메시 네트워크 | CoreBluetooth Central/Peripheral 동시 릴레이 | **상** | 2.0개월 |
| | 스텔스 SOS & 녹음 | 뒷면 탭/라이브 액티비티 연동, 백그라운드 M4A 압축 전송 | **중상** | 1.5개월 |
| | 사이렌 & 오디오 | Web Audio API / AVAudioSession Critical Alert 연동 | **중** | 1.0개월 |
| **모바일 Android** | 포그라운드 서비스 | Doze 모드 방어, 백그라운드 GPS/가속도 센서 항시 유지 | **상** | 1.5개월 |
| | Nearby 메시 릴레이 | Google Nearby Connections API 기반 P2P 패킷 전파 | **상** | 2.0개월 |
| | DND 우회 사이렌 | AudioManager / NotificationManager 방해금지 해제 | **중** | 1.0개월 |
| | 렌터카 e-Call 감지 | 자이로 센서 충격/전복 알고리즘 & 30초 카운트다운 | **중상** | 1.5개월 |
| **클라우드 백엔드** | 지오펜싱 & 위치엔진 | Redis Geo 기반 반경 1km 피어 탐색, PostGIS 공간 인덱싱 | **상** | 2.0개월 |
| | 공공데이터 수집기 | 기상청 특보, 천문연 일출몰, 해양조사원 만조, 치안지도 파이프라인 | **중** | 1.5개월 |
| | 119 출동 지령기 | UTM-K 국가지점번호 변환 엔진 및 SMS/카카오 알림톡 게이트웨이 | **중상** | 1.5개월 |
| **웹 통합 관제탑** | 실시간 GIS 대시보드 | Mapbox GL 기반 수만 명 실시간 클러스터링 지도 표출 | **상** | 2.0개월 |
| | 이상 탐지 알람 엔진 | 10분 정체자, 코스 이탈자, 피어 SOS 발생 시 관제 팝업 | **중** | 1.5개월 |
| | 인프라 관리 CRUD | 학교지킴이, 24시 편의점, AED, 안심주유소 데이터 관리 | **하** | 1.0개월 |

### 4.2 직군별 투입 공수 (Man-Month, MM) 산정

| 담당 직군 | 인원수 | 참여 기간 | 투입 공수 (MM) | 주 담당 업무 |
|---|---|---|---|---|
| **프로젝트 매니저 (PM)** | 1명 | 4.0개월 | **4.0 MM** | 사업 기획, 지자체/소방청 연계 조율, 마일스톤 관리 |
| **iOS 앱 개발자 (선임/중급)** | 2명 | 4.5개월 (각 3.0) | **6.0 MM** | Swift 네이티브 앱 코어, CoreBluetooth, Live Activities |
| **Android 앱 개발자 (선임/중급)** | 2명 | 4.5개월 (각 3.0) | **6.0 MM** | Kotlin 네이티브 앱, Nearby Connections, 백그라운드 서비스 |
| **백엔드/인프라 엔지니어** | 2명 | 4.0개월 (각 3.0) | **6.0 MM** | FastAPI, PostGIS, Redis Geo, 공공데이터 파이프라인, Kafka |
| **웹 프론트엔드 (관제탑)** | 1명 | 4.0개월 | **4.0 MM** | Next.js 통합 관제 웹, WebSocket 실시간 GIS 상황판 |
| **UI / UX 디자이너** | 1명 | 3.0개월 | **3.0 MM** | 모바일 앱 2종 GUI, 관제 대시보드 UI, 디자인 시스템 |
| **QA / 보안·필드테스터** | 1명 | 3.0개월 | **3.0 MM** | 한라산·곶자왈 통신음영 필드테스트, 센서 오작동 검증 |
| **합계** | **10명** | **총 6개월** | **32.0 MM** | **엔터프라이즈급 완성도 보장** |

---

## 5. 단계별 추진 로드맵 (6개월 WBS)

```
[M1: 기반 설계 & 센서 코어] 
  ├─ DB 스키마 설계 및 공공데이터 수집기 구축
  └─ iOS / Android 초절전 백그라운드 GPS 및 2단계 체크인 엔진 개발

[M2: 통신 음영 극복 & 위기 탈출 모듈]
  ├─ CoreBluetooth / Nearby Connections P2P 메시 릴레이 개발
  └─ 스텔스 SOS, 최대볼륨 사이렌, AI 가상동행 모듈 구현

[M3: 관제 시스템 & 안심포인트 연동 (MVP 완료)]
  ├─ Next.js GIS 실시간 관제탑 개발 및 WebSocket 연동
  └─ 4대 안심포인트(학교, 편의점, 주유소, 지구대) & 병원 최단 대피로 알고리즘

[M4: 모빌리티 & 소방 직결망 고도화]
  ├─ 택시 비정상 경로 이탈 감지 & 렌터카 e-Call 전복 알고리즘
  └─ 119 종합상황실 E-Call 데이터 패키지 자동 연동

[M5: 현장 필드테스트 & 취약점 개선]
  ├─ 제주 산간·곶자왈 실제 통신음영 구역 BLE 릴레이 필드테스트
  └─ 배터리 소모율 최적화 (24시간 보행 시 15% 미만 소모 달성)

[M6: 스토어 심사, 보안 감사 & 정식 런칭]
  ├─ Apple Critical Alerts 심사 및 구글 스토어 정식 등록
  └─ 제주도청/소방본부 공동 시범 서비스 개시
```\n