import logging
from attendance_check import fetch_attendance_data
from attendance_function import get_list_no_checkout
import attendance_function
from datetime import datetime
import asyncio


async def get_name_and_date(gisu):
    P2 = gisu
    today_date = datetime.today().strftime('%Y%m%d')
    return P2, today_date

async def all_request_checkout(gisu):
    date = datetime.today().strftime('%Y%m%d')

    P2, today_date= gisu, date

    dailyAttendence = fetch_attendance_data(P2,today_date)

    print(dailyAttendence)

    list_no_checkout = get_list_no_checkout(dailyAttendence)

    logging.basicConfig(filename='logs/logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')

    logging.info(f"[INFO] {gisu}기 중 퇴실 체크하지 않은 사람 : {list_no_checkout}")

    print(f"[INFO] {gisu}기 중 퇴실 체크하지 않은 사람 : {list_no_checkout}")


# 최상위에서 실행
if __name__ == "__main__":
    for gisu in range(8,14,1):
        asyncio.run(all_request_checkout(str(gisu)))



