import discord
from discord.ext import commands, tasks
from attendance_check import fetch_attendance_data
from datetime import datetime
import os
import attendance_function
import asyncio
import uvicorn
from fastapi import FastAPI

# FastAPI 앱 생성
app = FastAPI()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True  # 멤버 조회 활성화
intents.message_content = True  # 메시지 내용 읽기 활성화

bot = commands.Bot(command_prefix="!", intents=intents)

#봇이 들어 있는 서버 리스트
guild_list = []

@bot.event
async def on_ready():
    global guild_list
    print(f'✅ Logged in as {bot.user}')
    # 봇이 연결된 서버 목록 가져오기
    guild_list = [guild for guild in bot.guilds]  # 전체 서버 목록을 전역 변수로 저장
    for guild in guild_list:
        print(f"Connected to guild: {guild.name}, guild_id: {guild.id}")

# 디스코드에 출석하지 않은 사람들 리스트
async def not_yet_attendence(guild, P2, today_date):
    # 출석 데이터
    dailyAttendence = fetch_attendance_data(P2,today_date)

    # API에서 받은 데이터 중 퇴실 체크를 하지 않은 사람을 찾기
    list_no_checkout = attendance_function.get_list_no_checkout(dailyAttendence)

    # 디스코드 서버의 멤버 리스트를 가져오기
    students = attendance_function.get_list_students_from_discord(guild)

    # 퇴실 체크 안한 사람과 디스코드 멤버 매칭
    missing_members = attendance_function.get_list_match(students, list_no_checkout)

    #디스코드 형식에 맞게 변환
    discord_response = attendance_function.change_to_discord_response(missing_members)

    return discord_response

async def get_name_and_date(guild_name):
    P2 = guild_name.split("기")[0]
    today_date = datetime.today().strftime('%Y%m%d')
    return P2, today_date

@bot.command()
async def 퇴실체크(ctx):

    #guild_name = "12기_SK네트웍스 Family AI Camp"

    guild_name = ctx.guild.name  # 서버 이름 가져오기
    guild = ctx.guild

    P2, today_date = await get_name_and_date(guild_name)

    discord_response = await not_yet_attendence(guild, P2,today_date)
    #discord_response = ['<@343298573603045386>']

    if discord_response:
        await ctx.send(" ".join(discord_response) + " 퇴실 체크 하셔야 합니다!" )
    else:
        await ctx.send("모든 사람이 퇴실 체크를 완료했습니다.")

async def all_request_checkout(gisu, date):
    print(f"{gisu} 진입")

    P2, today_date= gisu, date
    dailyAttendence = fetch_attendance_data(P2,today_date)
    #print(dailyAttendence)
    missing_checkout_names = []
    for member in dailyAttendence:
        if member.get('lpsilTime', '') is not None and member.get('lpsilTime', '') != '0000' and member.get('levromTime', '') == '0000':
            name = member.get("cstmrNm")
            missing_checkout_names.append(name)
    print(missing_checkout_names)


# 최상위에서 실행
if __name__ == "__main__":
    date = '20250424'
    for gisu in range(7,14,1):
        asyncio.run(all_request_checkout(str(gisu), date))



