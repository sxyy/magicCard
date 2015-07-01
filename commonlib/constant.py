# -*- coding: utf-8 -*-
 
DOMAIN = r'http://172.18.49.102/bbs/'
USERNAME = 1105858958
PASSWORD = r'asdfgh'
CODE = '';
SESSION = '';
LOGINFIELD = r'username'
APPID = '549000912'
DATABASE = 'test.db';
COLLECTTHEMEID = -1;
COLLECTTHEMEID2 = -1;
STEALFRIEND = -1;
STEALFRIEND2 = -1;
QQSHOWSELECT = -1;
QQSHOWSELECT2 = -1;
QQSHOWID = 0;
QQSHOWID2 = 0;
EXCHANGEBOXNUM = 0;
STOREBOXNUM = 0;
SLOVENUM =0;
ISRED  = 0;
#抽卡次数
RANDCHANCE = 0;
 
ISNEEDCODEURL = r'http://check.ptlogin2.qq.com/check?uin=UIN&regmaster=&appid='+APPID+'&ptlang=2052&pt_tea=1&login_sig=&r=RANDOM '
CODEPIC = r'http://captcha.qq.com/getimage?aid='+APPID+'&r=RANDOM&cap_cd=CD&uin=UIN'
LOGINURL = r'http://ptlogin2.qq.com/login?u=USERNAME&p=PASSWORD&pt_vcode_v1=0&pt_verifysession_v1=VERIFYSESSION&pt_randsalt=0&login_sig=&verifycode=CODE&mibao_css=m_qzone&aid=549000912&u1=http%3A%2F%2Fimgcache.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone&ptredirect=1&h=1&from_ui=1&fp=loginerroralert&g=1&t=1&daid=5&pt_qzone_sig=1'
CARDLOGINURL = r'http://card.show.qq.com/cgi-bin/card_user_mainpage?g_tk=GTK '
SALECARD = r'http://card.show.qq.com/cgi-bin/card_market_npc_sell?g_tk=GTK '
CARDINPUTSTOREBOX = r'http://card.show.qq.com/cgi-bin/card_user_storage_exchange?g_tk=GTK';
DRAWCARDURL = r'http://card.show.qq.com/cgi-bin/card_user_random_get?g_tk=GTK '
BUYCARDURL = r'http://card.show.qq.com/cgi-bin/card_market_npc_buy?g_tk=GTK '
REFINEDCARD = r'http://card.show.qq.com/cgi-bin/card_stove_refinedcard_get?g_tk=GTK'
STOVEREFINEURL = r'http://card.show.qq.com/cgi-bin/card_stove_refine?g_tk=GTK'
USERLISTURL = r'http://card.show.qq.com/cgi-bin/card_user_list?g_tk=GTK'
GETSTEALCARD = r'http://card.show.qq.com/cgi-bin/card_stove_stealcard_get?g_tk=GTK'
STEALCARD = r'http://card.show.qq.com/cgi-bin/card_stove_steal?g_tk=GTK '
COLLECTADD = r'http://card.show.qq.com/cgi-bin/card_collection_add?g_tk=GTK';  #themetype=0&giftid=1330&cardtype=1&theme=382
QQSHOWURL = r'http://imgcache.qq.com/qqshow_v3/htdocs/syndata/excel_snashot/PAGENUM/ITEMNUM/IMAGENUM_0.gif'
MONEYDRAW = r'http://card.show.qq.com/cgi-bin/card_user_money_draw?g_tk=GTK'
FANPAIURL = r'http://card.show.qq.com/cgi-bin/card_pai_open?g_tk=GTK';
DAILYURL = r'http://sh.show.qq.com/cgi-bin/qs_sh_card_dailygift?g_tk=GTK'
'''
<?xml version="1.0" encoding="UTF-8"?>
<QQHOME code="0" money="316638" score="1376142" sendcard="5539" lv_diff="0" lv="54">
</QQHOME>
http://card.show.qq.com/cgi-bin/card_user_money_draw?g_tk=141761406
uin

<?xml version="1.0" encoding="UTF-8"?>
<QQHOME capable="0" code="0" money="5699" exp="1429" stovenum="1" rentstovenum="0" lv="5" fp_cnt="1" add_jf="60" day_get_fp="3" lv_diff="0">
    <card uin="1105858958" location="0" slot="5" status="0" time="1434268675" id="2555" cardname="&#x95C6;&#x546D;&#x59EB;&#x93C2;&#x0020;" cardpri="40" type="1" themename="&#x7F03;&#x6945;&#x2508;&#x7EC1;&#x70B6;&#x763D;" themeid="191"></card>
    <bj_card location="0" slot="0" status="0" time="0" id="0" cardname="" cardpri="0" type="0" themename="" themeid="0"></bj_card>
</QQHOME>
http://sh.show.qq.com/cgi-bin/qs_sh_card_dailygift?g_tk=1528628585 
type:0
uin:411249087
'''
EXCHANGEBOX = 0;
STOREBOX = 1;
STOVEBOX = 2;
MESSAGE = [];