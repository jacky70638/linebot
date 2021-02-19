from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from liffpy import LineFrontendFramework as LIFF,ErrorResponse
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

from gamelinebot.models import *

from member_profile.models import *

from bs4 import BeautifulSoup
import requests,datetime,re,time,json

liff_api = LIFF(settings.LINE_CHANNEL_ACCESS_TOKEN)
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

group_id='Ca2a22d4362431873ccfa8b9281fdf878'#測試
#group_id='C4d7af172bc840963d55215d5706f5c46'
urll='https://c4af36a066d7.ngrok.io'

def liff(request):
    if request.method == 'POST':
        uid = request.POST["uid"]
        name = request.POST["name"]
        account = request.POST["account"]
        password = request.POST["password"]
        agent_number = request.POST["agent_number"]
        if Member_Info.objects.filter(uid=uid).exists()==False:#測試有沒有註冊
            Member_Info.objects.create(uid=uid,name=name,agent_number=agent_number)
            Bet.objects.create(uid=uid,name=name)
            Account_password.objects.create(uid=uid,name=name,account=account,password=password)
        else:
            Member_Info.objects.filter(uid=uid).update(status=11)#status=11(代表重複註冊)
    return render(request,'liff.html',locals())

def bet(request):#下注
    if request.method == 'POST':
        uid = request.POST["uid"]
        name = request.POST["name"]
        location = request.POST["location"]
        if Member_Info.objects.filter(uid=uid).exists()==True:#測試有沒有註冊
            gameonofff=Gameonoff.objects.last()
            gameonoff=gameonofff.turn#現在遊戲開關狀態
            bet_turn=gameonofff.bet_turn#現在遊戲下注開關狀態

            game_no=Game_no.objects.last()#現在遊戲局號
            game_no=game_no.nonow
            game_mdtss=time.strftime('%Y-%m-%d',time.localtime())
            game_mdtss=game_mdtss+'-'+game_no

            wallets=Member_Info.objects.filter(uid=uid)#現在錢包餘額
            for wallet in wallets:
                now_wallet=wallet.wallet

            proxyss=Member_Info.objects.filter(uid=uid)#代理名稱
            for proxys in proxyss:
                proxyss=proxys.agent_number

            water_walletss=Proxy.objects.filter(agent_number=proxyss)#現在水錢包餘額
            for water_walletsss in water_walletss:
                water_wallets=water_walletsss.water
                water_odds=water_walletsss.water_odds

            player_statuss=Member_Info.objects.filter(uid=uid)#玩家狀態
            for player_status in player_statuss:
                player_status=int(player_status.status)
                
            if gameonoff == "1":#遊戲狀態=1 才可以玩
                if Member_Info.objects.filter(uid=uid).exists()==True:#測試有沒有註冊
                    if player_status!=11:#測試玩家狀態
                        if player_status==1:#測試玩家狀態
                            if bet_turn == '1':#下注審核
                                bet=Bet.objects.filter(uid=uid)
                                for bets in bet:
                                    max_ab=bets.max_ab
                                    min_ab=bets.min_ab
                                    max_ss=bets.max_ss
                                    min_ss=bets.min_ss
                                    max_cd=bets.max_cd
                                    min_cd=bets.min_cd
                                try:
                                    bookmaker = request.POST["bookmaker"]
                                    if int(now_wallet) >= int(location):
                                        if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                            User_Info.objects.create(uid=uid,name=name,mtext='莊｜'+location,gameno=game_mdtss,bookmaker=location)
                                            now_wallet=int(now_wallet) - int(location)
                                            Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                            info='%s\n莊｜%s  🉐️'%(name,location)
                                            message=[]
                                            message.append(TextSendMessage(text=info))
                                            line_bot_api.push_message(group_id,message)
                                            waters=int(location)*water_odds
                                            water_wallets=float(water_wallets)+float(waters)
                                            Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                except:
                                    pass
                                try:
                                    player = request.POST["player"]
                                    if int(now_wallet) >= int(location):
                                        if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                            User_Info.objects.create(uid=uid,name=name,mtext='閒｜'+location,gameno=game_mdtss,player=location)
                                            now_wallet=int(now_wallet) - int(location)
                                            Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                            info='%s\n閒｜%s  🉐️'%(name,location)
                                            message=[]
                                            message.append(TextSendMessage(text=info))
                                            line_bot_api.push_message(group_id,message)
                                            waters=int(location)*water_odds
                                            water_wallets=float(water_wallets)+float(waters)
                                            Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                except:
                                    pass
                                try:
                                    bookmaker_r = request.POST["bookmaker_r"]
                                    if int(now_wallet) >= int(location):
                                        if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                            User_Info.objects.create(uid=uid,name=name,mtext='莊對｜'+location,gameno=game_mdtss,bookmaker_r=location)
                                            now_wallet=int(now_wallet) - int(location)
                                            Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                            info='%s\n莊對｜%s  🉐️'%(name,location)
                                            message=[]
                                            message.append(TextSendMessage(text=info))
                                            line_bot_api.push_message(group_id,message)
                                            waters=int(location)*water_odds
                                            water_wallets=float(water_wallets)+float(waters)
                                            Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                except:
                                    pass
                                try:
                                    player_r = request.POST["player_r"]
                                    if int(now_wallet) >= int(location):
                                        if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                            User_Info.objects.create(uid=uid,name=name,mtext='閒對｜'+location,gameno=game_mdtss,player_r=location)
                                            now_wallet=int(now_wallet) - int(location)
                                            Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                            info='%s\n閒對｜%s  🉐️'%(name,location)
                                            message=[]
                                            message.append(TextSendMessage(text=info))
                                            line_bot_api.push_message(group_id,message)
                                            waters=int(location)*water_odds
                                            water_wallets=float(water_wallets)+float(waters)
                                            Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                except:
                                    pass
                                try:
                                    combine = request.POST["combine"]
                                    if int(now_wallet) >= int(location):
                                        if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                            User_Info.objects.create(uid=uid,name=name,mtext='和｜'+location,gameno=game_mdtss,combine=location)
                                            now_wallet=int(now_wallet) - int(location)
                                            Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                            info='%s\n和｜%s  🉐️'%(name,location)
                                            message=[]
                                            message.append(TextSendMessage(text=info))
                                            line_bot_api.push_message(group_id,message)
                                            waters=int(location)*water_odds
                                            water_wallets=float(water_wallets)+float(waters)
                                            Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                except:
                                    pass
                                try:
                                    lucky_r = request.POST["lucky_r"]
                                    if int(now_wallet) >= int(location):
                                        if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                            User_Info.objects.create(uid=uid,name=name,mtext='幸運六｜'+location,gameno=game_mdtss,lucky_r=location)
                                            now_wallet=int(now_wallet) - int(location)
                                            Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                            info='%s\n幸運六｜%s  🉐️'%(name,location)
                                            message=[]
                                            message.append(TextSendMessage(text=info))
                                            line_bot_api.push_message(group_id,message)
                                            waters=int(location)*water_odds
                                            water_wallets=float(water_wallets)+float(waters)
                                            Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                except:
                                    pass
                                gameonofff=Gameonoff.objects.last()
                                bs=gameonofff.ef
                                if '大小藍' == bs:
                                    try:
                                        big_r = request.POST["big_r"]
                                        if int(now_wallet) >= int(location):
                                            if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                                User_Info.objects.create(uid=uid,name=name,mtext='大｜'+location,gameno=game_mdtss,big_r=location)
                                                now_wallet=int(now_wallet) - int(location)
                                                Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                                info='%s\n大｜%s  🉐️'%(name,location)
                                                message=[]
                                                message.append(TextSendMessage(text=info))
                                                line_bot_api.push_message(group_id,message)
                                                waters=int(location)*water_odds
                                                water_wallets=float(water_wallets)+float(waters)
                                                Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                            else:
                                                message=[]
                                                message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                                line_bot_api.push_message(group_id,message)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    except:
                                        pass
                                    try:
                                        small_r = request.POST["small_r"]
                                        if int(now_wallet) >= int(location):
                                            if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                                User_Info.objects.create(uid=uid,name=name,mtext='小｜'+location,gameno=game_mdtss,small_r=location)
                                                now_wallet=int(now_wallet) - int(location)
                                                Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                                info='%s\n小｜%s  🉐️'%(name,location)
                                                message=[]
                                                message.append(TextSendMessage(text=info))
                                                line_bot_api.push_message(group_id,message)
                                                waters=int(location)*water_odds
                                                water_wallets=float(water_wallets)+float(waters)
                                                Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                            else:
                                                message=[]
                                                message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                                line_bot_api.push_message(group_id,message)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    except:
                                        pass
                                try:
                                    SS = request.POST["SS"]
                                    if int(now_wallet) >= int(location):
                                        if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                            User_Info.objects.create(uid=uid,name=name,mtext='莊對｜'+location,gameno=game_mdtss,bookmaker_r=location)
                                            User_Info.objects.create(uid=uid,name=name,mtext='閒對｜'+location,gameno=game_mdtss,player_r=location)
                                            User_Info.objects.create(uid=uid,name=name,mtext='和｜'+location,gameno=game_mdtss,combine=location)
                                            User_Info.objects.create(uid=uid,name=name,mtext='幸運六｜'+location,gameno=game_mdtss,lucky_r=location)
                                            now_wallet=int(now_wallet) - int(location)*4
                                            Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                            info='%s\n四寶｜%s  🉐️'%(name,location)
                                            message=[]
                                            message.append(TextSendMessage(text=info))
                                            line_bot_api.push_message(group_id,message)
                                            waters=int(location)*water_odds*4
                                            water_wallets=float(water_wallets)+float(waters)
                                            Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                except:
                                    pass
                                try:
                                    S = request.POST["S"]
                                    if int(now_wallet) >= int(location):
                                        if int(min_ab) <= int(location) <= int(max_ab):#檢查限紅
                                            User_Info.objects.create(uid=uid,name=name,mtext='莊對｜'+location,gameno=game_mdtss,bookmaker_r=location)
                                            User_Info.objects.create(uid=uid,name=name,mtext='閒對｜'+location,gameno=game_mdtss,player_r=location)
                                            User_Info.objects.create(uid=uid,name=name,mtext='和｜'+location,gameno=game_mdtss,combine=location)
                                            now_wallet=int(now_wallet) - int(location)*3
                                            Member_Info.objects.filter(uid=uid).update(wallet=now_wallet)
                                            info='%s\n三寶｜%s  🉐️'%(name,location)
                                            message=[]
                                            message.append(TextSendMessage(text=info))
                                            line_bot_api.push_message(group_id,message)
                                            waters=int(location)*water_odds*3
                                            water_wallets=float(water_wallets)+float(waters)
                                            Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                        else:
                                            message=[]
                                            message.append(TextSendMessage(text='[%s] 請符合下注限紅'%(name)))
                                            line_bot_api.push_message(group_id,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                except:
                                    pass
                        else:
                            message=[]
                            message.append(TextSendMessage(text='[%s] 已取消會員\n請找代理恢復會員'%(name)))
                            line_bot_api.push_message(group_id,message)
                    else:
                        message=[]
                        message.append(TextSendMessage(text='[%s] 重複註冊會員\n請找代理恢復會員'%(name)))
                        line_bot_api.push_message(group_id,message)
                else:
                    message=[]
                    message.append(TextSendMessage(text='[%s] 請先進行註冊'%(name)))
                    line_bot_api.push_message(group_id,message)
        else:
            message=[]
            message.append(TextSendMessage(text='[%s] 請先進行註冊'%(name)))
            line_bot_api.push_message(group_id,message)
    return render(request,'bet.html',locals())
@csrf_exempt
def win1(request):
    game_no=Game_no.objects.last()#現在遊戲局號
    game_no=game_no.nonow
    game_mdtss=time.strftime('%Y-%m-%d',time.localtime())
    game_mdtss=game_mdtss+'-'+game_no
    s = request.POST["key1"]
    key = request.POST["key2"]
    if '大小藍' == key:
        Gameonoff.objects.filter(turn=1).update(ef='大小藍')
        message=[]
        message.append(TextSendMessage(text='▂▂▂▂開始下注▂▂▂▂\n局號｜  %s\n\n---------倒數%s秒---------\n下注單以機器人收單為準'%(game_mdtss,s)))
        line_bot_api.push_message(group_id,message)
        message=[]
        message = ImagemapSendMessage(
            base_url='https://baida.ddns.net/static/img/ABC.jpg?',
            alt_text='組圖訊息',
            base_size=BaseSize(height=297, width=828),
            actions=[
                URIImagemapAction(
                    link_uri='https://liff.line.me/1655245083-EgMJxdaV',#下注網址
                    area=ImagemapArea(
                        x=0, y=0, width=828, height=297))])
        line_bot_api.push_message(group_id,message)
    else:
        Gameonoff.objects.filter(turn=1).update(ef='大小黑')
        message=[]
        message.append(TextSendMessage(text='▂▂▂▂開始下注▂▂▂▂\n局號｜  %s\n30局后不能投注 大 小 \n---------倒數%s秒---------\n下注單以機器人收單為準'%(game_mdtss,s)))
        line_bot_api.push_message(group_id,message)
        message=[]
        message = ImagemapSendMessage(
            base_url='https://baida.ddns.net/static/img/ABC.jpg?',
            alt_text='組圖訊息',
            base_size=BaseSize(height=297, width=828),
            actions=[
                URIImagemapAction(
                    link_uri='https://liff.line.me/1655245083-EgMJxdaV',
                    area=ImagemapArea(
                        x=0, y=0, width=828, height=297))])
        line_bot_api.push_message(group_id,message)
    Gameonoff.objects.filter(turn=1).update(bet_turn=1)#開啟下注動作
    return HttpResponse()

@csrf_exempt
def win2(request):
    game_no=Game_no.objects.last()#現在遊戲局號
    game_no=game_no.nonow
    game_mdtss=time.strftime('%Y-%m-%d',time.localtime())
    game_mdtss=game_mdtss+'-'+game_no
    datas = User_Info.objects.filter(gameno=game_mdtss)#叫出本局資料
    message=[]#玩家 
    for data in datas:
        info = '[ %s ]  %s'%(data.name,data.mtext)
        message.append(info)
    lenn=len(message)#押注
    Game_result.objects.create(gameno_result=game_mdtss,lenn=lenn)
    message = ','.join(message)
    info=message.replace(",","\n")
    bookmaker=0#莊家
    for data in datas:
        info1 = '%s'%(data.bookmaker)
        if info1 != '':
            bookmaker+=int(info1)
    player=0#閒家
    for data in datas:
        info2 = '%s'%(data.player)
        if info2 != '':
            player+=int(info2)
    combine = 0#和
    for data in datas:
        info3 = '%s'%(data.combine)
        if info3 != '':
            combine+=int(info3)
    bookmaker_r = 0#莊對
    for data in datas:
        info4 = '%s'%(data.bookmaker_r)
        if info4 != '':
            bookmaker_r+=int(info4)
    player_r = 0#閒對
    for data in datas:
        info5 = '%s'%(data.player_r)
        if info5 != '':
            player_r+=int(info5)
    big_r = 0#大
    for data in datas:
        info6 = '%s'%(data.big_r)
        if info6 != '':
            big_r+=int(info6)
    small_r = 0#小
    for data in datas:
        info7 = '%s'%(data.small_r)
        if info7 != '':
            small_r+=int(info7)
    lucky_r = 0#幸運六
    for data in datas:
        info8 = '%s'%(data.lucky_r)
        if info8 != '':
            lucky_r+=int(info8)
    summ = bookmaker+player+combine+bookmaker_r+player_r+big_r+small_r+lucky_r#總和
    Gameonoff.objects.filter(turn=1).update(bet_turn=0)#關閉下注動作
    message=[]
    message.append(TextSendMessage(text='停止下注\n收單統計'))
    message.append(TextSendMessage(text='''▂▂▂牌局資訊▂▂▂\n局號｜  %s\n▂▂▂下注有效玩家▂▂▂\n%s\n▂▂▂下注總表▂▂▂\n莊｜  %s\n閒｜  %s\n和｜  %s\n莊對｜  %s\n閒對｜  %s\n大｜  %s\n小｜  %s\n幸運六｜  %s\n\n押注｜  %s\n押注總和｜  %s\n'''%(game_mdtss,info,bookmaker,player,combine,bookmaker_r,player_r,big_r,small_r,lucky_r,lenn,summ)))
    line_bot_api.push_message(group_id,message)
    return HttpResponse()

@csrf_exempt
def win3(request):
    game_no=Game_no.objects.last()#現在遊戲局號
    game_no=game_no.nonow
    game_mdtss=time.strftime('%Y-%m-%d',time.localtime())
    game_mdtss=game_mdtss+'-'+game_no

    data = {'key':game_mdtss}
    url='%s/win_game2/'%(urll)
    linux_post=requests.post(url,data=data)

    bookmaker_odds = 0.95#遊戲規則賠率
    player_odds = 1
    combine_odds = 8
    bookmaker_r_odds = 11
    player_r_odds = 11
    lucky_r_odds = 6
    big_r_odds = 0.5
    small_r_odds = 1.5

    b_result = request.POST["key1"]
    p_result = request.POST["key2"]
    strr= request.POST["key3"]
    strrr=strr.split()
    Game_result.objects.filter(gameno_result=game_mdtss).update(game_bookmaker=b_result,game_player=p_result,result_game=strr)
    if '莊' in strrr:
        game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(bookmaker='')#查看本局下註記綠
        for game_result in game_results:
            game_result_uid=game_result.uid#uid
            game_result_bookmaker=game_result.bookmaker
            calculation = int(game_result_bookmaker)*bookmaker_odds#計算賠率後的輸贏結果
            balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
            for balance_check_result in balance_checks_result:
                info = balance_check_result.wallet
                wallet_results=info+calculation+int(game_result_bookmaker)
            Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
    if '閒' in strrr:
        game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(player='')#查看本局下註記綠
        for game_result in game_results:
            game_result_uid=game_result.uid#uid
            game_result_player=game_result.player
            calculation = int(game_result_player)*player_odds#計算賠率後的輸贏結果
            balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
            for balance_check_result in balance_checks_result:
                info = balance_check_result.wallet
                wallet_results=info+calculation+int(game_result_player)
            Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
    if '和' in strrr:
        game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(combine='')#查看本局下註記綠
        for game_result in game_results:
            game_result_uid=game_result.uid#uid
            game_result_combine=game_result.combine
            calculation = int(game_result_combine)*combine_odds#計算賠率後的輸贏結果
            balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
            for balance_check_result in balance_checks_result:
                info = balance_check_result.wallet
                wallet_results=info+calculation+int(game_result_combine)
            Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
    if '莊對' in strrr:
        game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(bookmaker_r='')#查看本局下註記綠
        for game_result in game_results:
            game_result_uid=game_result.uid#uid
            game_result_bookmaker_r=game_result.bookmaker_r
            calculation = int(game_result_bookmaker_r)*bookmaker_r_odds#計算賠率後的輸贏結果
            balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
            for balance_check_result in balance_checks_result:
                info = balance_check_result.wallet
                wallet_results=info+calculation+int(game_result_bookmaker_r)
            Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
    if '閒對' in strrr:
        game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(player_r='')#查看本局下註記綠
        for game_result in game_results:
            game_result_uid=game_result.uid#uid
            game_result_player_r=game_result.player_r
            calculation = int(game_result_player_r)*player_r_odds#計算賠率後的輸贏結果
            balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
            for balance_check_result in balance_checks_result:
                info = balance_check_result.wallet
                wallet_results=info+calculation+int(game_result_player_r)
            Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
    if '大' in strrr:
        game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(big_r='')#查看本局下註記綠
        for game_result in game_results:
            game_result_uid=game_result.uid#uid
            game_result_big_r=game_result.big_r
            calculation = int(game_result_big_r)*big_r_odds#計算賠率後的輸贏結果
            balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
            for balance_check_result in balance_checks_result:
                info = balance_check_result.wallet
                wallet_results=info+calculation+int(game_result_big_r)
            Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
    if '小' in strrr:
        game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(small_r='')#查看本局下註記綠
        for game_result in game_results:
            game_result_uid=game_result.uid#uid
            game_result_small_r=game_result.small_r
            calculation = int(game_result_small_r)*small_r_odds#計算賠率後的輸贏結果
            balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
            for balance_check_result in balance_checks_result:
                info = balance_check_result.wallet
                wallet_results=info+calculation+int(game_result_small_r)
            Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
    if '幸運六' in strrr:
        game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(lucky_r='')#查看本局下註記綠
        for game_result in game_results:
            game_result_uid=game_result.uid#uid
            game_result_lucky_r=game_result.lucky_r
            calculation = int(game_result_lucky_r)*lucky_r_odds#計算賠率後的輸贏結果
            balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
            for balance_check_result in balance_checks_result:
                info = balance_check_result.wallet
                wallet_results=info+calculation+int(game_result_lucky_r)
            Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包

    datas = User_Info.objects.filter(gameno=game_mdtss)#叫出本局資料
    total_win_lose=0
    messages=[]
    for data in datas:
        mtextc = re.sub(u"([^\u4e00-\u9fa5])","",data.mtext)
        mtexte = re.sub(u"([^\u0041-\u005a])","",data.mtext)
        mtextt = re.sub(u"([^\u0030-\u0039])","",data.mtext)
        if mtextc == '莊' and '莊' in strrr:
            mtextt=int(mtextt)*(bookmaker_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtextc,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtexte == 'A' and '莊' in strrr:
            mtextt=int(mtextt)*(bookmaker_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtextc == '閒' and '閒' in strrr:
            open_result='[ %s ]  %s｜+%s'%(data.name,mtextc,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtexte == 'B' and '閒' in strrr:
            open_result='[ %s ]  %s｜+%s'%(data.name,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtextc == '和' and '和' in strrr:
            mtextt=int(mtextt)*(combine_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtextc,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtexte == 'H' and '和' in strrr:
            mtextt=int(mtextt)*(combine_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtextc == '莊對' and '莊對' in strrr:
            mtextt=int(mtextt)*(bookmaker_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtextc,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtexte == 'AD' and '莊對' in strrr:
            mtextt=int(mtextt)*(bookmaker_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtextc == '閒對' and '閒對' in strrr:
            mtextt=int(mtextt)*(player_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtextc,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtexte == 'BD' and '閒對' in strrr:
            mtextt=int(mtextt)*(player_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtextc == '大' and '大' in strrr:
            mtextt=int(mtextt)*(big_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtextc,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtexte == 'E' and '大' in strrr:
            mtextt=int(mtextt)*(big_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtextc == '小' and '小' in strrr:
            mtextt=int(mtextt)*(small_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtextc,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtexte == 'F' and '小' in strrr:
            mtextt=int(mtextt)*(small_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtextc == '幸運六' and '幸運六' in strrr:
            mtextt=int(mtextt)*(lucky_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtextc,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        elif mtexte == 'L' and '幸運六' in strrr:
            mtextt=int(mtextt)*(lucky_r_odds)
            mtextt=int(mtextt)
            open_result='[ %s ]  %s｜+%s'%(data.name,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose+=int(mtextt)
        else:
            open_result='[ %s ]  %s%s｜-%s'%(data.name,mtextc,mtexte,mtextt)
            messages.append(open_result)
            total_win_lose-=int(mtextt)
    messages = ','.join(messages)
    info=messages.replace(",","\n")

    datas = Game_result.objects.filter(gameno_result=game_mdtss)#叫出本局資料(押注)
    lenns=[]#玩家 
    for data in datas:
        info1 = data.lenn
        lenns.append(info1)
    lenns = ','.join(lenns)

    message=[]
    message.append(TextSendMessage(text='''▂▂▂開牌結果▂▂▂\n局號｜%s\n勝  %s\n▂▂▂開獎輸贏▂▂▂\n%s\n▂▂▂輸贏總表▂▂▂\n押注｜%s\n總輸贏｜%s\n'''%(game_mdtss,strr,info,lenns,total_win_lose)))
    line_bot_api.push_message(group_id,message)
    message=[]
    o_c_url='%s/static/img/game_result/123/%s.jpg'%(urll,game_mdtss)
    message = ImageSendMessage(original_content_url=o_c_url, preview_image_url=o_c_url)
    line_bot_api.push_message(group_id,message)
    game_no=int(game_no)+1#局數+1
    Game_no.objects.create(nonow=game_no)

    gameonofff=Gameonoff.objects.last()
    gameonoff=gameonofff.turn#現在遊戲開關狀態
    data = {'key1':gameonoff,'key2':game_mdtss}
    url='%s/win_game3/'%(urll)
    linux_post=requests.post(url,data=data)
    return HttpResponse()

@csrf_exempt
def win4(request):  
    gameonoff = request.POST["key1"]
    red_img = request.POST["key2"]
    if '紅牌' not in red_img:
        print('沒紅牌')
        if gameonoff == "1":#遊戲狀態=1 才可以玩
            win5(request)
        else:
            message=[]
            message.append(TextSendMessage(text='今日遊戲結束\n謝謝各位'))
            line_bot_api.push_message(group_id,message)
    else:
        print('紅牌')
        message=[]
        message.append(TextSendMessage(text='遊戲洗牌中\n請各位休息稍等\n'))
        line_bot_api.push_message(group_id,message)
        time.sleep(200)#等待下一局#3:33
        message.append(TextSendMessage(text='遊戲即將開始\n請各位選手準備\n'))
        line_bot_api.push_message(group_id,message)
        win5(request)
    return HttpResponse()

@csrf_exempt
def win5(request): 
    game_no=Game_no.objects.last()#現在遊戲局號
    game_no=game_no.nonow
    game_mdtss=time.strftime('%Y-%m-%d',time.localtime())
    game_mdtss=game_mdtss+'-'+game_no
    data = {'key':game_mdtss}
    url='%s/win_game/'%(urll)
    linux_post=requests.post(url,data=data)
    return HttpResponse()

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']#驗證是否來自賴平台
        body = request.body.decode('utf-8')#這個是LINEBOT收到的JSON格式訊息
        try:#驗證你的request是不是真的來自LINE平台
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()  
#▼定義區▼----------------------------------------------------------------------------------------------------          
        for event in events:#自動回復一樣訊息
            if isinstance(event, MessageEvent):
                mtext=event.message.text#自己賴打的文字
                uid=event.source.user_id
                user_id=uid
                profile=line_bot_api.get_profile(uid)
                name=profile.display_name#profile是LINE的API指令
#-----------------------------------------------------------------------------------------------------------
                game_no=Game_no.objects.last()#現在遊戲局號
                game_no=game_no.nonow
                game_mdtss=time.strftime('%Y-%m-%d',time.localtime())
                game_mdtss=game_mdtss+'-'+game_no
#-----------------------------------------------------------------------------------------------------------
                gameonofff=Gameonoff.objects.last()
                gameonoff=gameonofff.turn#現在遊戲開關狀態
                bet_turn=gameonofff.bet_turn#現在遊戲下注開關狀態
#-----------------------------------------------------------------------------------------------------------
                wallets=Member_Info.objects.filter(uid=uid)#現在錢包餘額
                for wallet in wallets:
                    now_wallet=wallet.wallet
#-----------------------------------------------------------------------------------------------------------
                bet_records=User_Info.objects.filter(uid=uid).order_by('-mdt')[:20]#玩家下注紀錄
#-----------------------------------------------------------------------------------------------------------
                balance_checks=Member_Info.objects.filter(uid=uid)#玩家餘額查詢
#-----------------------------------------------------------------------------------------------------------
                player_statuss=Member_Info.objects.filter(uid=uid)#玩家狀態
                for player_status in player_statuss:
                    player_status=int(player_status.status)
#-----------------------------------------------------------------------------------------------------------
                proxyss=Member_Info.objects.filter(uid=uid)#代理名稱
                for proxys in proxyss:
                    proxyss=proxys.agent_number
#-----------------------------------------------------------------------------------------------------------
                water_walletss=Proxy.objects.filter(agent_number=proxyss)#現在水錢包餘額
                for water_wallets in water_walletss:
                    water_wallets=water_wallets.water
#▼個人區遊戲定義區▼-------------------------------------------------------------------------------------------
                if event.source.type=='user':#個人區
                    if Member_Info.objects.filter(uid=uid).exists()==True:#測試有沒有註冊
#-----------------------------------------------------------------------------------------------------------
                        if mtext == '取消會員':#玩家取消會員
                            Member_Info.objects.filter(uid=uid).update(status='0')
                            message=[]
                            message.append(TextSendMessage(text='------已取消會員------\n\n如要恢復會員，請洽代理\nLine ID：tata19970830'))
                            line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        elif mtext == '進行儲值':#玩家進行儲值
                            message=[]
                            message.append(TextSendMessage(text='如要進行儲值，請洽代理\nLine ID：tata19970830'))
                            line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        elif mtext == '餘額查詢':#玩家餘額查詢
                            infos=[]
                            for balance_check in balance_checks:
                                info = '[ %s ]  %s 元'%(balance_check.name,balance_check.wallet)
                                infos.append(info)
                            infos=','.join(infos)
                            infos=infos.replace(",","\n\n")
                            message=[]
                            message.append(TextSendMessage(text=infos))
                            line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        elif mtext == '下注紀錄':#玩家下注紀錄
                            infos=[]
                            for bet_record in bet_records:
                                info = '[ %s ]  第%s局  %s\n%s'%(bet_record.name,bet_record.gameno,bet_record.mtext,bet_record.mdt.strftime('%Y-%m-%d  %H:%M:%S'))# %H:%M:%S
                                infos.append(info)
                            infos=','.join(infos)
                            infos=infos.replace(",","\n\n")
                            message=[]
                            message.append(TextSendMessage(text=infos))
                            line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        elif mtext == '使用說明':#遊戲使用說明
                            if Root.objects.filter(uid=uid).exists()==False:
                                info='遊戲使用說明\n---------------------------\n1.先到綁定區進行綁定會員\n\n2.找代理進行儲值\n'
                                message=[]
                                message.append(TextSendMessage(text=info))
                                line_bot_api.reply_message(event.reply_token,message)
                            elif Root.objects.filter(uid=uid).exists()==True:
                                info='1.查詢現在注碼\n[Line名字/現在注碼]\n\n2.調整注碼\n[Line名字/莊閒最高/xxxxxx]\n[Line名字/莊閒最低/xxxxxx]\n[Line名字/四寶最高/xxxxxx]\n[Line名字/四寶最低/xxxxxx]\n[Line名字/大小最高/xxxxxx]\n[Line名字/大小最低/xxxxxx]\n\n3.遊戲開關\n開啟遊戲  [1]\n遊戲維修  [2]\n關閉遊戲  [0]\n關閉的時機\n要在本局結果後圖片顯示出來才可以下指令0\n'
                                message=[]
                                message.append(TextSendMessage(text=info))
                                line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                    else:
                        message=[]
                        message.append(TextSendMessage(text='請先進行註冊'))
                        line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                    if Root.objects.filter(uid=uid).exists()==True:#驗證權限
#-----------------------------------------------------------------------------------------------------------
                        '''
                        if 'https://' in mtext:
                            try:
                                liff_id = liff_api.add(
                                    view_type="full",
                                    view_url=mtext)
                                #1607718325-5QmeBQop=google首頁
                                message=[]
                                message.append(TextSendMessage(text='https://liff.line.me/'+liff_id))
                                line_bot_api.reply_message(event.reply_token,message)
                            except:
                                print(err.message)
                        '''
#-----------------------------------------------------------------------------------------------------------
                        if '現在注碼' in mtext:#控制注碼
                            mt=mtext.split('/',2)
                            bet=Bet.objects.filter(name=mt[0])#現在注碼
                            for bets in bet:
                                max_ab=bets.max_ab
                                min_ab=bets.min_ab
                                max_ss=bets.max_ss
                                min_ss=bets.min_ss
                                max_cd=bets.max_cd
                                min_cd=bets.min_cd
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ] 現在注碼\n\n莊 / 閒 限紅\n%s -至- %s\n\n莊對 / 閒對 / 和局 / 幸運六 限紅\n%s -至- %s\n\n大 / 小 限紅\n%s -至- %s'''%(mt[0],min_ab,max_ab,min_ss,max_ss,min_cd,max_cd)))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        elif '莊閒最高' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(max_ab=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        elif '莊閒最低' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(min_ab=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        elif '四寶最高' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(max_ss=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        elif '四寶最低' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(min_ss=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        elif '大小最高' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(max_cd=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        elif '大小最低' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(min_cd=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        elif '1' == mtext:#開啟遊戲
                            Gameonoff.objects.all().delete()#控制遊戲開關
                            Gameonoff.objects.create(turn=mtext)
                            message=[]
                            message.append(TextSendMessage(text='現在是遊戲時間'))
                            line_bot_api.reply_message(event.reply_token,message)
                        elif '2' == mtext:#遊戲維修
                            Gameonoff.objects.all().delete()
                            Gameonoff.objects.create(turn=mtext)
                            message=[]
                            message.append(TextSendMessage(text='現在是維修時間'))
                            line_bot_api.reply_message(event.reply_token,message)
                        elif '0' == mtext:#關閉遊戲
                            Gameonoff.objects.all().delete()
                            Gameonoff.objects.create(turn=mtext)
                            message=[]
                            message.append(TextSendMessage(text='現在不是遊戲時間'))
                            line_bot_api.reply_message(event.reply_token,message)
#▼群組區▼----------------------------------------------------------------------------------------------------
                else:#群組區
                    group_id=event.source.group_id
                    #print(group_id)
                    if event.source.type=='group':#user、room、group 個人、聊天室、群組
                        if gameonoff == "1":#遊戲狀態=1 才可以玩
                            if Member_Info.objects.filter(uid=uid).exists()==True:#測試有沒有註冊
                                if player_status!=11:#測試玩家狀態
                                    if player_status==1:#測試玩家狀態
                                        if '遊戲開始' == mtext and Root.objects.filter(uid=uid).exists()==True:
                                            data = {'key':game_mdtss}
                                            url='%s/win_game/'%(urll)
                                            linux_post=requests.post(url,data=data)
                                            
                                        if bet_turn == '1':#下注審核
                                            bet=Bet.objects.filter(uid=uid)
                                            water_odds=0.004
                                            for bets in bet:
                                                max_ab=bets.max_ab
                                                min_ab=bets.min_ab
                                                max_ss=bets.max_ss
                                                min_ss=bets.min_ss
                                                max_cd=bets.max_cd
                                                min_cd=bets.min_cd
                                            if '莊' in mtext or 'A' in mtext:
                                                if '對' not in mtext and 'D' not in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_ab) <= int(mtextt) <= int(max_ab):#檢查限紅
                                                            if mtextc != '':
                                                                if mtextc != '莊':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,bookmaker=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                            if mtexte != '':
                                                                if mtexte != 'A':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,bookmaker=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.push_message(group_id,message)
                                            if '閒' in mtext or 'B' in mtext:
                                                if '對' not in mtext and 'D' not in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_ab) <= int(mtextt) <= int(max_ab): 
                                                            if mtextc != '':
                                                                if mtextc != '閒':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,player=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                            if mtexte != '':
                                                                if mtexte != 'B':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,player=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.push_message(group_id,message)
                                            if '和' in mtext or 'H' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt) <= int(max_ss): 
                                                            if mtextc != '':
                                                                if mtextc != '和':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                            if mtexte != '':
                                                                if mtexte != 'H':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.push_message(group_id,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.push_message(group_id,message)
                                            if '莊對' in mtext or 'AD' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt) <= int(max_ss): 
                                                            if mtextc != '':
                                                                if mtextc != '莊對':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                            if mtexte != '':
                                                                if mtexte != 'AD':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.push_message(group_id,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.push_message(group_id,message)
                                            if '閒對' in mtext or 'BD' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt) <= int(max_ss): 
                                                            if mtextc != '':
                                                                if mtextc != '閒對':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                            if mtexte != '':
                                                                if mtexte != 'BD':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.push_message(group_id,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.push_message(group_id,message)

                                            gameonofff=Gameonoff.objects.last()
                                            bs=gameonofff.ef
                                            if '大小藍' == bs:
                                                if '大' in mtext or 'E' in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_cd) <= int(mtextt) <= int(max_cd): 
                                                                if mtextc != '':
                                                                    if mtextc != '大':
                                                                        message=[]
                                                                        message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                        line_bot_api.push_message(group_id,message)
                                                                    else:
                                                                        User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,big_r=mtextt)
                                                                        Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                        info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                        message=[]
                                                                        message.append(TextSendMessage(text=info))
                                                                        line_bot_api.push_message(group_id,message)
                                                                        waters=int(mtextt)*water_odds
                                                                        water_wallets=float(water_wallets)+float(waters)
                                                                        Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                                if mtexte != '':
                                                                    if mtexte != 'E':
                                                                        message=[]
                                                                        message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                        line_bot_api.push_message(group_id,message)
                                                                    else:
                                                                        User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,big_r=mtextt)
                                                                        Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                        info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                        message=[]
                                                                        message.append(TextSendMessage(text=info))
                                                                        line_bot_api.push_message(group_id,message)
                                                                        waters=int(mtextt)*water_odds
                                                                        water_wallets=float(water_wallets)+float(waters)
                                                                        Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.push_message(group_id,message)
                                                elif '小' in mtext or 'F' in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_cd) <= int(mtextt) <= int(max_cd): 
                                                                if mtextc != '':
                                                                    if mtextc != '小':
                                                                        message=[]
                                                                        message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                        line_bot_api.push_message(group_id,message)
                                                                    else:
                                                                        User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,small_r=mtextt)
                                                                        Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                        info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                        message=[]
                                                                        message.append(TextSendMessage(text=info))
                                                                        line_bot_api.push_message(group_id,message)
                                                                        waters=int(mtextt)*water_odds
                                                                        water_wallets=float(water_wallets)+float(waters)
                                                                        Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                                if mtexte != '':
                                                                    if mtexte != 'F':
                                                                        message=[]
                                                                        message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                        line_bot_api.push_message(group_id,message)
                                                                    else:
                                                                        User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,small_r=mtextt)
                                                                        Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                        info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                        message=[]
                                                                        message.append(TextSendMessage(text=info))
                                                                        line_bot_api.push_message(group_id,message)
                                                                        waters=int(mtextt)*water_odds
                                                                        water_wallets=float(water_wallets)+float(waters)
                                                                        Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.push_message(group_id,message)
                                            if '幸運六' in mtext or 'L' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt) <= int(max_ss): 
                                                            if mtextc != '':
                                                                if mtextc != '幸運六':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,lucky_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                            if mtexte != '':
                                                                if mtexte != 'L':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,lucky_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    waters=int(mtextt)*water_odds
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.push_message(group_id,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.push_message(group_id,message)
                                            if '三寶' in mtext or 'S' in mtext:
                                                if 'SS' not in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_ss) <= int(mtextt)*3 <= int(max_ss):#檢查限紅
                                                            if mtextc != '':
                                                                if mtextc != '三寶':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='莊對'+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='閒對'+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='和'+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt)*3)
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.reply_message(event.reply_token,message)
                                                                    waters=int(mtextt)*water_odds*3
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                            if mtexte != '':
                                                                if mtexte != 'S':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='莊對'+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='閒對'+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='和'+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt)*3)
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.reply_message(event.reply_token,message)
                                                                    waters=int(mtextt)*water_odds*3
                                                                    water_wallets=float(water_wallets)+float(waters)
                                                                    Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.reply_message(event.reply_token,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.reply_message(event.reply_token,message)
                                            if '四寶' in mtext or 'SS' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt)*3 <= int(max_ss):#檢查限紅
                                                        if mtextc != '':
                                                            if mtextc != '四寶':
                                                                message=[]
                                                                message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                line_bot_api.push_message(group_id,message)
                                                            else:
                                                                User_Info.objects.create(uid=uid,name=name,mtext='莊對'+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='閒對'+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='和'+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='幸運六'+'｜'+mtextt,gameno=game_mdtss,lucky_r=mtextt)
                                                                Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt)*4)
                                                                info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                message=[]
                                                                message.append(TextSendMessage(text=info))
                                                                line_bot_api.reply_message(event.reply_token,message)
                                                                waters=int(mtextt)*water_odds*4
                                                                water_wallets=float(water_wallets)+float(waters)
                                                                Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                        if mtexte != '':
                                                            if mtexte != 'SS':
                                                                message=[]
                                                                message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                line_bot_api.push_message(group_id,message)
                                                            else:
                                                                User_Info.objects.create(uid=uid,name=name,mtext='莊對'+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='閒對'+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='和'+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='幸運六'+'｜'+mtextt,gameno=game_mdtss,lucky_r=mtextt)
                                                                Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt)*4)
                                                                info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                message=[]
                                                                message.append(TextSendMessage(text=info))
                                                                line_bot_api.reply_message(event.reply_token,message)
                                                                waters=int(mtextt)*water_odds*4
                                                                water_wallets=float(water_wallets)+float(waters)
                                                                Proxy.objects.filter(agent_number=proxyss).update(water=water_wallets)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.reply_message(event.reply_token,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.reply_message(event.reply_token,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='[%s] 已取消會員\n請找代理恢復會員'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                else:
                                    message=[]
                                    message.append(TextSendMessage(text='[%s] 重複註冊會員\n請找代理恢復會員'%(name)))
                                    line_bot_api.push_message(group_id,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='[%s] 請先進行註冊'%(name)))
                                line_bot_api.push_message(group_id,message)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()





@csrf_exempt
def callback1(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']#驗證是否來自賴平台
        body = request.body.decode('utf-8')#這個是LINEBOT收到的JSON格式訊息
        try:#驗證你的request是不是真的來自LINE平台
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()  
#▼定義區▼----------------------------------------------------------------------------------------------------          
        for event in events:#自動回復一樣訊息
            if isinstance(event, MessageEvent):
                mtext=event.message.text#自己賴打的文字
                uid=event.source.user_id
                user_id=uid
                profile=line_bot_api.get_profile(uid)
                name=profile.display_name#profile是LINE的API指令
#-----------------------------------------------------------------------------------------------------------
                game_no=Game_no.objects.last()#現在遊戲局號
                game_no=game_no.nonow
                game_mdtss=time.strftime('%Y-%m-%d',time.localtime())
                game_mdtss=game_mdtss+'-'+game_no
                img_no=game_mdtss
#-----------------------------------------------------------------------------------------------------------
                gameonofff=Gameonoff.objects.last()
                gameonoff=gameonofff.turn#現在遊戲開關狀態
                bet_turn=gameonofff.bet_turn#現在遊戲下注開關狀態
#-----------------------------------------------------------------------------------------------------------
                wallets=Member_Info.objects.filter(uid=uid)#現在錢包餘額
                for wallet in wallets:
                    now_wallet=wallet.wallet
#-----------------------------------------------------------------------------------------------------------
                bet_records=User_Info.objects.filter(uid=uid).order_by('-mdt')[:20]#玩家下注紀錄
#-----------------------------------------------------------------------------------------------------------
                balance_checks=Member_Info.objects.filter(uid=uid)#玩家餘額查詢
#-----------------------------------------------------------------------------------------------------------
                player_statuss=Member_Info.objects.filter(uid=uid)#玩家狀態
                for player_status in player_statuss:
                    player_status=int(player_status.status)
#-----------------------------------------------------------------------------------------------------------
                bookmaker_odds = 0.95#遊戲規則賠率
                player_odds = 1
                combine_odds = 8
                bookmaker_r_odds = 11
                player_r_odds = 11
                lucky_r_odds = 6
                big_r_odds = 0.5
                small_r_odds = 1.5
#-----------------------------------------------------------------------------------------------------------
#▼個人區遊戲定義區▼-------------------------------------------------------------------------------------------
                if event.source.type=='user':#個人區
                    if Member_Info.objects.filter(uid=uid).exists()==True:#測試有沒有註冊
#-----------------------------------------------------------------------------------------------------------
                        '''
                        if 'https://' in mtext:
                            try:
                                liff_id = liff_api.add(
                                    view_type="full",
                                    view_url=mtext)
                                #1607718325-5QmeBQop=google首頁
                                message=[]
                                message.append(TextSendMessage(text='https://liff.line.me/'+liff_id))
                                line_bot_api.reply_message(event.reply_token,message)
                            except:
                                print(err.message)
                        '''
#-----------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
                        if mtext == '取消會員':#玩家取消會員
                            Member_Info.objects.filter(uid=uid).update(status='0')
                            message=[]
                            message.append(TextSendMessage(text='------已取消會員------\n\n如要恢復會員，請洽代理\nLine ID：tata19970830'))
                            line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        if mtext == '進行儲值':#玩家進行儲值
                            message=[]
                            message.append(TextSendMessage(text='如要進行儲值，請洽代理\nLine ID：tata19970830'))
                            line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        if mtext == '餘額查詢':#玩家餘額查詢
                            infos=[]
                            for balance_check in balance_checks:
                                info = '[ %s ]  %s 元'%(balance_check.name,balance_check.wallet)
                                infos.append(info)
                            infos=','.join(infos)
                            infos=infos.replace(",","\n\n")
                            message=[]
                            message.append(TextSendMessage(text=infos))
                            line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        if mtext == '下注紀錄':#玩家下注紀錄
                            infos=[]
                            for bet_record in bet_records:
                                info = '[ %s ]  第%s局  %s\n%s'%(bet_record.name,bet_record.gameno,bet_record.mtext,bet_record.mdt.strftime('%Y-%m-%d  %H:%M:%S'))# %H:%M:%S
                                infos.append(info)
                            infos=','.join(infos)
                            infos=infos.replace(",","\n\n")
                            message=[]
                            message.append(TextSendMessage(text=infos))
                            line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        if mtext == '使用說明':#遊戲使用說明
                            if Root.objects.filter(uid=uid).exists()==False:
                                info='遊戲使用說明\n---------------------------\n1.先到綁定區進行綁定會員\n\n2.找代理進行儲值\n'
                                message=[]
                                message.append(TextSendMessage(text=info))
                                line_bot_api.reply_message(event.reply_token,message)
                            elif Root.objects.filter(uid=uid).exists()==True:
                                info='1.查詢現在注碼\n[Line名字/現在注碼]\n\n2.調整注碼\n[Line名字/莊閒最高/xxxxxx]\n[Line名字/莊閒最低/xxxxxx]\n[Line名字/四寶最高/xxxxxx]\n[Line名字/四寶最低/xxxxxx]\n[Line名字/大小最高/xxxxxx]\n[Line名字/大小最低/xxxxxx]\n\n3.遊戲開關\n開啟遊戲  [1]\n遊戲維修  [2]\n關閉遊戲  [0]\n關閉的時機\n要在本局結果後圖片顯示出來才可以下指令0\n'
                                message=[]
                                message.append(TextSendMessage(text=info))
                                line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                    else:
                        message=[]
                        message.append(TextSendMessage(text='請先進行註冊'))
                        line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        if '現在注碼' in mtext:#控制注碼
                            mt=mtext.split('/',2)
                            bet=Bet.objects.filter(name=mt[0])#現在注碼
                            for bets in bet:
                                max_ab=bets.max_ab
                                min_ab=bets.min_ab
                                max_ss=bets.max_ss
                                min_ss=bets.min_ss
                                max_cd=bets.max_cd
                                min_cd=bets.min_cd
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ] 現在注碼\n\n莊 / 閒 限紅\n%s -至- %s\n\n莊對 / 閒對 / 和局 / 幸運六 限紅\n%s -至- %s\n\n大 / 小 限紅\n%s -至- %s'''%(mt[0],min_ab,max_ab,min_ss,max_ss,min_cd,max_cd)))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                    if Root.objects.filter(uid=uid).exists()==True:#驗證權限
                        if '莊閒最高' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(max_ab=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        if '莊閒最低' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(min_ab=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        if '四寶最高' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(max_ss=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        if '四寶最低' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(min_ss=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        if '大小最高' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(max_cd=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
                        if '大小最低' in mtext:
                            mt=mtext.split('/',3)
                            if Bet.objects.filter(name=mt[0]).exists()==True:
                                Bet.objects.filter(name=mt[0]).update(min_cd=mt[2])
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n莊閒最高更改為%s'''%(mt[0],mt[2])))
                                line_bot_api.reply_message(event.reply_token,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='''[ %s ]\n沒有此會員'''%(mt[0])))
                                line_bot_api.reply_message(event.reply_token,message)
#-----------------------------------------------------------------------------------------------------------
                        if '1' == mtext:#開啟遊戲
                            Gameonoff.objects.all().delete()#控制遊戲開關
                            Gameonoff.objects.create(turn=mtext)
                            message=[]
                            message.append(TextSendMessage(text='現在是遊戲時間'))
                            line_bot_api.reply_message(event.reply_token,message)
                        if '2' == mtext:#遊戲維修
                            Gameonoff.objects.all().delete()
                            Gameonoff.objects.create(turn=mtext)
                            message=[]
                            message.append(TextSendMessage(text='現在是維修時間'))
                            line_bot_api.reply_message(event.reply_token,message)
                        if '0' == mtext:#關閉遊戲
                            Gameonoff.objects.all().delete()
                            Gameonoff.objects.create(turn=mtext)
                            message=[]
                            message.append(TextSendMessage(text='現在不是遊戲時間'))
                            line_bot_api.reply_message(event.reply_token,message)
#▼群組區▼----------------------------------------------------------------------------------------------------
                else:#群組區
                    group_id=event.source.group_id
                    if event.source.type=='group':#user、room、group 個人、聊天室、群組
                        if gameonoff == "1":#遊戲狀態=1 才可以玩
                            if Member_Info.objects.filter(uid=uid).exists()==True:#測試有沒有註冊
                                if player_status!=11:#測試玩家狀態
                                    if player_status==1:#測試玩家狀態
                                        if '遊戲開始' == mtext and Root.objects.filter(uid=uid).exists()==True:
                                            cv_img='static/img/1.jpg'
                                            while True:#秒數辨識等於25.15就開始進行
                                                try:
                                                    window_capture(cv_img)#截圖
                                                    if int(15) == int(cv22(15,184,cv_img)):#數字辨識15
                                                        s=int(15)
                                                        break
                                                    if int(25) == int(cv22(25,184,cv_img)):#數字辨識25
                                                        s=int(25)
                                                        break
                                                except:
                                                    print('err1')
                                                    #pass
                                            print('辨識到%s秒了'%(s))
                                            sbs=black(cv_img) 
                                            second=s
                                            if '大小藍' in sbs:
                                                message=[]
                                                message.append(TextSendMessage(text='▂▂▂▂開始下注▂▂▂▂\n局號｜  %s\n\n---------倒數%s秒---------\n下注單以機器人收單為準'%(game_mdtss,second)))
                                                line_bot_api.push_message(group_id,message)
                                            else:
                                                message=[]
                                                message.append(TextSendMessage(text='▂▂▂▂開始下注▂▂▂▂\n局號｜  %s\n30局后不能投注 大 小 \n---------倒數%s秒---------\n下注單以機器人收單為準'%(game_mdtss,second)))
                                                line_bot_api.push_message(group_id,message)
                                            Gameonoff.objects.filter(turn=1).update(bet_turn=1)#開啟下注動作
                                            if s == int(15):
                                                time.sleep(13)
                                            if s == int(25):
                                                time.sleep(23)

                                            while True:#秒數辨識等於1就開始進行
                                                try:
                                                    window_capture(cv_img)#截圖
                                                    if int(1) == int(cv22(1,184,cv_img)):#數字辨識
                                                        break
                                                except:
                                                    print('err2')
                                                    #pass
                                            print('辨識到1秒')
                                            time.sleep(1)

                                            datas = User_Info.objects.filter(gameno=game_mdtss)#叫出本局資料
                                            message=[]#玩家 
                                            for data in datas:
                                                info = '[ %s ]  %s'%(data.name,data.mtext)
                                                message.append(info)
                                            lenn=len(message)#押注
                                            message = ','.join(message)
                                            info=message.replace(",","\n")
                                            bookmaker=0#莊家
                                            for data in datas:
                                                info1 = '%s'%(data.bookmaker)
                                                if info1 != '':
                                                    bookmaker+=int(info1)
                                            player=0#閒家
                                            for data in datas:
                                                info2 = '%s'%(data.player)
                                                if info2 != '':
                                                    player+=int(info2)
                                            combine = 0#和
                                            for data in datas:
                                                info3 = '%s'%(data.combine)
                                                if info3 != '':
                                                    combine+=int(info3)
                                            bookmaker_r = 0#莊對
                                            for data in datas:
                                                info4 = '%s'%(data.bookmaker_r)
                                                if info4 != '':
                                                    bookmaker_r+=int(info4)
                                            player_r = 0#閒對
                                            for data in datas:
                                                info5 = '%s'%(data.player_r)
                                                if info5 != '':
                                                    player_r+=int(info5)
                                            big_r = 0#大
                                            for data in datas:
                                                info6 = '%s'%(data.big_r)
                                                if info6 != '':
                                                    big_r+=int(info6)
                                            small_r = 0#小
                                            for data in datas:
                                                info7 = '%s'%(data.small_r)
                                                if info7 != '':
                                                    small_r+=int(info7)
                                            lucky_r = 0#幸運六
                                            for data in datas:
                                                info8 = '%s'%(data.lucky_r)
                                                if info8 != '':
                                                    lucky_r+=int(info8)
                                            summ = bookmaker+player+combine+bookmaker_r+player_r+big_r+small_r+lucky_r#總和
                                            Gameonoff.objects.filter(turn=1).update(bet_turn=0)#關閉下注動作
                                            message=[]
                                            message.append(TextSendMessage(text='停止下注\n收單統計'))
                                            message.append(TextSendMessage(text='''▂▂▂牌局資訊▂▂▂\n局號｜  %s\n▂▂▂下注有效玩家▂▂▂\n%s\n▂▂▂下注總表▂▂▂\n莊｜  %s\n閒｜  %s\n和｜  %s\n莊對｜  %s\n閒對｜  %s\n大｜  %s\n小｜  %s\n幸運六｜  %s\n\n押注｜  %s\n押注總和｜  %s\n'''%(game_mdtss,info,bookmaker,player,combine,bookmaker_r,player_r,big_r,small_r,lucky_r,lenn,summ)))
                                            line_bot_api.push_message(group_id,message)
                                            time.sleep(10)#等待翻牌

                                            '''遊戲結果辨識程式區'''
                                            while True:#辨識金條就開始進行
                                                try:
                                                    cv_img='static/img/game_result/%s.jpg'%(img_no)
                                                    window_capture(cv_img)#截圖
                                                    li=list(cv22(777,150,cv_img))
                                                    if int(1) in li:#金條辨識
                                                        print('辨識到金條了')
                                                        b_result=numbers(cv_img)[0]#莊牌結果
                                                        print(b_result,'莊')
                                                        p_result=numbers(cv_img)[1]#閒牌結果
                                                        print(p_result,'閒')
                                                        la_result=f_result(cv_img)#最終遊戲結果
                                                        #print(la_result,'遊戲結果')
                                                        if len(la_result) > 0:
                                                            #print(len(la_result))
                                                            strr=" ".join(la_result) 
                                                            print('遊戲結果-------------------------------',strr)
                                                        else:
                                                            print('辨識不完整')
                                                        img_resize(img_no)#調整圖片
                                                        Game_result.objects.create(gameno_result=game_mdtss,game_bookmaker=b_result,game_player=p_result,result_game=strr)
                                                        break
                                                except:
                                                    print('err3')
                                                    #pass

                                            if '莊' in la_result:
                                                game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(bookmaker='')#查看本局下註記綠
                                                for game_result in game_results:
                                                    game_result_uid=game_result.uid#uid
                                                    game_result_bookmaker=game_result.bookmaker
                                                    calculation = int(game_result_bookmaker)*bookmaker_odds#計算賠率後的輸贏結果
                                                    balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
                                                    for balance_check_result in balance_checks_result:
                                                        info = balance_check_result.wallet
                                                        wallet_results=info+calculation+int(game_result_bookmaker)
                                                    Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
                                            if '閒' in la_result:
                                                game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(player='')#查看本局下註記綠
                                                for game_result in game_results:
                                                    game_result_uid=game_result.uid#uid
                                                    game_result_player=game_result.player
                                                    calculation = int(game_result_player)*player_odds#計算賠率後的輸贏結果
                                                    balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
                                                    for balance_check_result in balance_checks_result:
                                                        info = balance_check_result.wallet
                                                        wallet_results=info+calculation+int(game_result_player)
                                                    Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
                                            if '和' in la_result:
                                                game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(combine='')#查看本局下註記綠
                                                for game_result in game_results:
                                                    game_result_uid=game_result.uid#uid
                                                    game_result_combine=game_result.combine
                                                    calculation = int(game_result_combine)*combine_odds#計算賠率後的輸贏結果
                                                    balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
                                                    for balance_check_result in balance_checks_result:
                                                        info = balance_check_result.wallet
                                                        wallet_results=info+calculation+int(game_result_combine)
                                                    Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
                                            if '莊對' in la_result:
                                                game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(bookmaker_r='')#查看本局下註記綠
                                                for game_result in game_results:
                                                    game_result_uid=game_result.uid#uid
                                                    game_result_bookmaker_r=game_result.bookmaker_r
                                                    calculation = int(game_result_bookmaker_r)*bookmaker_r_odds#計算賠率後的輸贏結果
                                                    balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
                                                    for balance_check_result in balance_checks_result:
                                                        info = balance_check_result.wallet
                                                        wallet_results=info+calculation+int(game_result_bookmaker_r)
                                                    Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
                                            if '閒對' in la_result:
                                                game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(player_r='')#查看本局下註記綠
                                                for game_result in game_results:
                                                    game_result_uid=game_result.uid#uid
                                                    game_result_player_r=game_result.player_r
                                                    calculation = int(game_result_player_r)*player_r_odds#計算賠率後的輸贏結果
                                                    balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
                                                    for balance_check_result in balance_checks_result:
                                                        info = balance_check_result.wallet
                                                        wallet_results=info+calculation+int(game_result_player_r)
                                                    Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
                                            if '大' in la_result:
                                                game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(big_r='')#查看本局下註記綠
                                                for game_result in game_results:
                                                    game_result_uid=game_result.uid#uid
                                                    game_result_big_r=game_result.big_r
                                                    calculation = int(game_result_big_r)*big_r_odds#計算賠率後的輸贏結果
                                                    balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
                                                    for balance_check_result in balance_checks_result:
                                                        info = balance_check_result.wallet
                                                        wallet_results=info+calculation+int(game_result_big_r)
                                                    Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
                                            if '小' in la_result:
                                                game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(small_r='')#查看本局下註記綠
                                                for game_result in game_results:
                                                    game_result_uid=game_result.uid#uid
                                                    game_result_small_r=game_result.small_r
                                                    calculation = int(game_result_small_r)*small_r_odds#計算賠率後的輸贏結果
                                                    balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
                                                    for balance_check_result in balance_checks_result:
                                                        info = balance_check_result.wallet
                                                        wallet_results=info+calculation+int(game_result_small_r)
                                                    Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包
                                            if '幸運六' in la_result:
                                                game_results=User_Info.objects.filter(gameno=game_mdtss).exclude(lucky_r='')#查看本局下註記綠
                                                for game_result in game_results:
                                                    game_result_uid=game_result.uid#uid
                                                    game_result_lucky_r=game_result.lucky_r
                                                    calculation = int(game_result_lucky_r)*lucky_r_odds#計算賠率後的輸贏結果
                                                    balance_checks_result=Member_Info.objects.filter(uid=game_result_uid)#各玩家餘額查詢
                                                    for balance_check_result in balance_checks_result:
                                                        info = balance_check_result.wallet
                                                        wallet_results=info+calculation+int(game_result_lucky_r)
                                                    Member_Info.objects.filter(uid=game_result_uid).update(wallet=wallet_results)#計算完成後更新錢包

                                            datas = User_Info.objects.filter(gameno=game_mdtss)#叫出本局資料
                                            total_win_lose=0
                                            messages=[]
                                            for data in datas:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",data.mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",data.mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",data.mtext)
                                                if mtextc == '莊' and '莊' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtextc+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtexte == 'A' and '莊' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtextc == '閒' and '閒' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtextc+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtexte == 'B' and '閒' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtextc == '和' and '和' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtextc+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtexte == 'H' and '和' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtextc == '莊對' and '莊對' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtextc+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtexte == 'AD' and '莊對' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtextc == '閒對' and '閒對' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtextc+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtexte == 'BD' and '閒對' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtextc == '大' and '大' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtextc+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtexte == 'E' and '大' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtextc == '小' and '小' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtextc+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtexte == 'F' and '小' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtextc == '幸運六' and '幸運六' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtextc+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                elif mtexte == 'L' and '幸運六' in la_result:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+'｜+'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose+=int(mtextt)
                                                else:
                                                    open_result='[ %s ]  %s'%(data.name,mtexte+mtextc+'｜-'+mtextt)
                                                    messages.append(open_result)
                                                    total_win_lose-=int(mtextt)
                                            messages = ','.join(messages)
                                            info=messages.replace(",","\n")

                                            message=[]
                                            message.append(TextSendMessage(text='''▂▂▂開牌結果▂▂▂\n局號｜%s\n勝  %s\n▂▂▂開獎輸贏▂▂▂\n%s\n▂▂▂輸贏總表▂▂▂\n押注｜%s\n總輸贏｜%s\n'''%(game_mdtss,strr,info,lenn,total_win_lose)))
                                            line_bot_api.push_message(group_id,message)
                                            message=[]
                                            o_c_url='https://2e58e9302c3c.ngrok.io/static/img/game_result/123/%s.jpg'%(img_no)
                                            message = ImageSendMessage(original_content_url=o_c_url, preview_image_url=o_c_url)
                                            line_bot_api.push_message(group_id,message)
                                            game_no=int(game_no)+1#局數+1
                                            Game_no.objects.create(nonow=game_no)
                                            time.sleep(1)#等待下一局

                                            gameonofff=Gameonoff.objects.last()
                                            gameonoff=gameonofff.turn#現在遊戲開關狀態
                                            red_img='static/img/game_result/%s.jpg'%(img_no)
                                            if '紅牌' not in red(red_img):
                                                #print('沒紅牌')
                                                if gameonoff == "1":#遊戲狀態=1 才可以玩
                                                    callback(request)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='今日遊戲結束\n謝謝各位'))
                                                    line_bot_api.push_message(group_id,message)
                                            else:
                                                print('紅牌')
                                                message=[]
                                                message.append(TextSendMessage(text='遊戲洗牌中\n請各位休息稍等\n'))
                                                line_bot_api.push_message(group_id,message)
                                                time.sleep(200)#等待下一局#3:33
                                                message.append(TextSendMessage(text='遊戲即將開始\n請各位選手準備\n'))
                                                line_bot_api.push_message(group_id,message)
                                                callback(request)

                                        bs = black('static/img/1.jpg')
                                        if bet_turn == '1':#下注審核
                                            bet=Bet.objects.filter(uid=uid)
                                            for bets in bet:
                                                max_ab=bets.max_ab
                                                min_ab=bets.min_ab
                                                max_ss=bets.max_ss
                                                min_ss=bets.min_ss
                                                max_cd=bets.max_cd
                                                min_cd=bets.min_cd
                                            if '莊' in mtext or 'A' in mtext:
                                                if '對' not in mtext and 'D' not in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_ab) <= int(mtextt) <= int(max_ab):#檢查限紅
                                                            if mtextc != '':
                                                                if mtextc != '莊':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,bookmaker=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                            if mtexte != '':
                                                                if mtexte != 'A':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,bookmaker=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.push_message(group_id,message)
                                            elif '閒' in mtext or 'B' in mtext:
                                                if '對' not in mtext and 'D' not in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_ab) <= int(mtextt) <= int(max_ab): 
                                                            if mtextc != '':
                                                                if mtextc != '閒':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,player=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                            if mtexte != '':
                                                                if mtexte != 'B':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,player=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.push_message(group_id,message)
                                            elif '和' in mtext or 'H' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt) <= int(max_ss): 
                                                            if mtextc != '':
                                                                if mtextc != '和':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                            if mtexte != '':
                                                                if mtexte != 'H':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.push_message(group_id,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.push_message(group_id,message)
                                            elif '莊對' in mtext or 'AD' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt) <= int(max_ss): 
                                                            if mtextc != '':
                                                                if mtextc != '莊對':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                            if mtexte != '':
                                                                if mtexte != 'AD':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.push_message(group_id,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.push_message(group_id,message)
                                            elif '閒對' in mtext or 'BD' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt) <= int(max_ss): 
                                                            if mtextc != '':
                                                                if mtextc != '閒對':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                            if mtexte != '':
                                                                if mtexte != 'BD':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.push_message(group_id,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.push_message(group_id,message)
                                            elif '大小藍' in bs:
                                                if '大' in mtext or 'E' in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_cd) <= int(mtextt) <= int(max_cd): 
                                                                if mtextc != '':
                                                                    if mtextc != '大':
                                                                        message=[]
                                                                        message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                        line_bot_api.push_message(group_id,message)
                                                                    else:
                                                                        User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,big_r=mtextt)
                                                                        Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                        info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                        message=[]
                                                                        message.append(TextSendMessage(text=info))
                                                                        line_bot_api.push_message(group_id,message)
                                                                if mtexte != '':
                                                                    if mtexte != 'E':
                                                                        message=[]
                                                                        message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                        line_bot_api.push_message(group_id,message)
                                                                    else:
                                                                        User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,big_r=mtextt)
                                                                        Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                        info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                        message=[]
                                                                        message.append(TextSendMessage(text=info))
                                                                        line_bot_api.push_message(group_id,message)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.push_message(group_id,message)
                                                elif '小' in mtext or 'F' in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_cd) <= int(mtextt) <= int(max_cd): 
                                                                if mtextc != '':
                                                                    if mtextc != '小':
                                                                        message=[]
                                                                        message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                        line_bot_api.push_message(group_id,message)
                                                                    else:
                                                                        User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,small_r=mtextt)
                                                                        Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                        info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                        message=[]
                                                                        message.append(TextSendMessage(text=info))
                                                                        line_bot_api.push_message(group_id,message)
                                                                if mtexte != '':
                                                                    if mtexte != 'F':
                                                                        message=[]
                                                                        message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                        line_bot_api.push_message(group_id,message)
                                                                    else:
                                                                        User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,small_r=mtextt)
                                                                        Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                        info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                        message=[]
                                                                        message.append(TextSendMessage(text=info))
                                                                        line_bot_api.push_message(group_id,message)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.push_message(group_id,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.push_message(group_id,message)
                                            elif '幸運六' in mtext or 'L' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt) <= int(max_ss): 
                                                            if mtextc != '':
                                                                if mtextc != '幸運六':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtextc+'｜'+mtextt,gameno=game_mdtss,lucky_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                            if mtexte != '':
                                                                if mtexte != 'L':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext=mtexte+'｜'+mtextt,gameno=game_mdtss,lucky_r=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt))
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.push_message(group_id,message)
                                                                    
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.push_message(group_id,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.push_message(group_id,message)
                                            if '三寶' in mtext or 'S' in mtext:
                                                if 'SS' not in mtext:
                                                    mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                    mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                    mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                    if int(now_wallet) > int(mtextt):
                                                        if int(min_ss) <= int(mtextt)*3 <= int(max_ss):#檢查限紅
                                                            if mtextc != '':
                                                                if mtextc != '三寶':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤1'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='莊對'+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='閒對'+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='和'+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt)*3)
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.reply_message(event.reply_token,message)
                                                            if mtexte != '':
                                                                if mtexte != 'S':
                                                                    message=[]
                                                                    message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤2'%(name)))
                                                                    line_bot_api.push_message(group_id,message)
                                                                else:
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='莊對'+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='閒對'+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                    User_Info.objects.create(uid=uid,name=name,mtext='和'+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                    Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt)*3)
                                                                    info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                    message=[]
                                                                    message.append(TextSendMessage(text=info))
                                                                    line_bot_api.reply_message(event.reply_token,message)
                                                        else:
                                                            message=[]
                                                            message.append(TextSendMessage(text='請符合下注限紅'))
                                                            line_bot_api.reply_message(event.reply_token,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                        line_bot_api.reply_message(event.reply_token,message)
                                            if '四寶' in mtext or 'SS' in mtext:
                                                mtextc = re.sub(u"([^\u4e00-\u9fa5])","",mtext)
                                                mtexte = re.sub(u"([^\u0041-\u005a])","",mtext)
                                                mtextt = re.sub(u"([^\u0030-\u0039])","",mtext)
                                                if int(now_wallet) > int(mtextt):
                                                    if int(min_ss) <= int(mtextt)*3 <= int(max_ss):#檢查限紅
                                                        if mtextc != '':
                                                            if mtextc != '四寶':
                                                                message=[]
                                                                message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤3'%(name)))
                                                                line_bot_api.push_message(group_id,message)
                                                            else:
                                                                User_Info.objects.create(uid=uid,name=name,mtext='莊對'+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='閒對'+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='和'+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt)*3)
                                                                info='%s\n%s｜%s  🉐️'%(name,mtextc,mtextt)
                                                                message=[]
                                                                message.append(TextSendMessage(text=info))
                                                                line_bot_api.reply_message(event.reply_token,message)
                                                        if mtexte != '':
                                                            if mtexte != 'SS':
                                                                message=[]
                                                                message.append(TextSendMessage(text='[ %s ]\n下注格式錯誤4'%(name)))
                                                                line_bot_api.push_message(group_id,message)
                                                            else:
                                                                User_Info.objects.create(uid=uid,name=name,mtext='莊對'+'｜'+mtextt,gameno=game_mdtss,bookmaker_r=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='閒對'+'｜'+mtextt,gameno=game_mdtss,player_r=mtextt)
                                                                User_Info.objects.create(uid=uid,name=name,mtext='和'+'｜'+mtextt,gameno=game_mdtss,combine=mtextt)
                                                                Member_Info.objects.filter(uid=uid).update(wallet=int(now_wallet) - int(mtextt)*3)
                                                                info='%s\n%s｜%s  🉐️'%(name,mtexte,mtextt)
                                                                message=[]
                                                                message.append(TextSendMessage(text=info))
                                                                line_bot_api.reply_message(event.reply_token,message)
                                                    else:
                                                        message=[]
                                                        message.append(TextSendMessage(text='請符合下注限紅'))
                                                        line_bot_api.reply_message(event.reply_token,message)
                                                else:
                                                    message=[]
                                                    message.append(TextSendMessage(text='[%s] 錢包餘額不夠'%(name)))
                                                    line_bot_api.reply_message(event.reply_token,message)
                                    else:
                                        message=[]
                                        message.append(TextSendMessage(text='%s已取消會員\n請找代理恢復會員'%(name)))
                                        line_bot_api.push_message(group_id,message)
                                else:
                                    message=[]
                                    message.append(TextSendMessage(text='%s重複註冊會員\n請找代理恢復會員'%(name)))
                                    line_bot_api.push_message(group_id,message)
                            else:
                                message=[]
                                message.append(TextSendMessage(text='請先進行註冊 @%s'%(name)))
                                line_bot_api.push_message(group_id,message)
                        else:
                            message=[]
                            message.append(TextSendMessage(text='現在不是遊戲時間'))
                            line_bot_api.push_message(group_id,message)
                return HttpResponse()
            else:
                return HttpResponseBadRequest()