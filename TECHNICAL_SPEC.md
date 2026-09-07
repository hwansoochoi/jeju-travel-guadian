# 스마트 세이프 트래블 가디언 (Safe Travel Guardian)
## 기술 개발 명세서 & 시스템 구현 아키텍처 (Technical Specification)

본 문서는 **스마트 세이프 트래블 가디언** 플랫폼의 iOS 및 Android 모바일 네이티브 애플리케이션, 클라우드 백엔드, 웹 기반 통합 관제 시스템(Admin Dashboard)의 구축 방법, OS별 기술적/법적 제약 분석, 개발 난이도 및 소요 공수(MM)를 정의한 공식 엔지니어링 명세서입니다.

---

## 1. 시스템 전체 아키텍처 및 데이터 흐름 구조도 (System Architecture)

### 1.1 엔드투엔드 시스템 구조도 (Mermaid Flowchart)

```mermaid
graph TD
    subgraph MobileEdge["📱 모바일 클라이언트 & 오프라인 엣지 (Mobile Edge Layer)"]
        iOS["🍎 iOS 네이티브 앱<br>(Swift 6 / CoreLocation / CoreBluetooth / Live Activities / CallKit)"]
        Android["🤖 Android 네이티브 앱<br>(Kotlin / Foreground Service / Nearby Connections / DND 우회)"]
        BLE["📡 P2P 오프라인 메시 & BLE 비콘<br>(라스트 핑 / 배터리 3% 블랙박스 비콘 / 다중 홉 릴레이)"]
    end

    subgraph GatewayLayer["🛡️ 게이트웨이 & 보안 통신망 (API Gateway & Security Layer)"]
        CF["☁️ Cloudflare CDN & WAF<br>(DDoS 차단 / Anycast DNS / SSL 오프로딩)"]
        Kong["🚪 Kong / Envoy API Gateway<br>(mTLS 1.3 / JWT 인증 / Rate Limiting)"]
        WS["⚡ WebSocket / WebRTC 허브<br>(0.2초 초저지연 양방향 위치 스트리밍 & 가상동행)"]
        Kafka["📨 Apache Kafka & RabbitMQ<br>(비동기 이벤트 큐 / 긴급 119 패킷 버스)"]
    end

    subgraph CoreServices["⚙️ 코어 마이크로서비스 & 데이터 파이프라인 (Core Microservices)"]
        LocEngine["📍 실시간 궤적 & 위치엔진<br>(Go / Kalman Filter / OSRM 맵매칭)"]
        RiskRadar["⚠️ 지오펜싱 & 리스크 레이더<br>(FastAPI / PostGIS 공간인덱싱)"]
        CheckIn["⏱️ 2단계 체크인 엔진<br>(Dead Man's Switch / 10분 정체 알람)"]
        PublicData["🌐 공공데이터 파이프라인<br>(Airflow - 기상청 / 천문연 / 해양조사원 / 치안지도)"]
    end

    subgraph DataStorage["💾 데이터베이스 & 분산 스토리지 계층 (Data Persistence Layer)"]
        PostGIS[("🗺️ PostgreSQL 16 + PostGIS<br>(궤적 / 올레길 지오펜스 / 4대 안심포인트)")]
        Redis[("⚡ Redis 7 Cluster<br>(실시간 세션 / 반경 1km 피어 색인 / 라스트 핑)")]
        S3[("🔒 AWS S3 / MinIO<br>(스텔스 녹음 30초 오디오 AES-256 암호화 보관)")]
    end

    subgraph DispatchAdmin["🚨 통합 관제탑 & 유관기관 연계 계층 (Admin & Emergency Integration)"]
        AdminWeb["🖥️ 웹 통합 관제탑 (Next.js 15)<br>(Mapbox GL JS 실시간 GIS 상황판 / 현장 지령)"]
        Fire119["🚒 119 소방 종합상황실<br>(UTM-K 국가지점번호 E-Call 구조 패킷 직결)"]
        Police112["🚓 112 경찰 & 피어 지킴이망<br>(도심 우범지역 순찰차 직결 / 1km 피어 비상 푸시)"]
        Kakao["💬 보호자 긴급 통보 게이트웨이<br>(카카오 알림톡 & 통신사 재난 SMS 실시간 링크)"]
    end

    iOS -->|HTTPS / WSS / mTLS| CF
    Android -->|HTTPS / WSS / mTLS| CF
    BLE -.->|오프라인 P2P 릴레이| iOS
    BLE -.->|오프라인 P2P 릴레이| Android

    CF --> Kong
    Kong --> WS
    Kong --> CoreServices

    WS <--> LocEngine
    CoreServices --> Kafka
    Kafka --> LocEngine
    Kafka --> RiskRadar
    Kafka --> CheckIn
    PublicData --> RiskRadar

    LocEngine <--> Redis
    LocEngine --> PostGIS
    RiskRadar --> PostGIS
    CheckIn --> PostGIS
    CoreServices --> S3

    Kafka --> AdminWeb
    Kafka --> Fire119
    Kafka --> Police112
    Kafka --> Kakao
    AdminWeb <--> WS
```

### 1.2 계층별 아키텍처 상세 다이어그램

```
[ Layer 1: 클라이언트 계층 (Mobile & User Edge) ]
  ├── iOS 네이티브 앱 (Swift 6, CoreLocation, CoreBluetooth 메시, Live Activities, Critical Alerts)
  ├── Android 네이티브 앱 (Kotlin, Foreground Service, Nearby Connections, DND 우회, 센서 융합)
  └── IoT & P2P 오프라인 노드 (BLE 비콘 브리지, 비상 라스트 핑, 여행자 P2P 릴레이)
             │
             ▼ (HTTPS / WSS / mTLS 1.3)
[ Layer 2: 게이트웨이 & 실시간 통신망 (API Gateway & Security Layer) ]
  ├── Cloudflare CDN / DDoS 방어 / WAF
  ├── Kong / Envoy API Gateway (JWT 인증, Rate Limiting, 로드밸런싱)
  └── WebSocket & WebRTC 시그널링 허브 (0.2s 초저지연 양방향 위치 중계)
             │
             ▼ (gRPC / Async Event Bus - Kafka / RabbitMQ)
[ Layer 3: 코어 서비스 마이크로서비스 (Core Microservices & Event Stream) ]
  ├── 실시간 궤적 & 위치 추적 엔진 (Go, Kalman Filter, OSRM 맵 매칭)
  ├── 지오펜싱 & 리스크 레이더 (FastAPI, PostGIS 공간 인덱싱, 위험구역 판정)
  ├── 2단계 체크인 & 데드맨 스위치 (10분 정체자 이상 감지 알고리즘)
  └── 공공데이터 파이프라인 (Airflow / Celery - 기상청, 천문연, 해양조사원, 경찰청)
             │
             ▼ (JDBC / Redis Protocol / S3 API)
[ Layer 4: 데이터베이스 & 스토리지 계층 (Data Persistence Layer) ]
  ├── 공간 DB: PostgreSQL 16 + PostGIS (궤적, 안심포인트, 코스 지오메트리)
  ├── 인메모리 캐시: Redis 7 Cluster (실시간 핑, 세션, 반경 1km 피어 색인)
  └── 암호화 스토리지: AWS S3 / MinIO (스텔스 녹음 음성 파일 AES-256 저장)
             │
             ▼ (WebSocket / E-Call REST API / SMS Gateway)
[ Layer 5: 통합 관제탑 & 공공 연계망 (Admin & Emergency Integration) ]
  ├── 웹 통합 관제탑 (Next.js 15, React 19, Mapbox GL JS, 실시간 GIS 상황판)
  ├── 119 소방 종합상황실 & 112 경찰청 긴급 출동 지령 시스템 직결 (UTM-K 좌표)
  └── 보호자 긴급 SMS & 카카오 알림톡 게이트웨이
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

### 3.1 숙소 불법촬영 점검 (IR 적외선 렌즈 & Wi-Fi IP 스캐닝) 현실성 및 구현 계획

#### [현실적 가능 여부 결론]
**조건부 구현 가능 (실효 검출율 약 75%~85%)**.  
단일 센서나 일반 카메라만으로는 물리적/보안적 한계가 명확하므로, **"광학 재귀반사 AI + 전면 IR 수신 + C클래스 스트리밍 포트 스캔"**의 3단계 하이브리드 파이프라인으로 구축해야 상용 수준의 실효성을 가집니다.

#### (1) IR 적외선 렌즈 광학 탐지 (하드웨어/센서 메커니즘)
- **물리적·하드웨어 한계**:
  - 스마트폰 **후면 메인 카메라**는 주간 촬영 품질(색상 왜곡 방지)을 위해 렌즈 앞에 물리적인 **IR-Cut 필터(적외선 차단 필터)**가 증착되어 있어, 850nm / 940nm 파장의 적외선 LED를 차단합니다.
  - 몰카 렌즈 자체는 전자석 발광체가 아니므로 주간에는 스스로 빛을 내지 않습니다.
- **실무 구현 파이프라인**:
  1. **야간 조명 소등 발광체 탐지 (전면 셀피 카메라)**:
     - 전면 카메라(TrueDepth / 셀피 센서)는 얼굴 인식 및 저조도 감도를 위해 IR-Cut 필터가 없거나 매우 약합니다.
     - 객실 내 불을 모두 끈 상태에서 전면 카메라 프리뷰를 구동하면, 야간 촬영용 몰카의 적외선 LED(850nm)가 화면에 선명한 보라색/백색 점광원으로 실시간 노출됩니다.
  2. **주간 핀홀 렌즈 재귀반사(Retro-reflection) AI 검출**:
     - 스마트폰 후면 LED 플래시를 점등한 상태에서 카메라 프리뷰 프레임을 OpenCV 파이프라인으로 전송합니다.
     - 핀홀 렌즈의 광학 유리 및 코팅 곡면에서 광원이 정확히 180도 역반사(재귀반사)되는 원형 고휘도 반사광(Red-dot/White-dot)을 `Circle Hough Transform` 및 `Blob Detection` 알고리즘으로 추출합니다.
     - 탐지된 반사점 주변의 반사율과 깜빡임 주기를 머신러닝으로 분석하여 화면상에 AR 위험 타겟팅 서클을 렌더링합니다.
  3. **LiDAR / ToF 센서 표면 왜곡 분석 (iPhone Pro / 최신 Galaxy)**:
     - 905nm 적외선 레이저 펄스를 방출하여 물체 표면의 거리와 반사율(Reflectivity)을 3D 포인트 클라우드로 수집합니다.
     - 환풍구, 화재경보기, 콘센트 벽면의 균일한 평면 데이터 중 직경 1~2mm 수준의 미세 핀홀 구멍과 비정상 굴절률을 가진 렌즈 표면의 심도 이상치를 추출합니다.

#### (2) Wi-Fi 비인가 IP 카메라 스캐닝 (네트워크 메커니즘)
- **현실적 환경 한계**:
  - **AP Isolation (클라이언트 격리)**: 5성급 호텔 등 기업용 AP망은 기기간 패킷 통신(ARP/TCP)을 차단하므로 스캐닝이 불가능합니다. (반면 일반 펜션, 모텔, 에어비앤비, 게스트하우스 등 소상공인 공유기는 95% 이상 AP Isolation이 해제되어 있어 100% 스캔 가능).
  - **SD카드 로컬 저장형 몰카 / 자체 LTE 에그 몰카**: Wi-Fi 망에 접속하지 않으므로 네트워크 스캔으로는 검출 불가 (➔ 위의 광학/IR 탐지 파이프라인으로 방어).
- **OS 보안 정책 제약**:
  - **iOS 14+**: 앱이 로컬 네트워크를 스캔하려면 `NSLocalNetworkUsageDescription` 권한 팝업을 띄워 사용자 명시적 승인을 받아야 함.
  - **iOS/Android 공통**: 커널 레벨의 ARP 테이블 접근이 차단되어 IP에 대응하는 하드웨어 MAC 주소(OUI 제조사 조회)를 직접 가져올 수 없음.
- **실무 우회 구현 파이프라인**:
  1. 스마트폰이 연결된 Wi-Fi의 기본 게이트웨이(예: `192.168.0.1`) 및 서브넷 마스크를 확인하여 C-Class 서브넷(`192.168.0.1 ~ 192.168.0.254`) 대역 산출.
  2. 비동기 소켓 코루틴(Kotlin Coroutines / Swift Concurrency)을 통해 254개 전체 IP를 대상으로 영상 스트리밍 특화 포트를 초고속 병렬 스캔:
     - **Port 554**: RTSP (Real Time Streaming Protocol, 전 세계 IP 카메라 표준)
     - **Port 3702**: ONVIF (IP 네트워크 카메라 디바이스 자동 탐색 프로토콜)
     - **Port 80, 8080, 8000**: IP 카메라 웹 관리 콘솔 및 HTTP-FLV 비디오 스트림
     - **Port 1935**: RTMP 비디오 전송
  3. **mDNS (Bonjour) / SSDP (UPnP)** 멀티캐스트 패킷을 브로드캐스팅하여 응답하는 디바이스 헤더 파싱.
  4. 수신된 HTTP Server 배너 문자열 및 RTSP 응답 헤더에서 알려진 IP 카메라 제조사 시그니처(`Hikvision`, `Dahua`, `Tuya`, `Ezviz`, `Reolink`, `XMEYE` 등)를 정규식 매칭하여 비인가 카메라 발견 시 즉각 알림.

---

### 3.2 7대 핵심 기능 종합 OS별 기술적·법적 제약 및 실무 우회 매트릭스

| 기능 항목 | Android 환경 | iOS (iPhone) 환경 | 기술적·법적 한계 및 실무 엔지니어링 우회 방안 |
|---|---|---|---|
| **1. 숙소 불법촬영 (IR 렌즈 & Wi-Fi IP)** | **제한적 가능**<br>전면카메라 + OpenCV 반사광, Wi-Fi 포트 스캔 | **제한적 가능**<br>전면카메라 + LiDAR, Local Network 권한 후 RTSP 스캔 | **[한계]** 후면 렌즈 IR-Cut 필터 및 엔터프라이즈 AP Isolation 격리망 한계.<br>**[우회]** '소등 전면카메라 야간 LED 감지 + 플래시 재귀반사 OpenCV 필터 + C클래스 RTSP(554)/ONVIF(3702) 포트 스캔' 3단계 하이브리드 파이프라인 구축 |
| **2. 스텔스 무음 SOS (물리키 5회 연타)** | **가능 (우회)**<br>AccessibilityService로 전원/볼륨키 가로채기 가능 | **불가능 (OS 원천 차단)**<br>Apple 샌드박스 정책상 화면 잠금 시 전원키 이벤트 앱 전달 원천 차단 | **[한계]** Apple 보안 정책상 하드웨어 키 가로채기 불가 (기본 긴급구조 112 충돌).<br>**[우회]** iOS '뒷면 탭하기(Back Tap)' 단축어 연동, Siri 음성 비상 트리거, 잠금화면 Live Activities 위젯, 애플워치 액션버튼으로 우회 |
| **3. 무음·진동 돌파 120dB 사이렌** | **가능**<br>NotificationManager 방해금지 해제 및 Alarm 채널 최대 볼륨 | **제한적 (사전승인 필수)**<br>물리 무음 토글 스위치 켜짐 시 일반 앱의 오디오 출력 차단 | **[한계]** iOS 하드웨어 무음 스위치 켜짐 시 백그라운드 오디오 차단 원칙.<br>**[우회]** Apple Developer 공식 `Critical Alerts(중대 경보)` Entitlement 심사 승인 획득 (인명구조 앱 전용 허용), 미승인 시 `AVAudioSession.playback` 카테고리 설정 |
| **4. 성범죄자 알림e 및 주거지 지도 표출** | **기술적 구현 가능** | **기술적 구현 가능** | **[⚠️ 법적 전면 불가 (아청법 위반)]**<br>아동·청소년의 성보호에 관한 법률 제55조 제5항 위반 시 **5년 이하의 징역 또는 5천만원 이하의 벌금**.<br>**[우회]** 성범죄자 개인정보 표기를 전면 배제하고, 행안부/경찰청 '생활안전지도 5대 범죄 발생통계' 및 '야간 안심귀갓길 지오펜스 폴리곤'으로 100% 합법 가공 표출 |
| **5. 오프라인 음영지역 BLE 메시 릴레이** | **가능**<br>Nearby Connections 및 BLE 백그라운드 상시 수신 | **제한적**<br>화면 꺼짐 시 백그라운드 BLE Advertising 주기 15분 이상 지연 | **[한계]** iOS 배터리 정책상 백그라운드 BLE 패킷 전달 주기 급증으로 실시간 중계 지연.<br>**[우회]** Android 기기를 상시 브리지 중계 노드(Relay Node)로 작동하도록 비대칭 메시(Asymmetric Mesh) 토폴로지 설계, iOS는 포그라운드 유지 유도 |
| **6. 야생동물(들개·멧돼지) 기피 고주파** | **제한적**<br>모바일 스피커 18kHz 이상 출력 SPL 급감 | **제한적**<br>모바일 스피커 하드웨어 음압(SPL) 급감 | **[한계]** 스마트폰 마이크로 스피커는 18kHz 이상 초음파 재생 시 음압이 40dB 이하로 급감하여 야외 동물 퇴치 실효성 미흡.<br>**[우회]** 단순 초음파 지양 ➔ 맹수(호랑이/표범) 포효 및 파열음(가청 2~4kHz 최대 SPL 방출) + 카메라 플래시 고속 스트로보(Strobe Flash) 결합 복합 방어 |
| **7. 모빌리티 이상 감지 (택시/렌터카)** | **가능**<br>GPS + 센서 융합 | **가능**<br>CoreLocation + CoreMotion | **[한계]** 산간 터널/도로에서 GPS 튀는 현상(Multipath)으로 인한 오경보 및 폰 단순 낙하(Drop) 오인.<br>**[우회]** 택시 이탈은 OSRM 맵 매칭 + 칼만 필터(5회 연속 100m 이탈 시 경보), 렌터카 전복은 '감속도 >4G + 자이로 전복각 >60° + 주행속도 급감' 3중 융합 필터 적용 |

---

### 3.3 앱스토어 심사 통과 및 법률 준수(Compliance) 핵심 전략
1. **Apple Critical Alerts Entitlement 획득 전략**:
   - 인명구조, 조난구조 목적임을 증빙하는 제주특별자치도 또는 소방방재청과의 공식 MOU/공문 서류를 첨부하여 Apple Developer Relations 팀에 정식 신청.
2. **아청법 제55조 컴플라이언스**:
   - 성범죄자 개별 이름, 얼굴, 세부 번지수 표출을 시스템 레벨에서 원천 배제하고, 지자체 공공 치안 등급 데이터(안전/주의/경고 폴리곤)로만 렌더링하여 법적 형사처벌 리스크 0% 달성.
3. **배터리 수명 및 백그라운드 프로세스 생존율 극대화**:
   - 무조건적인 고빈도 GPS 폴링을 지양하고, Significant Change Location API + 이동 가속도(Accelerometer) 융합을 통해 평상시 배터리 소모율을 1시간당 0.8% 미만으로 유지.

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
```

---

## 6. 정부 및 민간 공공 OpenAPI 접속 규격 및 연동 명세 (OpenAPI Integration Specifications)

본 플랫폼은 정부 공공기관(기상청, 천문연구원, 해양조사원, 행정안전부, 경찰청, 국립중앙의료원, 국토정보공사, 소방청) 및 민간 테크 기업(카카오, 통신사)의 공공/상용 OpenAPI를 실시간 연동합니다.

### 6.1 공공데이터포털(data.go.kr) 기반 정부 공공 OpenAPI 연동 규격

| 서비스명 | 제공 기관 | 기본 요청 URL 및 엔드포인트 | 인증 방식 | 요청 파라미터 (주요) | 응답 포맷 | 수집 주기 / 캐시 TTL |
|---|---|---|---|---|---|---|
| **기상특보 조회서비스** | 기상청 (KMA) | `http://apis.data.go.kr/1360000/WthrWrnInfoService/getWthrWrnList` | 일반 인증키 (`serviceKey`) | `pageNo=1&numOfRows=10&dataType=JSON` | JSON | 30분 / Redis 1800s |
| **단기예보 조회서비스** | 기상청 (KMA) | `http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst` | 일반 인증키 (`serviceKey`) | `base_date=YYYYMMDD&base_time=HHMM&nx=52&ny=38` (제주) | JSON | 1시간 / Redis 3600s |
| **출몰영력정보 (일출·일몰)** | 한국천문연구원 (KASI) | `http://apis.data.go.kr/B090041/openapi/service/RiseSetInfoService/getAreaRiseSetInfo` | 일반 인증키 (`serviceKey`) | `locdate=YYYYMMDD&location=제주` | XML/JSON | 1일 1회 (자정) / 24h |
| **조석예보 (만조·간조)** | 국립해양조사원 (KHOA) | `http://www.khoa.go.kr/api/oceangrid/tideObsPreTab/search.do` | 서비스키 (`ServiceKey`) | `ObsCode=DT_0004(제주)&Date=YYYYMMDD` | JSON | 1일 1회 / Redis 24h |
| **생활안전지도 (Safemap)** | 행정안전부 / 국립재난안전연구원 | `https://www.safemap.go.kr/openApi/sub.do` | Open API Key | `layers=A2SM_CRIME_ALL&styles=A2SM_CRIME_ALL` (WMS/WFS) | GeoJSON / WMS 타일 | 월 1회 동기화 (PostGIS 저장) |
| **응급실 실시간 가용병상** | 국립중앙의료원 (E-Gen) | `http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire` | 일반 인증키 (`serviceKey`) | `STAGE1=제주&STAGE2=제주시` | XML/JSON | 5분 / Redis 300s |
| **공공 자동심장충격기(AED)** | 국립중앙의료원 (E-Gen) | `http://apis.data.go.kr/B552657/AedInfoInqireService/getAedLcinfoInqire` | 일반 인증키 (`serviceKey`) | `WGS84_LON=126.5&WGS84_LAT=33.3&pageNo=1` | XML/JSON | 주 1회 동기화 (PostGIS 공간 인덱스) |
| **산악 국가지점번호 변환** | 한국국토정보공사 (LX) | `http://apis.data.go.kr/1611000/nsdi/GisPosService` | 일반 인증키 (`serviceKey`) | `coordType=WGS84&x=126.5&y=33.3` | JSON | 실시간 변환 (내장 알고리즘 병행) |

---

### 6.2 민간 테크 플랫폼 및 긴급 출동 연계 OpenAPI

| 서비스명 | 제공사 / 기관 | 기본 요청 URL 및 엔드포인트 | 인증 방식 | 주요 기능 및 전달 데이터 | 호출 트리거 / 응답 속도 |
|---|---|---|---|---|---|
| **카카오 로컬 카테고리 검색** | 카카오 (Kakao Developers) | `https://dapi.kakao.com/v2/local/search/category.json` | Header: `Authorization: KakaoAK {REST_API_KEY}` | 안심편의점(`CS2`), 안심주유소(`OL7`), 병원(`HP8`), 약국(`PM9`) 반경 500m 검색 | 위기 발생 또는 지도 이동 시 / 0.1초 |
| **카카오내비 최적 경로** | 카카오 모빌리티 | `https://apis-navi.kakaomobility.com/v1/directions` | Header: `Authorization: KakaoAK {REST_API_KEY}` | 택시 권장 경로 폴리라인(경로이탈 판정 기준선) 및 안심포인트 최단 대피로 산출 | 경로 생성 시 / 0.2초 |
| **카카오 알림톡 게이트웨이** | 카카오 i 커넥트 / 비즈엠 | `https://api.bizmsg.kr/v2/sender/send` | API Key + Sender Profile Key | 보호자 상황별 맞춤 템플릿(정체, 이탈, 조난 SOS) 및 실시간 궤적 조회 링크 발송 | 2단계 체크인 3분 무응답 시 / 0.5초 |
| **소방청 119 다매체 긴급신고** | 소방청 종합상황실 (119.go.kr) | 국가재난안전 E-Call 게이트웨이 표준 인터페이스 | mTLS 상호 인증 + 지자체 전용 암호화 토큰 | 신고자 신원, 성별, 위경도, UTM-K 국가지점번호, 기저질환, 배터리 잔량, 암호화 오디오 S3 URL 패킷 전송 | 원클릭 119 전송 버튼 또는 낙상/전복 확정 시 / 즉시 전송 |

---

### 6.3 OpenAPI 장애 대응 (Fail-over) 및 쿼터 관리 정책
1. **공공데이터포털 트래픽 쿼터 방어**:
   - 일일 10,000건 기본 제한을 초과하지 않도록 Redis 인메모리 캐시를 적용하여 기상/특보/만조/일출몰 데이터를 수만 명의 사용자에게 1회 호출로 서빙.
2. **네트워크 장애 및 지연 대비 로컬 오프라인 Fallback**:
   - 국가지점번호: 외부 API 서버 장애 시 앱 내장 `UTM-K ➔ 국가지점번호 100km 격자 수식 연산 엔진(Swift/Kotlin)`으로 네트워크 없이 0.001초 만에 로컬 산출.
   - 4대 안심포인트: 제주도 내 24시 편의점, 주유소, 지구대 좌표를 SQLite/Room/CoreData에 사전 임베딩하여 오프라인에서도 즉시 최단 피난처 안내.\n