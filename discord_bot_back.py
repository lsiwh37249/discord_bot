import discord
from discord.ext import commands, tasks
from attendance_check import fetch_attendance_data
from datetime import datetime
import os
import attendance_function
import asyncio
import uvicorn
from fastapi import FastAPI
import pandas as pd

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

    # 동명이인 데이터 처리
    print(dailyAttendence)

    # API에서 받은 데이터 중 퇴실 체크를 하지 않은 사람을 찾기
    list_no_checkout = attendance_function.get_list_no_checkout(dailyAttendence)

    df = pd.DataFrame(dailyAttendence)

    # 디스코드 서버의 멤버 리스트를 가져오기
    students = attendance_function.get_list_students_from_discord(guild)

    # 퇴실 체크 안한 사람과 디스코드 멤버 매칭
    missing_members = attendance_function.get_list_match(students, list_no_checkout)

    #디스코드 형식에 맞게 변환
    discord_response = attendance_function.change_to_discord_response(missing_members)

    new_df = df[df['cstmrNm'].isin(students)].copy()

    attendance_function.save_api_debug_log(new_df, P2, today_date)
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

    if discord_response:
        await ctx.send(" ".join(discord_response) + " 퇴실 체크 하셔야 합니다!" )
    else:
        await ctx.send("모든 사람이 퇴실 체크를 완료했습니다.")

# FastAPI & Discord 봇 동시에 실행
async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(TOKEN))  # Discord 봇 실행
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()  # FastAPI 실행

# 실행
if __name__ == "__main__":
    asyncio.run(main())
