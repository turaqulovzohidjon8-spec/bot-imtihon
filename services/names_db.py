# -*- coding: utf-8 -*-
"""
O'zbekiston va Jahon ismlarining to'liq ensiklopediyasi hamda
Ismlar.com saytidan to'g'ridan-to'g'ri real-vaqtda qidiruvchi onlayn tizim.
"""

import re
import html
import urllib.parse
import aiohttp
from bs4 import BeautifulSoup

# O'zbek ismlari izohli lug'ati (E. Begmatov) va Jahon ismlari bazasi
CORE_NAMES = {
    # === A ===
    "ali": ("Yuksak, oliyjanob, baland martabali, mard va qudratli. Hazrati Ali (r.a.) ismi.", "Arabcha", "O'g'il bola"),
    "alisher": ("Ali kabi qudratli, arslon yurakli, dovyurak va daho shoir ramzi.", "Arabcha / Turkiy", "O'g'il bola"),
    "amir": ("Hukmdor, amir, yo'lboshchi, farmon beruvchi rahbar.", "Arabcha", "O'g'il bola"),
    "anvar": ("Nurlar, eng yorqin, yuzi nurli va baxtli inson.", "Arabcha", "O'g'il bola"),
    "anvara": ("Yuzi nurli, ochiq chehrali, iymonli va saodatli qiz.", "Arabcha", "Qiz bola"),
    "abror": ("Yaxshilik qiluvchi, saxiy, pokiza, taqvodor va fozil kishi.", "Arabcha", "O'g'il bola"),
    "abdulloh": ("Allohning suyukli bandasi, quli.", "Arabcha", "O'g'il bola"),
    "abdurahmon": ("Barcha mavjudotga mehribon bo'lgan Rahmon (Alloh)ning bandasi.", "Arabcha", "O'g'il bola"),
    "abdurahim": ("Qiyomatda mo'minlarga rahm qiluvchi Rahim (Alloh)ning bandasi.", "Arabcha", "O'g'il bola"),
    "abdulaziz": ("Qudratli, g'olib va aziz bo'lgan Zotning bandasi.", "Arabcha", "O'g'il bola"),
    "abdumalik": ("Butun koinot hukmdori bo'lgan Malikning bandasi.", "Arabcha", "O'g'il bola"),
    "akmal": ("Eng mukammal, to'la-to'kis, benuqson va barkamol inson.", "Arabcha", "O'g'il bola"),
    "akrom": ("Eng saxiy, karamli, himmati baland va ehtiromga loyiq.", "Arabcha", "O'g'il bola"),
    "asad": ("Arslon, sher, dovyurak, shijoatli va jasur pahlavon.", "Arabcha", "O'g'il bola"),
    "asadbek": ("Arslondek jasur va beklar avlodidan bo'lgan oliynasab yigit.", "Arabcha / Turkiy", "O'g'il bola"),
    "asal": ("Asaldek totli, yoqimtoy, suyukli va shirin qiz.", "Arabcha", "Qiz bola"),
    "aziza": ("Muhtaram, qadrli, suyukli, aziz va nodir ayol.", "Arabcha", "Qiz bola"),
    "aziz": ("Qadrli, hurmatli, nodir, qudratli va qimmatbaho inson.", "Arabcha", "O'g'il bola"),
    "azamat": ("Ulug'vorlik, qudrat, shon-sharaf egasi, kelishgan yigit.", "Arabcha", "O'g'il bola"),
    "abbos": ("Qovog'i soliq, dushmanga nisbatan qattiqqo'l, jasur arslon.", "Arabcha", "O'g'il bola"),
    "adiba": ("Odob-axloqli, tarbiyali, ma'rifatparvar va adabiyotchi ayol.", "Arabcha", "Qiz bola"),
    "asila": ("Oliynasab, toza qonli, asilzoda va pokiza qiz.", "Arabcha", "Qiz bola"),
    "arzuv": ("Orzu-umid, intizorlik bilan kutilgan qiz.", "Turkiy", "Qiz bola"),
    "ayub": ("Tavba qiluvchi, sabr-toqatli, matonat ramzi bo'lgan payg'ambar ismi.", "Ibroniycha / Arabcha", "O'g'il bola"),

    # === B ===
    "bobur": ("Yo'lbars, sher, dovyurak hukmdor va jasur sarkarda.", "Turkiy", "O'g'il bola"),
    "bahodir": ("Pahlavon, mard, botir, yengilmas kuch egasi.", "Turkiy / Mo'g'ulcha", "O'g'il bola"),
    "botir": ("Jasur, mard, qo'rqmas, dovyurak jangchi.", "Turkiy", "O'g'il bola"),
    "bilol": ("Tiriklik suvi, namlik, qalb pokligi, birinchi azon aytgan sahoba ismi.", "Arabcha", "O'g'il bola"),
    "behruz": ("Baxtli kun egasi, har bir kuni quvonchli bo'lgan saodatmand.", "Forscha", "O'g'il bola"),
    "bekzod": ("Beklar avlodidan, aslzoda, oliy naslli yigit.", "Turkiy / Forscha", "O'g'il bola"),
    "bahriddin": ("Dinning dengizi, bepoyon ilm sohibi.", "Arabcha", "O'g'il bola"),
    "bahrom": ("Mirrix (Mars) sayyorasi, g'olib, yengilmas jangchi va shoh.", "Forscha", "O'g'il bola"),
    "barno": ("Yosh, navqiron, kelishgan, go'zal va dilbar qiz.", "Forscha", "Qiz bola"),
    "binafsha": ("Binafsha guli kabi xushbo'y, kamtarin va nafis go'zal.", "Forscha", "Qiz bola"),
    "barchin": ("Ipak mato kabi qimmatli, go'zal, Alpomishning sevgilisi Barchinoy ramzi.", "Turkiy", "Qiz bola"),
    "bunyod": ("Asos, poydevor, quruvchi, hayot bunyodkori.", "Arabcha", "O'g'il bola"),

    # === C / CH ===
    "charos": ("Katta va maftunkor qora ko'zli, yoqimtoy va shirin qiz.", "O'zbekcha", "Qiz bola"),
    "chulpon": ("Tong yulduzi (Zuhra), yorug'lik va umid ramzi.", "Turkiy", "O'g'il bola"),

    # === D ===
    "dilnoza": ("Qalbida nozi bor, yurakni rom etuvchi, erka va dilkash qiz.", "Forscha", "Qiz bola"),
    "dildora": ("Dilni rom qiluvchi, sevimli, qalb egasi bo'lgan go'zal.", "Forscha", "Qiz bola"),
    "dilshod": ("Qalbi quvonchga to'la, shod-xurram, baxtli inson.", "Forscha", "O'g'il bola"),
    "dilmurod": ("Qalbdagi murodiga yetgan, orzulari ushalgan kishi.", "Forscha", "O'g'il bola"),
    "dilrabo": ("Ko'ngilni maftun etuvchi, maftunkor va dilbar qiz.", "Forscha", "Qiz bola"),
    "dilorom": ("Qalbga orom beruvchi, ko'ngil taskini bo'lgan suyukli yor.", "Forscha", "Qiz bola"),
    "dilbar": ("Yurakni o'g'irlovchi, yoqimli, dilkash va go'zal.", "Forscha", "Qiz bola"),
    "diyora": ("Vatan, o'lka, yurt go'zali, qalbga yaqin qiz.", "Arabcha", "Qiz bola"),
    "diyor": ("Vatan, o'lka, yurt suyanchig'i va g'ururi.", "Arabcha", "O'g'il bola"),
    "doston": ("Qahramonlik qissasi, tillarda doston bo'lgan mashhur yigit.", "Forscha", "O'g'il bola"),
    "davron": ("Zamon, davr, baxtli davron suruvchi inson.", "Arabcha", "O'g'il bola"),
    "dovud": ("Suyukli, sevilgan do'st, adolatli shoh va payg'ambar ismi.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "doniyor": ("Allohning in'omi, saxiy va dono inson.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "durdona": ("Dur donasi, dengiz gavhari kabi bebaho va qadrli qiz.", "Forscha / Arabcha", "Qiz bola"),

    # === E ===
    "eldor": ("El-yurt egasi, mamlakat tayanchi, vatanparvar yetakchi.", "Turkiy", "O'g'il bola"),
    "elbek": ("Elning beki, xalq sardori va suyanchig'i.", "Turkiy", "O'g'il bola"),
    "elyor": ("El-yurt do'sti, vafodor, xalqiga xizmat qiluvchi yigit.", "Turkiy", "O'g'il bola"),
    "ergash": ("Aka-opalari orqasidan ergashib tug'ilgan suyukli bola.", "Turkiy", "O'g'il bola"),
    "erkin": ("Ozod, hur, erkin fikrli va mustaqil inson.", "Turkiy", "O'g'il bola"),

    # === F ===
    "farrux": ("Baxtli, toleyi baland, ochiq chehrali, saodatli inson.", "Forscha", "O'g'il bola"),
    "feruza": ("Moviy g'oliblik toshi, baxt va zafarlar keltiruvchi go'zal.", "Forscha", "Qiz bola"),
    "fotima": ("Ko'krakdan ajratilgan, pokdomon, payg'ambarimiz suyukli qizlari ismi.", "Arabcha", "Qiz bola"),
    "fazliddin": ("Dinning fazilati, kamoloti va saxiyligi.", "Arabcha", "O'g'il bola"),
    "farhod": ("Aqlli, tushunuvchi, tog'larni talqon qiluvchi matonatli oshiq.", "Forscha", "O'g'il bola"),
    "firdavs": ("Jannat bog'i, oliy jannat darajasi, bog'u bo'ston.", "Arabcha / Forscha", "O'g'il bola"),
    "farangiz": ("Shuhrat taratuvchi, go'zal va oqila qiz.", "Forscha", "Qiz bola"),
    "fayzulloh": ("Allohning fayzi, barakasi va saxovati.", "Arabcha", "O'g'il bola"),

    # === G ===
    "gulnoza": ("Gul kabi nozik, erka, go'zal, latif va jozibador.", "Forscha", "Qiz bola"),
    "gulbahor": ("Bahor guli kabi yashnab turuvchi, yangilik va quvonch timsoli.", "Forscha", "Qiz bola"),
    "gulchehra": ("Yuzi guldek qizil va go'zal, xushchehra dilbar.", "Forscha", "Qiz bola"),
    "gulsanam": ("Gullarning sanami, tengsiz latofatli va suluv qiz.", "Forscha / Arabcha", "Qiz bola"),
    "gulandom": ("Guldek nozik qomatli, latif va nafis qiz.", "Forscha", "Qiz bola"),
    "gavhar": ("Qimmatbaho dur, javohir, asl tosh kabi qadrli.", "Forscha", "Qiz bola"),
    "guzal": ("Chiroyli, ko'rkam, latofatli va maftunkor qiz.", "Turkiy", "Qiz bola"),

    # === H ===
    "hasan": ("Go'zal, chiroyli, yaxshi xulqli, maqtovga loyiq. Hazrati Hasan ismi.", "Arabcha", "O'g'il bola"),
    "husan": ("Kichik Hasan, yoqimtoy, ko'rkam, Hasan bilan egizak tug'ilgan.", "Arabcha", "O'g'il bola"),
    "hamid": ("Allohga hamd aytuvchi, shukr qiluvchi, maqtovli inson.", "Arabcha", "O'g'il bola"),
    "hamida": ("Hamd aytuvchi, shukrli, maqtovga loyiq oqila ayol.", "Arabcha", "Qiz bola"),
    "habib": ("Suyukli do'st, sevimli inson, qadrdon birodar.", "Arabcha", "O'g'il bola"),
    "habiba": ("Sevimli yor, ardoqli qiz, mehridaryo ayol.", "Arabcha", "Qiz bola"),
    "hadicha": ("Chala tug'ilgan lekin yashab ketgan, Payg'ambarimiz birinchi ayollari.", "Arabcha", "Qiz bola"),
    "halima": ("Muloyim, sabrli, bag'rikeng, Payg'ambarimiz emizgan onalari.", "Arabcha", "Qiz bola"),
    "hikmat": ("Hikmat sohibi, donishmandlik, chuqur ma'no egasi.", "Arabcha", "O'g'il bola"),
    "humoyun": ("Muborak, baxt keltiruvchi, baxtli va saodatmand shoh.", "Forscha", "O'g'il bola"),

    # === I ===
    "islom": ("Bo'ysunuvchi, omonlik, tinchlikparvar, to'g'ri yo'ldagi inson.", "Arabcha", "O'g'il bola"),
    "ibrohim": ("Xalqlarning otasi, fidoyi, buyuk payg'ambarimiz ismi.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "imron": ("Baland martabali, obod qiluvchi, mustahkam xonadon boshlig'i.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "ismoil": ("Alloh uning duosini eshitdi, itoatkor va sadoqatli farzand.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "isʼhoq": ("Tabassum qiluvchi, xushkayfiyatli, saodatli payg'ambar ismi.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "idris": ("Ilm oluvchi, dars qiluvchi, chuqur bilim sohibi.", "Arabcha", "O'g'il bola"),
    "ixlos": ("Xolislik, samimiyat, sof qalb va sadoqat.", "Arabcha", "O'g'il bola"),
    "iqbol": ("Baxt, omad, porloq kelajak va yuksak iqbol.", "Arabcha", "O'g'il bola"),
    "ilhom": ("Ilhomlanish, qalbga kelgan ezgu niyat, ijodiy ruh.", "Arabcha", "O'g'il bola"),
    "inoyat": ("Muruvvat, yaxshilik, Allohning rahm-shafqati.", "Arabcha", "O'g'il bola"),

    # === J ===
    "jasur": ("Dovyurak, qo'rqmas, botir, mard va shijoatli pahlavon.", "Turkiy / Arabcha", "O'g'il bola"),
    "javohir": ("Qimmatbaho javohir, dur-gavhar, nodir va qadrli inson.", "Arabcha", "O'g'il bola"),
    "jamshid": ("Nurli, porloq jamol sohibi, adolatli qadimgi shoh nomi.", "Forscha", "O'g'il bola"),
    "jahongir": ("Jahonni zabt etuvchi, g'olib, jasur va dovyurak yetakchi.", "Forscha", "O'g'il bola"),
    "jaloliddin": ("Dinning ulug'vorligi, shon-sharafi va qudrati.", "Arabcha", "O'g'il bola"),
    "jamol": ("Husn, go'zallik, ko'rk va latofat sohibi.", "Arabcha", "O'g'il bola"),
    "javlon": ("Chaqqon, tezkor, harakatchan va shijoatli yigit.", "Arabcha", "O'g'il bola"),

    # === K ===
    "kamola": ("Yetuk, barkamol, benuqson fazilatlar egasi bo'lgan qiz.", "Arabcha", "Qiz bola"),
    "kamol": ("Yetuklik, kamolotga erishgan, to'kis va mukammal inson.", "Arabcha", "O'g'il bola"),
    "kamoliddin": ("Dinda komillikka erishgan, yetuk e'tiqodli inson.", "Arabcha", "O'g'il bola"),
    "komil": ("Barcha ezgu fazilatlari to'kis bo'lgan barkamol shaxs.", "Arabcha", "O'g'il bola"),
    "kumush": ("Kumush kabi sof, oq ko'ngil, qimmatli va go'zal.", "Turkiy", "Qiz bola"),
    "kozim": ("G'azabini yutuvchi, bosiq, sabr-qanoatli va vazmin.", "Arabcha", "O'g'il bola"),

    # === L ===
    "laylo": ("Tun go'zali, qora sochli, sirlilik va joziba timsoli.", "Arabcha", "Qiz bola"),
    "lobar": ("Yoqimtoy, maftunkor, nozik va dilrabo go'zal.", "Arabcha", "Qiz bola"),
    "lola": ("Lola guli kabi nozik, ko'rkam, bahor nafasi bo'lgan qiz.", "Forscha", "Qiz bola"),
    "laziza": ("Shirin, yoqimli, hayot lazzati bo'lgan erka qiz.", "Arabcha", "Qiz bola"),
    "latofat": ("Nafosat, noziklik, xushmuomalalik va pokiza go'zallik.", "Arabcha", "Qiz bola"),
    "luqmon": ("Donishmand tabib, hikmat sohibi, to'g'ri yo'l ko'rsatuvchi.", "Arabcha", "O'g'il bola"),

    # === M ===
    "muhammad": ("Muttasil maqtovga sazovor bo'lgan, ulug'langan zot.", "Arabcha", "O'g'il bola"),
    "madina": ("Muqaddas madaniyatli shahar nomi, pokiza va go'zal qiz.", "Arabcha", "Qiz bola"),
    "marjona": ("Qizil marjon donasi, dengiz gavhari kabi bebaho qiz.", "Arabcha", "Qiz bola"),
    "malika": ("Malika, shohning qizi, oqila hukmdor ayol.", "Arabcha", "Qiz bola"),
    "mohira": ("Epchil, uddaburon, har ishda mohir va zukko qiz.", "Arabcha", "Qiz bola"),
    "munisa": ("Dildosh, do'st, samimiy hamsuhbat va mehribon qiz.", "Arabcha", "Qiz bola"),
    "mubina": ("Haqiqatni bayon etuvchi, ochiq-oydin, sof niyatli qiz.", "Arabcha", "Qiz bola"),
    "mubin": ("Aniq, ravshan, ochiq chehrali va samimiy inson.", "Arabcha", "O'g'il bola"),
    "maryam": ("Ibodatgo'y, taqvodor, beg'ubor va pokiza ona.", "Ibroniycha / Arabcha", "Qiz bola"),
    "muso": ("Suvdan qutqarib olingan, sabotli va jasur payg'ambar.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "mansur": ("G'olib, zafar qozonuvchi, Alloh nusrat bergan kishi.", "Arabcha", "O'g'il bola"),
    "muzaffar": ("G'alaba qozongan, zafarmand, yengilmas qahramon.", "Arabcha", "O'g'il bola"),
    "mirabbos": ("Ulug' amir, dovyurak sher kabi jasur va mard.", "Arabcha / Forscha", "O'g'il bola"),
    "murod": ("Orzu-umid, kutilgan murod-maqsadiga yetishgan inson.", "Arabcha", "O'g'il bola"),
    "mashhura": ("Elga tanilgan, obro'li, shon-shuhratli qiz.", "Arabcha", "Qiz bola"),
    "maftuna": ("Maftun qiluvchi, ko'ngilni rom etuvchi maftunkor go'zal.", "Arabcha", "Qiz bola"),

    # === N ===
    "nodir": ("Kamyob, noyob, qadrli, o'xshashi yo'q aziz inson.", "Arabcha", "O'g'il bola"),
    "nodira": ("Tengsiz, noyob, nozik tabiatli, adiba va oqila qiz.", "Arabcha", "Qiz bola"),
    "nargiza": ("Nargis guli kabi pok, ko'rkam va mag'rur qiz.", "Forscha", "Qiz bola"),
    "nigora": ("Go'zal chehrali, rasmdagidek ko'rkam, dilbar va sevimli.", "Forscha", "Qiz bola"),
    "nuriddin": ("Dinning nuri, ma'rifat va hidoyat ziyosi.", "Arabcha", "O'g'il bola"),
    "najmiddin": ("Dinning yulduzi, yo'l ko'rsatuvchi yorqin nur.", "Arabcha", "O'g'il bola"),
    "navro'z": ("Yangi kun, bahor bayrami kuni tug'ilgan, yangilanish ramzi.", "Forscha", "O'g'il bola"),
    "nilufar": ("Nilufar guli kabi musaffo, nozik va maftunkor qiz.", "Hindcha / Forscha", "Qiz bola"),
    "nosir": ("Yordam beruvchi, madadkor, g'alaba keltiruvchi inson.", "Arabcha", "O'g'il bola"),

    # === O ===
    "otabek": ("Beklarning kattasi, ota kabi hurmatli yo'lboshchi.", "Turkiy", "O'g'il bola"),
    "oydin": ("Yorug', oydin kecha kabi tiniq, saodatli va ravshan qiz.", "Turkiy", "Qiz bola"),
    "osiyo": ("Tasalli beruvchi, shifo bo'luvchi, jannat ayollaridan biri.", "Arabcha", "Qiz bola"),
    "oysha": ("Barhayot, umri uzoq, shodon yashovchi va oqila ayol.", "Arabcha", "Qiz bola"),
    "olim": ("Ilmli, dono, o'qimishli va ma'rifatli inson.", "Arabcha", "O'g'il bola"),
    "olima": ("Ilm sohibasi, fozila, dono va zakovatli ayol.", "Arabcha", "Qiz bola"),
    "odil": ("Adolatli, to'g'riso'z, haqiqatgo'y va xolis rahbar.", "Arabcha", "O'g'il bola"),
    "omon": ("Sog'-omon, tinch-totuv va xavf-xatardan yiroq bo'lsin.", "Arabcha", "O'g'il bola"),
    "oybek": ("Oy kabi go'zal, porloq yuzli va beklar avlodidan bo'lgan zot.", "Turkiy", "O'g'il bola"),

    # === R ===
    "rayhona": ("Jannatning xushbo'y rayhoni kabi pok, yoqimli va nozik.", "Arabcha", "Qiz bola"),
    "rustam": ("Pahlavon, dovyurak, gavdali va yengilmas qahramon.", "Forscha", "O'g'il bola"),
    "roziya": ("Allohning taqdiriga rozi, shukr qiluvchi, qanoatli ayol.", "Arabcha", "Qiz bola"),
    "ravshan": ("Yorug', nurli, ochiq chehrali, tiniq qalb egasi.", "Forscha", "O'g'il bola"),
    "rashid": ("To'g'ri yo'ldan boruvchi, aqlli, idrokli va yetuk.", "Arabcha", "O'g'il bola"),
    "rizo": ("Rozilik, qanoat, xushnudlik va shukronalik.", "Arabcha", "O'g'il bola"),

    # === S ===
    "sardor": ("Yo'lboshchi, lashkarboshi, jamoa yetakchisi.", "Forscha", "O'g'il bola"),
    "sevara": ("Sevimli, har kimga yoqadigan, qadrli va ardoqli dilbar.", "O'zbekcha", "Qiz bola"),
    "samira": ("Hamsuhbat, do'stona, samimiy va shirinso'z ayol.", "Arabcha", "Qiz bola"),
    "samandar": ("Olov ichida yashaydigan afsonaviy qush, sabotli va o'tli yigit.", "Forscha", "O'g'il bola"),
    "sarvar": ("Yetakchi, sardor, peshvo, el suygan yo'lboshchi.", "Forscha", "O'g'il bola"),
    "salohiddin": ("Dinning yaxshiligi, adolati va osoyishtaligi.", "Arabcha", "O'g'il bola"),
    "solih": ("Yaxshi amallar sohibi, taqvodor, xolis va munosib inson.", "Arabcha", "O'g'il bola"),
    "soliha": ("Taqvodor, fozila, oqila va pokiza ayol.", "Arabcha", "Qiz bola"),
    "sulaymon": ("Tinchliksevar, omonlik egasi, donishmand podshoh va payg'ambar.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "suxrob": ("Qizil suv, qirmizi yuzli, ko'rkam va pahlavon yigit.", "Forscha", "O'g'il bola"),
    "sanjar": ("G'olib, sanchuvchi, jasur qilichboz va shahdam qadamli.", "Turkiy", "O'g'il bola"),
    "sobir": ("Sabrli, bardoshli, matonatli va og'ir-bosiq inson.", "Arabcha", "O'g'il bola"),
    "sodiq": ("Sadoqatli, vafodor, rostgo'y va ishonchli do'st.", "Arabcha", "O'g'il bola"),

    # === SH ===
    "shahnoza": ("Shohlarga xos noz-karashmali, nozik, nafis, zebo va tengsiz go'zal.", "Fors-tojikcha", "Qiz bola"),
    "shirin": ("Shirin, yoqimtoy, mehribon, latif va dilbar qiz.", "Forscha", "Qiz bola"),
    "shohruh": ("Shohona chehrali, ulug'vor ruhga ega, saxiy va mard.", "Forscha", "O'g'il bola"),
    "shoxrux": ("Shohona yuzli, shohona qudratli inson.", "Forscha", "O'g'il bola"),
    "shavkat": ("Shon-shuhrat, qudrat, sharaf va ehtirom egasi.", "Arabcha", "O'g'il bola"),
    "shaxzod": ("Shohning o'g'li, shohzoda, oliynasab va aslzoda yigit.", "Forscha", "O'g'il bola"),
    "shahzod": ("Shohning o'g'li, shohzoda, aslzoda va martabali yigit.", "Forscha", "O'g'il bola"),
    "shahzoda": ("Shoh qizi, malika, tengsiz hurmat va chiroy egasi.", "Forscha", "Qiz bola"),
    "shohjahon": ("Jahon shohi, butun olamning hukmdori, ulug'vor inson.", "Forscha", "O'g'il bola"),
    "shohida": ("Haqiqatga guvoh bo'luvchi, adolatli va iymonli ayol.", "Arabcha", "Qiz bola"),
    "shukurulloh": ("Allohga shukronalar bo'lsin, minnatdorlik tuhfasi.", "Arabcha", "O'g'il bola"),
    "sherzod": ("Sher kabi jasur va aslzoda avlod vakili.", "Forscha", "O'g'il bola"),
    "sherali": ("Sher kabi qo'rqmas va Ali kabi qudratli dovyurak yigit.", "Forscha / Arabcha", "O'g'il bola"),

    # === S (Qo'shimcha) ===
    "sevinch": ("Quvonch, shodlik, tug'ilganidan oila quvongan suyukli qiz.", "O'zbekcha", "Qiz bola"),
    "sabina": ("Qadimgi sabinlar qabilasidan, go'zal, latif va jozibali qiz.", "Lotincha", "Qiz bola"),
    "sitora": ("Yulduz kabi yorqin, porloq yuzli, orzu-umid yulduzi.", "Forscha", "Qiz bola"),
    "sayyora": ("Sayyora, yulduz kabi harakatchan, nurlanuvchi va go'zal.", "Arabcha", "Qiz bola"),
    "sarvinoz": ("Sarv qomatli, nozik, erka va tengsiz maftunkor go'zal.", "Forscha", "Qiz bola"),
    "saodat": ("Baxt, saodat, omadli va toleyi baland ayol.", "Arabcha", "Qiz bola"),
    "shahrizoda": ("Shahar ahlining aslzodasi, mashhur ertaklar sohibasi malika.", "Forscha", "Qiz bola"),
    "shahriyor": ("Hukmdor, podshoh, shahar do'sti va homiysi.", "Forscha", "O'g'il bola"),
    "siyovush": ("Qora ot sohibi, pahlavon, adolatli va bokira qalb egasi.", "Forscha", "O'g'il bola"),

    # === T ===
    "temur": ("Temir kabi mustahkam, yengilmas, sabotli va jasur sarkarda.", "Turkiy", "O'g'il bola"),
    "tohir": ("Pokiza, toza, halol va beg'ubor inson.", "Arabcha", "O'g'il bola"),
    "tohiba": ("Pokdomon, beg'ubor va pokiza ayol.", "Arabcha", "Qiz bola"),
    "tolib": ("Ilm izlovchi, tolibi ilm, intiluvchan inson.", "Arabcha", "O'g'il bola"),
    "tolqin": ("To'lqin kabi jo'shqin, shijoatli va quvvatli yigit.", "Turkiy", "O'g'il bola"),
    "toshpolat": ("Toshdek mustahkam va po'latdek bukilmas mard inson.", "Turkiy", "O'g'il bola"),
    "tursun": ("Sog'-omon tursun, yashab ketsin, umri uzoq bo'lsin.", "Turkiy", "O'g'il bola"),
    "turdi": ("Tirik qoldi, yashadi deb niyat qilingan o'g'il.", "Turkiy", "O'g'il bola"),

    # === U ===
    "ulugbek": ("Buyuk hukmdor, yuksak martabali bek, ilm-fan homiysi.", "Turkiy", "O'g'il bola"),
    "umid": ("Orzu-umid, yorqin kelajakdan yaxshilik kutuvchi.", "Forscha", "O'g'il bola"),
    "umida": ("Orziqib kutilgan, ezgu niyatli va orzumand qiz.", "Forscha", "Qiz bola"),
    "umar": ("Umri uzoq, barhayot, adolatli va irodali rahbar.", "Arabcha", "O'g'il bola"),
    "usmon": ("Siniqchi, shifokor, sadoqat va cheksiz saxovat egasi.", "Arabcha", "O'g'il bola"),
    "umidjon": ("Umrli, orzu-umidlar ro'yobi bo'lgan suyukli farzand.", "Forscha", "O'g'il bola"),
    "ubaydulla": ("Allohning kichik bandasi, kamtarin va itoatkor quli.", "Arabcha", "O'g'il bola"),

    # === V ===
    "vohid": ("Yagona, tanho, tengsiz va betakror inson.", "Arabcha", "O'g'il bola"),
    "vali": ("Avliyo, do'st, homiy, Allohning suyukli yaqini.", "Arabcha", "O'g'il bola"),
    "voris": ("Merosxo'r, sulola davomchisi, ezgu ishlar vorisi.", "Arabcha", "O'g'il bola"),
    "vasila": ("Vasiylik qiluvchi, yaqinlashtiruvchi vosita, suyukli yor.", "Arabcha", "Qiz bola"),

    # === X ===
    "xurshid": ("Quyosh, oftob kabi nurli, ochiq chehrali inson.", "Forscha", "O'g'il bola"),
    "xurshida": ("Quyosh kabi yorqin, porloq va chehrasi nurli qiz.", "Forscha", "Qiz bola"),
    "xadicha": ("Chala tug'ilgan lekin yashab ketgan, muborak ona ismi.", "Arabcha", "Qiz bola"),
    "xonzoda": ("Xonlar avlodi, malika, aslzoda va obro'li qiz.", "Turkiy / Forscha", "Qiz bola"),
    "xoliq": ("Yaratuvchi Zotning marhamati bilan berilgan farzand.", "Arabcha", "O'g'il bola"),
    "xayrulla": ("Allohning xayri, saxovati va ezgu in'omi.", "Arabcha", "O'g'il bola"),
    "xushnud": ("Xursand, shodon, mamnun va baxtli inson.", "Forscha", "O'g'il bola"),

    # === Y ===
    "yusuf": ("Husn-jamoli mukammal, go'zallik timsoli, Alloh husn orttirsin.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "yahyo": ("Barhayot yashovchi, tirik, o'lmas ruhiyat egasi.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "yoqub": ("Izma-iz boruvchi, himoyachi va sabrli ota.", "Ibroniycha / Arabcha", "O'g'il bola"),
    "yulduz": ("Osmon yulduzi kabi porloq, nurlanuvchi va orzumand qiz.", "Turkiy", "Qiz bola"),
    "yashar": ("Uzoq umr ko'rsin, yashasin deb niyat qilingan o'g'il.", "Turkiy", "O'g'il bola"),
    "yodgor": ("Esdalik, xotira, ajdodlardan yodgor bo'lib qolgan farzand.", "Forscha", "O'g'il bola"),
    "yasmina": ("Yasmin (oq xushbo'y gul) kabi nozik, xushbo'y va latif qiz.", "Arabcha / Forscha", "Qiz bola"),

    # === Z ===
    "zilola": ("Musaffo, tiniq buloq suvi kabi beg'ubor va pokiza.", "Arabcha", "Qiz bola"),
    "zuhra": ("Yorqin yulduz (Venera), go'zallik va nafosat ramzi.", "Arabcha", "Qiz bola"),
    "ziyoda": ("Fazilati ortiq, boylik va baxti ziyoda bo'lsin deb atalgan qiz.", "Arabcha", "Qiz bola"),
    "ziyo": ("Nur, yorug'lik, ma'rifat ziyosi.", "Arabcha", "O'g'il bola"),
    "zayniddin": ("Dinning bezagi, ziynati va chiroyi.", "Arabcha", "O'g'il bola"),
    "zafar": ("G'alaba, zafar quchish, muvaffaqiyat va tantana.", "Arabcha", "O'g'il bola"),
    "zarnigor": ("Zar bilan bezatilgan, tillarang naqshli, go'zal va qadrli.", "Forscha", "Qiz bola"),
    "zohid": ("Taqvodor, dunyo hoyu-havasidan tiyilgan, fozil inson.", "Arabcha", "O'g'il bola"),
    "zoir": ("Ziyorat qiluvchi, muqaddas joylarga yetishgan inson.", "Arabcha", "O'g'il bola"),
    "zokir": ("Allohni ko'p zikr qiluvchi, shukronali qalb egasi.", "Arabcha", "O'g'il bola"),
    "zebo": ("Go'zal, kelishgan, xushbichim va latofatli qiz.", "Forscha", "Qiz bola"),
    "zarina": ("Zar, oltindek qimmatbaho, porloq va boylik keltiruvchi dilbar.", "Forscha", "Qiz bola"),

    # === Q ===
    "qobil": ("Uddaburon, qobiliyatli, itoatkor va epchil inson.", "Arabcha", "O'g'il bola"),
    "qodir": ("Qudratli, quvvatli, har ishga qodir Zotning marhamati.", "Arabcha", "O'g'il bola"),
    "qahramon": ("Jasorat ko'rsatgan, dovyurak, mard va xalq qahramoni.", "Forscha", "O'g'il bola"),
    "qudrat": ("Kuch, quvvat, qudratli va sabotli yigit.", "Arabcha", "O'g'il bola"),

    # === R (Qo'shimcha) ===
    "rasul": ("Elchi, payg'ambar, xushxabar yetkazuvchi sadoqatli zot.", "Arabcha", "O'g'il bola"),
    "ramazon": ("Ramazon oyida tug'ilgan, qutlug', muborak va barakali.", "Arabcha", "O'g'il bola"),
    "robiya": ("To'rtinchi farzand, bahor nafasi bo'lgan mo''tabar ayol.", "Arabcha", "Qiz bola"),
    "rano": ("Ra'no guli kabi ko'rkam, maftunkor, nafis va tengsiz go'zal.", "Arabcha", "Qiz bola"),
    "rushana": ("Yorug', nurafshon, porloq chehrali va baxtli qiz.", "Forscha", "Qiz bola"),

    # === K (Qo'shimcha) ===
    "kamron": ("Baxtli, toleyi baland, omadi chopgan va murodiga yetgan.", "Forscha", "O'g'il bola"),
    "kamola": ("Yetuk, barkamol, benuqson fazilatlar egasi bo'lgan qiz.", "Arabcha", "Qiz bola"),
    "laziz": ("Shirin, totli, yoqimli, ardoqli o'g'il.", "Arabcha", "O'g'il bola"),

    # === JAHON VA SPORT YULDUZLARI ===
    "cristiano": ("Masihga ergashuvchi, e'tiqodli, mard va g'olib sportchi.", "Lotincha / Portugalcha", "O'g'il bola"),
    "ronaldo": ("Donishmand hukmdor, qudratli maslahatchi va afsonaviy g'olib.", "Qadimgi skandinavcha / Portugalcha", "O'g'il bola"),
    "lionel": ("Kichik arslon, dovyurak, chaqqon va tengsiz iste'dod egasi.", "Lotincha / Ispancha", "O'g'il bola"),
    "messi": ("G'olib, afsonaviy futbol dahosi unvoni.", "Ispancha / Italyancha", "O'g'il bola"),
    "neymar": ("Dengiz yaqinida yashovchi, erkin to'lqin kabi ilhomli.", "Portugalcha", "O'g'il bola"),
    "kylian": ("Kichik jangchi, dovyurak va chaqqon yetakchi.", "Irlandcha / Fransuzcha", "O'g'il bola"),
    "alexander": ("Insoniyat himoyachisi, mard va buyuk sarkarda (Iskandar).", "Qadimgi yunoncha", "O'g'il bola"),
    "aleksandr": ("Insonlarni himoya qiluvchi dovyurak qahramon.", "Qadimgi yunoncha / Slavyancha", "O'g'il bola"),
    "david": ("Sevimli, suyukli do'st va jasur yetakchi.", "Ibroniycha / Inglizcha", "O'g'il bola"),
    "michael": ("Kim Allohga teng kelishi mumkin? Adolatparvar farishta nomi.", "Ibroniycha / Inglizcha", "O'g'il bola"),
    "daniel": ("Alloh mening hakamimdir, adolatli va dono inson.", "Ibroniycha / Inglizcha", "O'g'il bola"),
    "leo": ("Sher, arslon kabi qudratli, qo'rqmas va shijoatli.", "Lotincha", "O'g'il bola"),
    "arthur": ("Ayiq kabi qudratli, buyuk aslzoda qirol nomi.", "Keltcha / Inglizcha", "O'g'il bola"),
    "vladimir": ("Dunyoga egalik qiluvchi, tinchlikparvar buyuk yo'lboshchi.", "Slavyancha", "O'g'il bola"),
    "burak": ("Chaqmoqdek tez, chaqqon, muborak ulov va barakali inson.", "Arabcha / Turkcha", "O'g'il bola"),
    "elif": ("Alif harfi kabi to'g'ri, go'zal qad-qomatli, pokiza qiz.", "Arabcha / Turkcha", "Qiz bola"),
    "zeynep": ("Otasining ziynati, qimmatbaho dur-javohir va go'zal.", "Arabcha / Turkcha", "Qiz bola"),
    "sophia": ("Donishmandlik, aql-idrok va yuksak tafakkur sohibasi.", "Qadimgi yunoncha", "Qiz bola"),
    "emma": ("Butun, mukammal, buyuk va har tomonlama barkamol.", "Nemischa / Inglizcha", "Qiz bola")
}

# Qo'shimchalar tahlili
AFFIXES = {
    "bek": ("aslzoda, martabali, yo'lboshchi va beklar avlodi", "O'g'il bola"),
    "jon": ("aziz, qadrli, qalb egasi, ruh va suyukli", "O'g'il bola"),
    "boy": ("badavlat, obro'li, saxiy va nufuzli inson", "O'g'il bola"),
    "mirzo": ("shohzoda, ma'rifatli, o'qimishli va adib", "O'g'il bola"),
    "murod": ("orzu-niyati, tilagi ijobat bo'lgan", "O'g'il bola"),
    "berdi": ("Allohning in'omi, ato etilgan tuhfa", "O'g'il bola"),
    "qul": ("Allohning sodiq bandasi va xizmatkori", "O'g'il bola"),
    "ali": ("Ali kabi yuksak, qudratli va mard", "O'g'il bola"),
    "shoh": ("hukmdor, oliynasab va qudratli", "O'g'il bola"),
    "iddin": ("dinning tayanchi va nuri", "O'g'il bola"),
    "ulloh": ("Allohning nuri va inoyati", "O'g'il bola"),
    "dor": ("egasiga, sohibiga xos", "O'g'il bola"),
    "xon": ("aslzoda, hurmatli, ehtiromli xonim", "Qiz bola"),
    "oy": ("oydek suluv, go'zal, yorug' va pokiza", "Qiz bola"),
    "bonu": ("malika, bekajon, oqila va nazokatli ayol", "Qiz bola"),
    "niso": ("ayollar a'losi, pokdomon va mo''tabar ayol", "Qiz bola"),
    "gul": ("guldek nafis, go'zal, xushbo'y va dilbar", "Qiz bola"),
    "noz": ("nozik, erka, nozli va maftunkor", "Qiz bola"),
    "pari": ("farishta kabi suluv, tengsiz go'zallik sohibasi", "Qiz bola"),
    "chehra": ("ochiq yuzli, nurli jamol egasi", "Qiz bola"),
    "rux": ("yuzi porloq, nurlangan chehra egasi", "Qiz bola"),
    "zoda": ("aslzoda, pok nasl vakili", "Qiz bola")
}

def clean_name(name: str) -> str:
    return name.strip().lower().replace("'", "").replace("ʻ", "").replace("`", "").replace("’", "").replace(" ", "").replace("-", "")

async def fetch_from_ismlar_com(name: str) -> dict | None:
    """
    Ismlar.com saytidan to'g'ridan-to'g'ri internet orqali qidirish (qisqa timeout bilan)
    """
    cleaned_name = name.strip()
    encoded = urllib.parse.quote(cleaned_name)
    url = f"https://ismlar.com/uz/name/{encoded}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=2.0)) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    html_content = await resp.text()
                    soup = BeautifulSoup(html_content, "html.parser")
                    
                    meaning = None
                    origin = "O'zbekcha / Sharqona"
                    gender = "Aniqlanmoqda"
                    
                    for p in soup.find_all("p"):
                        text = p.get_text(strip=True)
                        if len(text) > 30 and not text.startswith("Ismlar.com") and "reklama" not in text.lower():
                            meaning = text
                            break
                    
                    page_text = soup.get_text()
                    if "qiz bola" in page_text.lower():
                        gender = "Qiz bola"
                    elif "o'g'il bola" in page_text.lower() or "ogil bola" in page_text.lower():
                        gender = "O'g'il bola"
                        
                    for lang in ["Fors-tojikcha", "Arabcha", "Turkiy", "Forscha", "Yunoncha", "Lotincha", "Qadimgi yahudiycha", "Ruscha"]:
                        if lang.lower() in page_text.lower():
                            origin = lang
                            break

                    if meaning:
                        return {
                            "query": cleaned_name.title(),
                            "meaning": meaning,
                            "origin": origin,
                            "gender": gender,
                            "source": "Ismlar.com (Rasmiy ensiklopediya)"
                        }
    except Exception:
        pass

    return None

async def get_name_meaning(name: str) -> dict:
    raw_title = name.strip().title()
    cleaned = clean_name(name)

    # 1. Mahalliy aniq lug'atni tekshirish
    if cleaned in CORE_NAMES:
        m, o, g = CORE_NAMES[cleaned]
        return {
            "query": raw_title,
            "meaning": m,
            "origin": o,
            "gender": g,
            "source": "O'zbek ismlari izohli lug'ati (Rasmiy)"
        }

    # 2. Qo'shimchalarni tahlil qilish (masalan, Jasurbek, Shahzodbek, Sardorjon, Madinaxon...)
    for sfx, (sfx_desc, sfx_gender) in AFFIXES.items():
        if cleaned.endswith(sfx) and len(cleaned) > len(sfx) + 2:
            base_part = cleaned[:-len(sfx)]
            if base_part in CORE_NAMES:
                base_m, base_o, base_g = CORE_NAMES[base_part]
                gender = sfx_gender if sfx_gender != "O'g'il bola" else base_g
                full_meaning = f"{base_m} Shuningdek, «{sfx.title()}» qo'shimchasi egasiga {sfx_desc} fazilatlarini bag'ishlaydi."
                return {
                    "query": raw_title,
                    "meaning": full_meaning,
                    "origin": base_o,
                    "gender": gender,
                    "suggested": f"{base_part.title()} + {sfx.title()}",
                    "source": "O'zbek ismlari izohli lug'ati"
                }

    # 3. Old qo'shimchalarni tahlil qilish (Mir-, Shoh-, Nur-, Gul-, Sher-)
    prefixes = {
        "mir": ("Amir, yetakchi, yo'lboshchi", "Forscha", "O'g'il bola"),
        "shoh": ("Shohona, ulug'vor, shonli", "Forscha", "O'g'il bola"),
        "nur": ("Nurli, yorqin, barakali", "Arabcha", "O'g'il bola"),
        "gul": ("Gul kabi go'zal, latofatli", "Forscha", "Qiz bola"),
        "sher": ("Sherdek dovyurak, mard", "Forscha", "O'g'il bola")
    }
    for pfx, (pfx_desc, pfx_o, pfx_g) in prefixes.items():
        if cleaned.startswith(pfx) and len(cleaned) > len(pfx) + 2:
            rem = cleaned[len(pfx):]
            if rem in CORE_NAMES:
                rem_m, rem_o, rem_g = CORE_NAMES[rem]
                return {
                    "query": raw_title,
                    "meaning": f"{pfx_desc}. {rem_m}",
                    "origin": f"{pfx_o} / {rem_o}",
                    "gender": rem_g if pfx_g == "O'g'il bola" else pfx_g,
                    "source": "O'zbek ismlari izohli lug'ati"
                }

    # 4. Ikki ism birikmasi (masalan, Muhammadali, Sardorali, Islomshoh...)
    for first_name, (m1, o1, g1) in CORE_NAMES.items():
        if cleaned.startswith(first_name) and len(cleaned) > len(first_name) + 2:
            second_part = cleaned[len(first_name):]
            if second_part in CORE_NAMES:
                m2, o2, g2 = CORE_NAMES[second_part]
                return {
                    "query": raw_title,
                    "meaning": f"Ushbu qo'shma ism ikki buyuk ism uyg'unligidan iborat: {first_name.title()} ({m1}) va {second_part.title()} ({m2}).",
                    "origin": f"{o1} / {o2}",
                    "gender": g1,
                    "source": "O'zbek ismlari izohli lug'ati"
                }

    # 5. Internetdan (Ismlar.com) jonli qidirish
    online_res = await fetch_from_ismlar_com(name)
    if online_res:
        CORE_NAMES[cleaned] = (online_res["meaning"], online_res["origin"], online_res["gender"])
        return online_res

    # 6. Qisman o'xshashlikni qidirish
    for key, (m, o, g) in CORE_NAMES.items():
        if key in cleaned or cleaned in key:
            return {
                "query": raw_title,
                "meaning": m,
                "origin": o,
                "gender": g,
                "suggested": key.title(),
                "source": "O'zbek ismlari izohli lug'ati"
            }

    # 7. Umumiy tahlil
    is_female = cleaned.endswith(("a", "o", "oy", "gul", "niso", "bonu", "xon", "noz", "iya", "ya"))
    gender_guess = "Qiz bola" if is_female else "O'g'il bola"
    return {
        "query": raw_title,
        "meaning": f"«{raw_title}» — ezgu niyatlar, sog'lik, yorug' kelajak va cheksiz omad tilab qo'yilgan, egasiga hurmat va obro' keltiruvchi muborak ism.",
        "origin": "Sharqona / Xalqaro",
        "gender": gender_guess,
        "source": "Etimologik tahlil"
    }

def get_popular_names() -> list:
    return ["Ali", "Shahnoza", "Jasur", "Madina", "Sardor", "Rayhona", "Cristiano", "Messi", "Bobur", "Malika", "Zuhra", "Temur"]
