import os
import pandas as pd
from collections import defaultdict

def get_list_students_from_discord(guild):
    return [member for member in guild.members]

def get_list_match(discord_members, missing_checkout_names):
    missing_members = []
    print(f"missing_checkout_names: {missing_checkout_names}")

    if discord_members:
        for discord_member in discord_members:
            # 디스코드 멤버 이름을 사용하여 비교
            if any(name in discord_member.display_name for name in missing_checkout_names):
                missing_members.append(discord_member)

    return missing_members

def change_to_discord_response(missing_members):
    # 퇴실 체크 안한 사람들의 Discord 아이디 출력
    response = []
    for member in missing_members:
        response.append(f"<@{member.id}>")
    return response

def get_samename_list(dailyAttendence):
    # 이름 기준 정렬
    sorted_attendance = sorted(dailyAttendence, key=lambda x: x['cstmrNm'])

    # 이름별로 모으기
    name_groups = defaultdict(list)
    for person in sorted_attendance:
        name_groups[person['cstmrNm']].append(person)

    result = []
    for name, group in name_groups.items():
        if len(group) > 1:  # 동명이인인 경우
            # trneeCstmrId 기준 정렬
            group_sorted = sorted(group, key=lambda x: x['trneeCstmrId'])
            for i, person in enumerate(group_sorted):
                # 이름에 A, B 태그 붙이기
                tag = "A" if i == 0 else "B"
                new_person = person.copy()
                new_person['cstmrNm'] = f"{person['cstmrNm']} ({tag})"
                result.append(new_person)
        else:
            result.extend(group)
        return result


def get_list_no_checkout(dailyAttendence):
    missing_checkout_names = []
    for member in dailyAttendence:
        if member.get('lpsilTime', '') is not None and member.get('lpsilTime', '') != '0000' and member.get('levromTime', '') == '0000':
            name = member.get("cstmrNm")
            #동명이인에 포함되는 경우
            # member.get("trneeCstmrId")가 동명이인 리스트에 포함되어 있는 경우 이름을 다르게 변경하기

            missing_checkout_names.append(name)

    return missing_checkout_names


def save_api_debug_log(attendance_data, gisu, today_date):
    debug_dir = f"logs/{today_date}"
    os.makedirs(debug_dir, exist_ok=True)

    file_path = os.path.join(debug_dir, "api_debug_sorted.csv")

    # 새로운 데이터프레임 생성
    new_df = attendance_data
    new_df['gisu'] = gisu

    # 기존 파일이 있으면 불러오기
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    # 정렬 후 저장
    combined_df = combined_df.sort_values(by='levromTime')
    print(combined_df)
    combined_df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"[DEBUG] API 응답 저장 (합침): {file_path}")