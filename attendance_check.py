import os

import requests
import json
from datetime import datetime

SECRET_KEY = os.getenv("SECRET_KEY")
P1 = os.getenv("P1")

def fetch_attendance_data(P2: int, selected_date: str):
    """
     특정 회차의 선택한 날짜의 출석 데이터를 가져오는 함수
     :param P2: 회차 번호
     :param selected_date: 사용자가 선택한 날짜 (YYYYMMDD 형식)
     :return: 선택한 날짜의 출석 데이터 리스트
     """
    api_url = (
        f'https://hrd.work24.go.kr/jsp/HRDP/HRDPO00/HRDPOA60/HRDPOA60_4.jsp'
        f'?returnType=JSON&authKey={SECRET_KEY}&returnType=XML&outType=2'
        f'&srchTrprId={P1}&srchTrprDegr={P2}&outType=2&srchTorgId=student_detail'
        f'&atendMo={selected_date[:6]}'  # YYYYMM 형식으로 전달
    )

    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception(f"API 호출 실패: {response.status_code}")

    try:
        data = json.loads(response.json().get("returnJSON", "{}"))
        attendance_list = data.get("atabList", [])

        # ✅ 선택한 날짜 데이터만 필터링
        return [entry for entry in attendance_list if
                entry.get("atendDe") == selected_date and entry.get("atendSttusNm") != '중도탈락미출석']

    except json.JSONDecodeError as e:
        raise Exception(f"JSON 파싱 오류: {e}")