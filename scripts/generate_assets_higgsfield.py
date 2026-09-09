#!/usr/bin/env python3
"""
스마트 제주 트래블 가디언 (SMART JEJU TRAVEL GUARDIAN)
Higgsfield AI (each::labs) 연동 에셋 생성 자동화 파이프라인

용도:
- 앱 온보딩 및 제안서 덱에 사용할 비(非)구난 UI 비주얼 에셋의 사전(offline) 생성

적용 범위 제한 (TECHNICAL_SPEC.md §11 Safety Boundary):
- 생성형 AI 산출물은 실시간 구조 판단 경로에 개입하지 않는다.
- 119 관제 화면 및 구조대원 단말에 AI 합성 지형·기상 이미지를 표출하지 않는다.
  (실제 지형과 불일치 시 현장 오판 및 수색 지연 위험)

API 규격 출처: docs.eachlabs.ai / docs.higgsfield.ai
- each::labs 경유: Authorization: Bearer $EACHLABS_API_KEY
- Higgsfield 직접 호출 시에는 스킴이 다름:
  Authorization: Key ${HF_API_KEY_ID}:${HF_API_KEY_SECRET}  (api.higgsfield.ai)
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error

# each::labs 는 모델별 개별 경로가 아니라 단일 prediction 엔드포인트를 사용한다.
# 사용할 모델은 요청 본문의 "model" 필드로 지정한다. (docs.eachlabs.ai)
API_ENDPOINT = os.getenv("EACHLABS_API_URL", "https://api.eachlabs.ai/v1/prediction")
API_KEY = os.getenv("EACHLABS_API_KEY") or os.getenv("HIGGSFIELD_API_KEY", "")

# 모델 식별자는 each::labs 대시보드에서 확인해야 하며 변동될 수 있음  [검증 필요]
MODEL_ID = os.getenv("EACHLABS_MODEL_ID", "higgsfield/higgsfield-ai-visual-effects")

# 산출물 저장 루트 (정적 배포 대상 디렉터리)
OUTPUT_ROOT = os.getenv("ASSET_OUTPUT_ROOT", "public")

# 프롬프트 프리셋 (제주 트래블 가디언 비주얼 가이드라인)
ASSET_PRESETS = {
    "hero_guardian": {
        "title": "야간 제주 가디언 키 비주얼",
        "filename": "assets/hero_jeju_guardian.png",
        "aspect_ratio": "16:9",
        "prompt": (
            "Cinematic photorealistic shot of a solo female hiker walking on a misty Jeju Gotjawal forest trail at twilight, "
            "a sleek autonomous search-and-rescue emergency drone hovering above with a subtle glowing cyan and emerald safety beacon beam, "
            "atmospheric fog, volcanic basalt rocks, lush ferns, 8k resolution, Unreal Engine 5 render, cyberpunk naturalism"
        ),
        "negative_prompt": "cartoon, low quality, blurry, horror, grotesque, distorted faces, watermark"
    },
    "stealth_sos": {
        "title": "주머니 속 스텔스 무음 SOS",
        "filename": "assets/stealth_sos_macro.png",
        "aspect_ratio": "1:1",
        "prompt": (
            "Dramatic close-up macro shot of a person's hand pressing a modern smartphone power button repeatedly inside a dark coat pocket, "
            "covert subtle emerald haptic pulse indicator, tension, cinematic shallow depth of field, photorealistic, 8k"
        ),
        "negative_prompt": "bright screen, illuminated face, noisy, amateur"
    },
    "virtual_companion": {
        "title": "AI 가상동행자 페르소나 아바타",
        "filename": "assets/virtual_companion_avatar.png",
        "aspect_ratio": "1:1",
        "prompt": (
            "Friendly, reassuring, warm smiling female Korean safety assistant avatar, 3D Pixar-Disney stylized realism, "
            "wearing smart outdoor travel jacket with subtle guardian shield badge, gentle studio lighting, clean background, 8k"
        ),
        "negative_prompt": "scary, uncanny valley, robotic, dark, sad"
    },
    "last_beacon_drone": {
        "title": "라스트 블랙박스 비콘 수색 드론",
        "filename": "assets/last_beacon_drone.png",
        "aspect_ratio": "16:9",
        "prompt": (
            "High-tech Korean fire and rescue department (119) quadcopter drone scanning a dark Hallasan mountain ridge with LiDAR and infrared sensors, "
            "tracking a glowing pulse from a lost hiker's smartphone BLE beacon, cinematic night photography, high contrast, 8k"
        ),
        "negative_prompt": "military weapon, crash, war, explosion, lowres"
    }
}

def generate_asset_higgsfield(key: str, preset: dict, api_key: str):
    print(f"[*] Higgsfield API 작업 요청: [{preset['title']}] ({key})")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # each::labs 규격: 생성 파라미터는 최상위가 아니라 "input" 객체 안에 중첩한다.
    # input 이 받는 키 집합은 모델마다 다르므로 연동 전 해당 모델 문서를 확인할 것.  [검증 필요]
    payload = {
        "model": MODEL_ID,
        "input": {
            "prompt": preset["prompt"],
            "negative_prompt": preset.get("negative_prompt", ""),
            "aspect_ratio": preset.get("aspect_ratio", "16:9"),
        },
    }
    
    req = urllib.request.Request(
        API_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            task_id = data.get("task_id") or data.get("id")
            print(f"[+] 작업 생성 완료 (Task ID: {task_id}). 렌더링 대기 중...")
            
            # 폴링 로직 (실제 API 응답 구조에 맞춤)
            output_url = data.get("output_url") or (data.get("output", [None])[0] if isinstance(data.get("output"), list) else None)
            if not output_url and task_id:
                # 비동기 상태 확인
                # 결과 조회 경로는 공식 문서로 재확인 필요  [검증 필요]
                poll_url = f"{API_ENDPOINT}/{task_id}"
                for _ in range(30):
                    time.sleep(3)
                    poll_req = urllib.request.Request(poll_url, headers=headers)
                    with urllib.request.urlopen(poll_req) as p_resp:
                        p_data = json.loads(p_resp.read().decode("utf-8"))
                        if p_data.get("status") == "completed":
                            output_url = p_data.get("output_url")
                            break
            
            if output_url:
                dest = os.path.join(OUTPUT_ROOT, preset["filename"])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                urllib.request.urlretrieve(output_url, dest)
                print(f"[SUCCESS] 에셋 다운로드 완료 -> {dest}")
            else:
                print(f"[INFO] 결과 대기 타임아웃 또는 URL 수신 완료: {data}")
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Higgsfield HTTP Error: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERROR] 파이프라인 예외 발생: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Higgsfield AI 에셋 생성 도구")
    parser.add_argument("--preset", choices=list(ASSET_PRESETS.keys()) + ["all"], default="all", help="생성할 프리셋 선택")
    parser.add_argument("--api-key", default=API_KEY, help="each::labs API Key (Bearer)")
    parser.add_argument("--list", action="store_true", help="등록된 프리셋 목록 출력")
    
    args = parser.parse_args()
    
    if args.list:
        print("=== 등록된 스마트 제주 트래블 가디언 에셋 프리셋 ===")
        for k, v in ASSET_PRESETS.items():
            print(f"- {k}: {v['title']} ({v['aspect_ratio']}) -> {v['filename']}")
        return

    api_key = args.api_key or API_KEY
    if not api_key:
        print("[!] EACHLABS_API_KEY가 설정되지 않았습니다.")
        print("    사용법: export EACHLABS_API_KEY='your_key' 후 실행하거나 --api-key 인자로 전달하십시오.")
        print("    (오프라인 모드에서는 Antigravity 기본 비주얼 생성 도구 또는 목업 에셋이 사용됩니다.)")
        sys.exit(0)

    presets_to_run = ASSET_PRESETS.items() if args.preset == "all" else [(args.preset, ASSET_PRESETS[args.preset])]
    for k, p in presets_to_run:
        generate_asset_higgsfield(k, p, api_key)

if __name__ == "__main__":
    main()
