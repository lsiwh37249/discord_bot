#!/bin/bash

# 1. 실행할 프로세스 시작 (예: some_command)
/usr/bin/python3 /home/kim/code/DiscordBot/discord_bot_back.py >> /home/kim/code/DiscordBot/crontab_test.log 

# 2. 방금 실행된 프로세스의 PID 저장
PID=$!

# 3. 필요한 만큼 대기 (예: 10분 후 종료)
sleep 60

# 4. 프로세스 종료
kill $PID
