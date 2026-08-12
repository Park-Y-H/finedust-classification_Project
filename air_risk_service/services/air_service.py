from urllib.parse import unquote
import requests
import os


def get_seoul_temp_hub():
    auth_key = os.getenv("KMA_AUTH_KEY")
    url = f"https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php?stn=108&help=0&authKey={auth_key}"
    try:
        res = requests.get(url, timeout=5)
        lines = res.text.strip().split('\n')
        for line in lines:
            if line.startswith('#') or not line.strip(): continue
            parts = line.split()
            if len(parts) > 13:
                return float(parts[11]), float(parts[13])
    except:
        return -999.0, -999.0
    return -999.0, -999.0


def get_seoul_air_quality():
    auth_key = os.getenv("SEOUL_AIR_KEY")
    url = f"http://openapi.seoul.go.kr:8088/{auth_key}/json/RealtimeCityAir/1/25/"
    air_dict = {}
    time_info = {}  # 구별 개별 시각 저장용
    common_time = ""

    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if 'RealtimeCityAir' in data:
            rows = data['RealtimeCityAir']['row']
            common_time = rows[0].get('MSRMT_DT', "")  # 전체 기준 시간
            for item in rows:
                gu = item['MSRSTN_NM']
                # JSON 원본 키값에 맞게 수정
                pm10 = item.get('PM')
                pm25 = item.get('FPM')
                o3 = item.get('OZON')
                no2 = item.get('NTDX')
                so2 = item.get('SPDX')
                co = item.get('CBMX')

                msrmt_dt = item.get('MSRMT_DT', common_time)
                if pm10 is not None and pm25 is not None:
                    air_dict[gu] = {
                        'pm10': float(pm10) if pm10 else None,
                        'pm25': float(pm25) if pm25 else None,
                        'o3': float(o3) if o3 else None,  # 오존이 없어도 에러 안 남
                        'no2': float(no2) if no2 else None,
                        'so2': float(so2) if so2 else None,
                        'co': float(co) if co else None
                    }
                    time_info[gu] = msrmt_dt
        return air_dict, time_info, common_time
    except:
        return {}, {}, ""


def get_past_air_data(station_name):
    raw_key = os.getenv("PAST_AIR_KEY", "")
    auth_key = unquote(raw_key)
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"

    params = {
        'serviceKey': auth_key,
        'returnType': 'json',
        'numOfRows': '100',
        'pageNo': '1',
        'stationName': station_name,
        'dataTerm': 'MONTH',  # [수정] DAILY 대신 MONTH를 사용해야 3일 전 데이터가 안정적으로 옵니다.
        'ver': '1.0'
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        if "quota exceeded" in res.text.lower():
            # 쿼터 초과 시 에러를 내지 않고 조용히 None 반환 (캐시가 있으면 캐시를 쓰고, 없으면 점검중 표시)
            return [[None] * 3, [None] * 3]
        print(f"DEBUG [{station_name}]: {res.text[:50]}")
        data = res.json()
        items = data.get('response', {}).get('body', {}).get('items', [])

        if not items:
            return [[None] * 3, [None] * 3]

        def to_f(v):
            return float(v) if v and v not in ['-', 'None', 'null'] else None



        def find_available_past(target_idx):
            # 정해진 시점부터 최대 30시간 전(target_idx + 6)까지 탐색
            for offset in range(7):
                idx = target_idx + offset
                if 0 <= idx < len(items):
                    p10 = to_f(items[idx].get('pm10Value'))
                    p25 = to_f(items[idx].get('pm25Value'))
                    if p10 is not None and p25 is not None:
                        return p10, p25
            return None, None

        l1_10, l1_25 = find_available_past(23)
        l2_10, l2_25 = find_available_past(47)
        l3_10, l3_25 = find_available_past(71)

        # 리스트 형태 반환: [[PM25 과거 3,2,1], [PM10 과거 3,2,1]]
        return [[l3_25, l2_25, l1_25], [l3_10, l2_10, l1_10]]


    except Exception as e:
        print(f"기상청 데이터 에러: {e}")
        return -999.0, -999.0