# 스마트 제주 트래블 가디언 (SMART JEJU TRAVEL GUARDIAN) 🛡️

> **제주 및 전국 단독·안심 여행자를 위한 4대 안전영역 & 16대 전방위 스마트 세이프티 & 긴급 구난 통합 플랫폼**

자연재해·조난부터 도심 범죄·신변 위협, 모빌리티 및 숙소 안전까지, **상시 감시의 거부감은 지우고 단독 여행자의 위기 골든타임을 지키는 실시간 통합 수호 솔루션**입니다.

---

## 🌟 4대 영역 16대 핵심 안전 체계

### 1. 사전 위험 예방 레이더 (Prevention Radar)
1. **공공기관 데이터 실시간 연동**: 기상청 날씨/특보, 한국천문연구원 일출·일몰 시간(당일 일몰 30분 전 산악 하산 권고), 국립해양조사원 만조 데이터(만조 40분 전 해안 갯바위 대피 경보)
2. **범죄다수 발생지역 지오펜싱**: 경찰청 치안통계 및 지자체 범죄지도 연계, 우범지대 및 가로등 취약 골목 진입 시 햅틱 진동 및 안전 우회로 권고
3. **인근 성범죄자 주거지 안내**: 여성가족부 ‘성범죄자 알림e’ 공공데이터 연계, 반경 200m 접근 시 프라이버시 보호형 지능형 사전주의 가이드 발송
4. **숙소 안심 점검 & 불법촬영 탐지**: 카메라 IR 적외선 센서를 이용한 몰카 렌즈 탐지 가이드 및 Wi-Fi 비인가 IP 카메라 스캐닝

### 2. 지능형 모니터링 & 조난 차단 (Smart Monitoring)
5. **단독여행자 실시간 궤적추적**: 올레길·등산로 브레드크럼(Breadcrumb) 이동 궤적 실시간 기록, 코스 이탈 자동 감지
6. **2단계 체크인 (데드맨 스위치)**: 위험구역 10분 정체 시 본인 확인(진동/화면탭/음성) ➔ 3분간 무응답 시에만 비상 전파로 **오경보 90% 차단**
7. **라스트 핑 & 라스트 블랙박스 비콘**:
   - 통신 음영 직전 좌표 서버 박제 + 배터리 3% 방전 직전 최소전력 BLE 비콘 방출로 수색 드론/수색견 탐지 유도
   - **iOS 구현/회피:** `ActivityKit` 킵얼라이브 연동, 셧다운 전 고전력 GPS 차단 ➔ iBeacon 초절전 펄스 전환(3~5시간 지속)
   - **Android 구현/회피:** `Foreground Service` Doze 방어, `Nearby Connections API` P2P 클러스터 메시, 3% 시 비연결형 BLE 패킷(좌표/혈액형) 브로드캐스팅
8. **야생동물 출몰 경보 & 기피 주파수**: 제주 중산간 들개 무리, 멧돼지 출몰지 경고 및 20kHz~25kHz 고주파 사운드 방출

### 3. 위기 대응 & 탈출 (Crisis Response & Escape)
9. **주머니 속 스텔스 무음 SOS**: 화면을 켜지 않고 주머니 속에서 전원버튼 5회 클릭 ➔ 30초 현장 오디오 자동 녹음 및 실시간 좌표 112/보호자 은밀 전송
10. **AI 가짜 통화 & 가상 동행**: 어두운 밤길에서 "누군가와 통화 중"인 상황을 연출하는 AI 음성 가짜 통화 실행 및 보호자 실시간 위치 중계
11. **강제 최대 볼륨 비상 사이렌**: 매너모드/진동 상태 강제 해제, 120dB급 소방/경찰 주파수 변조 사운드(Web Audio API) 및 화면 스트로브 플래시 점멸
12. **여행자 안심포인트 & 최단 대피로**: 학교지킴이집, 24시 안심편의점, 주유소, 지구대/파출소 위치 및 비상 시 원터치 최단 도보 내비게이션 연동
13. **인근 병원 및 응급의료 안내**: 야간/휴일 진료 병·의원, 권역 응급의료센터, 공공 심장충격기(AED) 핀포인트 안내 및 원클릭 응급실 직통 연결

### 4. 모빌리티 & 커뮤니티 연대 (Mobility & Community)
14. **피어(동서비스 이용자) SOS**: 반경 1km 내 동일 앱 이용자 및 등록된 로컬 지킴이(주민, 상인)에게 즉각 긴급 푸시 전파
15. **모빌리티 세이프티**: 택시 권장경로 20% 이상 이탈 시 자동 경고 & 렌터카 전복·충격 감지 자동 e-Call
16. **올레길 안심 동행 매칭 & 다국어 119 TTS**: 본인인증 1인 여행자 간 안전 버디 매칭 및 외국인 관광객을 위한 다국어 한국어 음성 번역 리포트

---

## 🏗️ 전체 시스템 구조도 (System Architecture)

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

---

## 📂 프로젝트 구성

- `index.html`: 18개의 인터랙티브 프레젠테이션 슬라이드 (11번 슬라이드: **라이브 가디언 시뮬레이터**, 13~18번 슬라이드: **iOS/Android 네이티브 개발 명세, 7대 기능 OS 제약 및 불법촬영 현실성 검토, 웹 관제탑(Admin), 코어 모듈 구현, 32MM WBS 공수 산정(예상)**)
- `vercel.json`: Vercel 무설정 정적 호스팅 설정 파일
- `cloudflare/worker.js`: Cloudflare Workers 배포용 초경량 CDN 서빙 스크립트
- `TECHNICAL_SPEC.md`: 모바일 네이티브(iOS/Android), 백엔드, 웹 관제탑, OS별 기술적·법적 제약 우회책, 6개월 개발 WBS 및 32MM 공수 산정(예상)이 명시된 공식 엔지니어링 명세서

---

## 🚀 실행 및 배포 방법

### 1. 로컬에서 실행
`index.html` 파일을 브라우저로 열거나, 로컬 웹서버로 실행합니다.
- 키보드 [←], [→], [Space] 또는 하단 고정 플로팅 바를 통해 18개 슬라이드 이동
- **슬라이드 11**: 비상 사이렌, 스텔스 SOS, AI 가짜 통화, 야생동물 기피음, 택시 경로이탈, BLE 메시 릴레이 등 직접 체험 가능
- **슬라이드 14**: 숙소 불법촬영(IR/Wi-Fi) 기술 현실성 및 7대 핵심 기능 OS 제약·우회 매트릭스 검토
- **슬라이드 15~17**: 통합 관제탑(Admin) 명세, 모바일 코어 모듈 구현 기법 및 총 32MM 공수 산정(예상)표 확인

### 2. Vercel 배포 (권장)
GitHub 저장소를 Vercel에 연동하면 별도 빌드 과정 없이 `index.html`이 전 세계 글로벌 CDN을 통해 초고속 정적 웹사이트로 자동 배포됩니다.

### 3. Cloudflare Workers 배포 (선택)
`cloudflare/worker.js` 코드를 Cloudflare Workers 대시보드에 붙여넣고 배포하거나 Wrangler CLI로 배포합니다.
---

## 🌐 연동 정부 및 민간 OpenAPI 명세 (OpenAPI Registry)

본 플랫폼은 위기 예방 및 실시간 구난을 위해 정부 및 민간의 핵심 OpenAPI를 실시간 연동합니다.

| 연동 서비스명 | 제공 기관 / 기업 | 엔드포인트 / 서비스 URL | 주요 기능 | 인증 방식 |
|---|---|---|---|---|
| **기상특보 & 단기예보** | 기상청 (KMA) | `data.go.kr/1360000/VilageFcstInfoService_2.0` | 호우/강풍/대설 특보 및 시간별 강수 확률 | 공공데이터포털 일반 인증키 |
| **일출·일몰 영력정보** | 한국천문연구원 (KASI) | `data.go.kr/B090041/RiseSetInfoService` | 위치 기반 당일 일몰시각 산출 (일몰 30분 전 하산 권고) | 공공데이터포털 일반 인증키 |
| **바다누리 조석예보** | 국립해양조사원 (KHOA) | `khoa.go.kr/api/oceangrid/tideObsPreTab` | 고조(만조) 시각 산출 (만조 40분 전 갯바위 대피 경보) | 해양정보포털 ServiceKey |
| **생활안전지도 (Safemap)** | 행정안전부 / 국립재난안전연구원 | `safemap.go.kr/openApi` | 치안 5대 범죄 밀집도 WMS 레이어 및 여성안심귀갓길 폴리곤 | Open API Key |
| **응급실 실시간 가용병상** | 국립중앙의료원 (E-Gen) | `data.go.kr/B552657/ErmctInfoInqireService` | 제주대병원/한라병원 실시간 중환자실/응급실 가용병상 | 공공데이터포털 일반 인증키 |
| **공공 자동심장충격기(AED)** | 국립중앙의료원 (E-Gen) | `data.go.kr/B552657/AedInfoInqireService` | 반경 200m 내 공공 AED 비치함 실시간 핀포인트 안내 | 공공데이터포털 일반 인증키 |
| **산악 국가지점번호 변환** | 한국국토정보공사 (LX) | `data.go.kr/1611000/nsdi/GisPosService` | WGS84 ➔ UTM-K / 국가지점번호 100km 한글 격자 변환 | 공공데이터포털 일반 인증키 |
| **카카오 로컬 장소검색** | 카카오 (Kakao Developers) | `dapi.kakao.com/v2/local/search/category.json` | 안심편의점(`CS2`), 안심주유소(`OL7`), 병원(`HP8`) 검색 | KakaoAK REST API Key |
| **카카오내비 최적 경로** | 카카오 모빌리티 | `apis-navi.kakaomobility.com/v1/directions` | 택시 권장경로 폴리라인(이탈 판정) 및 도보 대피로 | KakaoAK REST API Key |
| **카카오 알림톡 게이트웨이** | 카카오 비즈메시지 | `api.bizmsg.kr/v2/sender/send` | 보호자 상황별 맞춤 비상 템플릿 및 실시간 궤적 전송 | API Key + Profile Key |
| **119 다매체 긴급신고** | 소방청 종합상황실 | `119.go.kr` 표준 긴급구조 E-Call 인터페이스 | 국가지점번호, 기저질환, 배터리, 암호화 오디오 S3 패킷 | mTLS 상호 인증 |

---

## 🔗 저장소 및 링크
- **GitHub Repository**: [https://github.com/hwansoochoi/jeju-travel-guardian.git](https://github.com/hwansoochoi/jeju-travel-guardian.git)
- **Clone Command**:
  ```bash
  git clone https://github.com/hwansoochoi/jeju-travel-guardian.git
  ```