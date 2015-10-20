# -*- coding: utf-8 -*-
 
DOMAIN = r'http://172.18.49.102/bbs/'
USERNAME = 1105858958
PASSWORD = r'asdfgh'
CODE = ''
SESSION = ''
LOGINFIELD = r'username'
APPID = '549000912'
APPID2 = '15403'
APPID3 = '1600000084'
DATABASE = 'test.db'
REFINEDTYPE = 0
COLLECTTHEMEID = -1
COLLECTTHEMEID2 = -1
STEALFRIEND = -1
STEALFRIEND2 = -1
QQSHOWSELECT = -1
QQSHOWSELECT2 = -1
QQSHOWID = 0
QQSHOWID2 = 0
EXCHANGEBOXNUM = 0
STOREBOXNUM = 0
SLOVENUM =0
ISRED  = 0
#抽卡次数
RANDCHANCE = 0
# 运行状态
RUNSTATE = False

#默认购买卡片的id
DEFAULTBYCARDID= 329
ISSALEOFFCARD = 0
MOJINGDICT = {'add_cmj':u'橙魔晶','add_hmj':u'红魔晶','add_zmj':u'紫魔晶'}
GIFTDICT = {'2':u'升炉卡','3':u'开箱卡','4':u'小魔瓶','5':u'中魔瓶','6':u'大魔瓶','7':u'100面值卡','8':u'200面值卡','9':u'抽卡包','10':u'600面值卡','12':u'租炉卡7天',
            '13':u'租炉卡3天','43':u'幸运卡','44':u'金币','45':u'经验','46':u'五彩石','51':u'橙魔晶','52':u'红魔晶','53':u'紫魔晶','55':u'魔力'}
#搜索的卡友数目
CARDUSERNUM = 100
#是否更新数据库
ISUPDATEDB = 1
#通过web进行提交
ISCOMMITBYWEB = 1
#是否满足卡片就提交
ISCOMPLETECOMMIT = 0
#是否搜索偷炉位好友
ISSEARCHSTEALFRIEND = 0

###手机偷卡
SID = '-1'
NEWCODE = ''
COMMITCARD = r'http://mfkp.qzapp.z.qq.com/qshow/cgi-bin/wl_card_collection_add?sid=SID&themeid=THEMEID&themetype=0&cardtype=0'
MAINPAGE = r'http://pt.3g.qq.com/s?aid=nLogin&sid=AfYLxNl-zrRwzRvmKiZc5aV8'
GIFTURL = r'http://card.show.qq.com/cgi-bin/card_task_activity?g_tk=GTK'
GETSID = r'http://pt.3g.qq.com/handleLogin?sid=AfYLxNl-zrRwzRvmKiZc5aV8&vdata=643C15A85505190D7375ED14A2F70D3A'
TRANSFER_CARD = r'http://card.show.qq.com/cgi-bin/card_user_transfer_card?g_tk=GTK'
GETGIFTLISTURL = r'http://hydra.qzone.qq.com/cgi-bin/freegift/freegift_get_list?g_tk=GTK&appid=365&uin=USERNAME&cb=1&r=0.7080595267470926'
GIFTRECEIVE = r'http://hydra.qzone.qq.com/cgi-bin/freegift/freegift_take?g_tk=GTK'
MOBILESTEALCARD = r'http://mfkp.qzapp.z.qq.com/qshow/cgi-bin/wl_card_refine?sid=SID&tid=TID&fuin=FRENDID&steal=1&buy=1&id=CARDID&tt=1&s1=117440513&s2=117440513&s3=117440513&t1=117440514&t2=117440514&t3=117440514 '
GETCARD = r'http://hydra.qzone.qq.com/cgi-bin/activity/exchange_gift?g_tk=GTK'
ZCGINFOURL = r'http://card.show.qq.com/cgi-bin/card_user_zcg?g_tk=GTK'
SENDCARD = r'http://hydra.qzone.qq.com/cgi-bin/freegift/freegift_send?g_tk=GTK'
ACTEGG = r'http://card.show.qq.com/cgi-bin/card_act_get_free?g_tk=GTK'

ISNEEDCODEURL2 = r'http://check.ptlogin2.qq.com/check?pt_tea=1&uin=UIN&appid='+APPID2+'&ptlang=2052&r=RANDOM'#APP2
ISNEEDCODEURL3 = r'http://check.ptlogin2.qq.com/check?pt_tea=1&uin=UIN&appid='+APPID3+'&ptlang=2052&r=RANDOM'#APP2
ISNEEDCODEURL = r'http://check.ptlogin2.qq.com/check?uin=UIN&regmaster=&appid='+APPID+'&ptlang=2052&pt_tea=1&login_sig=&r=RANDOM '
CODEPIC = r'http://captcha.qq.com/getimage?aid='+APPID+'&r=RANDOM&cap_cd=CD&uin=UIN'
CODEPIC2 = r'http://captcha.qq.com/getimage?aid='+APPID2+'&r=RANDOM&cap_cd=CD&uin=UIN'#http://mfkp.qzapp.z.qq.com/qshow/cgi-bin/wl_card_mainpage
CODEPIC3 = r'http://captcha.qq.com/getimage?aid='+APPID3+'&r=RANDOM&cap_cd=CD&uin=UIN'
LOGINURL = r'http://ptlogin2.qq.com/login?u=USERNAME&p=PASSWORD&pt_vcode_v1=0&pt_verifysession_v1=VERIFYSESSION&pt_randsalt=0&login_sig=&verifycode=CODE&mibao_css=m_qzone&aid=549000912&u1=http%3A%2F%2Fimgcache.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone&ptredirect=1&h=1&from_ui=1&fp=loginerroralert&g=1&t=1&daid=5&pt_qzone_sig=1'
LOGINURL2 = r'http://ptlogin2.qq.com/login?pt_vcode_v1=0&pt_verifysession_v1=VERIFYSESSION&verifycode=CODE&u=USERNAME&p=PASSWORD&pt_randsalt=0&ptlang=2052&low_login_enable=0&u1=http%3A%2F%2Fmfkp.qzapp.z.qq.com%2Fqshow%2Fcgi-bin%2Fwl_card_mainpage&from_ui=1&fp=loginerroralert&device=2&aid=1600000084&pt_3rd_aid=0&ptredirect=1&h=1&g=1&pt_uistyle=9&'
QQLOGINURL = r'http://ptlogin2.qq.com/login?pt_vcode_v1=0&pt_verifysession_v1=VERIFYSESSION&verifycode=CODE&u=USERNAME&p=PASSWORD&pt_randsalt=0&ptlang=2052&low_login_enable=0&u1=http://info.3g.qq.com&from_ui=1&fp=loginerroralert&device=2&aid=15403&pt_ttype=1&pt_3rd_aid=0&ptredirect=1&h=1&g=1&pt_uistyle=9& '
CARDLOGINURL = r'http://card.show.qq.com/cgi-bin/card_user_mainpage?g_tk=GTK '
SALECARD = r'http://card.show.qq.com/cgi-bin/card_market_npc_sell?g_tk=GTK '
CARDINPUTSTOREBOX = r'http://card.show.qq.com/cgi-bin/card_user_storage_exchange?g_tk=GTK'
DRAWCARDURL = r'http://card.show.qq.com/cgi-bin/card_user_random_get?g_tk=GTK '
BUYCARDURL = r'http://card.show.qq.com/cgi-bin/card_market_npc_buy?g_tk=GTK '
REFINEDCARD = r'http://card.show.qq.com/cgi-bin/card_stove_refinedcard_get?g_tk=GTK'
STOVEREFINEURL = r'http://card.show.qq.com/cgi-bin/card_stove_refine?g_tk=GTK'
USERLISTURL = r'http://card.show.qq.com/cgi-bin/card_user_list?g_tk=GTK'
GETSTEALCARD = r'http://card.show.qq.com/cgi-bin/card_stove_stealcard_get?g_tk=GTK'
STEALCARD = r'http://card.show.qq.com/cgi-bin/card_stove_steal?g_tk=GTK '
COLLECTADD = r'http://card.show.qq.com/cgi-bin/card_collection_add?g_tk=GTK'  #themetype=0&giftid=1330&cardtype=1&theme=382
QQSHOWURL = r'http://imgcache.qq.com/qqshow_v3/htdocs/syndata/excel_snashot/PAGENUM/ITEMNUM/IMAGENUM_0.gif'
MONEYDRAW = r'http://card.show.qq.com/cgi-bin/card_user_money_draw?g_tk=GTK'
FANPAIURL = r'http://card.show.qq.com/cgi-bin/card_pai_open?g_tk=GTK'
DAILYURL = r'http://sh.show.qq.com/cgi-bin/qs_sh_card_dailygift?g_tk=GTK'
THEMELISTURL = r'http://card.show.qq.com/cgi-bin/card_user_theme_list?g_tk=GTK'
REGISTERMAGICCARD = r'http://card.show.qq.com/cgi-bin/card_user_register?g_tk=GTK&timestamp=36236368_0.7147724962439818'
MAGICCARDGUIDE = r'http://card.show.qq.com/cgi-bin/card_user_guide_report?g_tk=GTK'
MAGICCOMMLETEMISSION = r'http://card.show.qq.com/cgi-bin/card_mission_complete?g_tk=GTK'
MOBILEMAINPAGE = r'http://mfkp.qzapp.z.qq.com/qshow/cgi-bin/wl_card_mainpage?g_f=19011&sid=SID'
#BxiIOTtHcDP6ISg6g3WPOO5dPtbxHl1Mbeaab4550201%3d%3d
MOBILEREFINEDCARD = r'http://mfkp.qzapp.z.qq.com/qshow/cgi-bin/wl_card_refinedcard_get?sid=SID&target_id='
MOBILELIANCARD = r'http://mfkp.qzapp.z.qq.com/qshow/cgi-bin/wl_card_refine?sid=SID&tid=52&fuin=0&steal=0&buy=1&id=62&tt=1&s1=117440513&s2=117440513&s3=117440513&t1=117440514&t2=117440514&t3=117440514'
GQGETGIFTS = r'http://card.show.qq.com/cgi-bin/card_act_get_gifts?g_tk=GTK'
GQACTIVITY = r'http://card.show.qq.com/cgi-bin/card_task_activity??g_tk=GTK'
LEVELUP = r'http://card.show.qq.com/cgi-bin/card_user_levelup_bonus?g_tk=GTK'

SEARCHTHEMEID = 204
EXCHANGEBOX = 0
STOREBOX = 1
STOVEBOX = 2
ZCG = 3
MESSAGE = []