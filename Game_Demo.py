"""
-*- Version: 0.0.1.Beta               -*-
-*- Environment: python 3.8 preferred -*-
-*- coding: utf-8                     -*-
-*- By Howard Holo (Hongru He)        -*-
Jan 24, 2021

注：此为对原版本进行整合后的script，以便于传阅。将部分class与package重写为函数形式。
原有class：
Character，记录角色的状态。本版本中构造函数放置于set_pool_character()，以pd.dataframe形式记录。

原有其他py文件（和package）：
AiCards，AI的决策方法与具体AI策略，本版本中拆分到field_montecarlo，field_AIdeploy中。
Field，与每局的战场有关的函数。本版本中拆分整合为若干field_开头的函数。
TextSource，文本资源。包括各类名称、以及剧情文本。本版本中拆分为introduction, end函数，以及全局变量中。
"""

import time
import random
import pandas as pd     # 导入pandas库是因为pandas输出表格更美观

pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)
pd.set_option('display.unicode.east_asian_width', True)


"""
全局资源。按理说应该单独写在一个甚至多个数据库里的，但考虑到运行方便放在了一起。
notes：python和C++最大的区别在于，python没有main是逐级运行的。
"""
field_pool = ["营地", "巴比伦墙", "禹峡", "博卓卡维亚"]
field_sum_pl = [[1,2,3,4,5,6,7,8,9,10],[],[],[]]        # [0] 是未上场人物编号
field_sum_ai = [[1,2,3,4,5,6,7,8,9,10],[],[],[]]
job_pool = ["V", "D", "R", "S"]
name_pool = ["Amiya", "Lumen", "Xiaoyu", "Serpent", "Shira", "Holo", "Abigail", "Fubuki", "Ark", "Cuora",
             "Gumu", "Siege", "Rosa", "Rosso", "Platinum", "Corona", "Myrtle", "Poca", "Red", "Metero",
             "Kross", "Kiki", "Kami", "George", "Ceobe", "Nearl", "Pearl", "Leizy", "Jessica", "Julia",
             "Sora", "Lapland", "Texas", "Gavir", "Tianmin", "Savage", "Perfume", "Night", "Shamaren", "Grave",
             "Kal'tish", "Nir", "Silence", "Beagle", "Melle", "Mousse", "Frost", "Nova", "Leaf", "Myrh",
             "Ansel", "Gavial", "Therm", "Uta", "Ambie", "Amber", "Swam", "Steven", "Sesa", "Cleve",
             "Estella", "Matoi", "Maru", "Honoka", "Chika", "Dober", "Cutter", "Yuki", "You", "Kotori",
             "Umi", "Nozomi", "Eli", "Nico", "Hanayo", "Makki", "Rico", "Hana", "Yoshiko", "Ruby",
             "Dia", "Kanan", "Mary", "Coco", "Ver", "May", "Durnar", "Matter", "Horn", "Sussu",
             "Poco", "Deep", "Grevy", "Haze", "Gitano", "Shaw", "Skadi", "Ethan", "Popca", "Cardy"]
recon_list = [False, False, False, False, False,
              False, False, False, False, False]


"""
角色人物创建
设置四类职业：Vanguard先锋, Defender护卫, Ranger突袭, Sniper狙击。VD主近战，RS主远程。
每个职业有特殊优势。V高攻高机动；D高防高生命；R高机动且攻击手段多样；S高攻。
对每个设置如下属性：生命、防御、近战、远程、命中率、机动。
"""
def set_pool_character():
    # task 1: 确定不同rank的人数，通过多项分布获取。
    # 经证明，总体rank星均值约为20，标准差约为2
    rank_used = 0
    count = 0
    while (rank_used < 18 or rank_used > 22):
        count += 1
        rank_used = 0
        num_ranki = [0,0,0,0]
        for i in range(10):
            rank_seed = random.uniform(0, 100)
            if (rank_seed <= 20):
                rank_used += 3
                num_ranki[3] += 1
            elif (rank_seed <= 80):
                rank_used += 2
                num_ranki[2] += 1
            else:
                rank_used += 1
                num_ranki[1] += 1

        # 理论上还真能这么多次还不出结果。
        if (count > 1000000):
            num_ranki[3], num_ranki[2], num_ranki[1] = 3, 4, 3
            break

    # task 2: 按照星级设置角色
    name_glass = random.sample(name_pool, 10)
    count = 0
    charpool = []
    for i in range(1, 4, 1):
        for n in range(num_ranki[i]):
            # 选择职业
            job = random.sample(job_pool, 1); job = job[0]

            # 职业基础面板定义
            if(job == "V"):
                hp = 200; armor = 20; melee = 50; remote = 0
            if(job == "D"):
                hp = 220; armor = 30; melee = 30; remote = 0
            if(job == "R"):
                hp = 170; armor = 10; melee = 40; remote = 50
            if (job == "S"):
                hp = 170; armor = 5; melee = 20; remote = 60

            # 角色名称选取
            name = name_glass[count]
            count += 1

            # 角色星级确定，并根据星级调整基础面板
            rank = i; rk = rank
            while(rk != 1):
                if (job == "V"):
                    hp += 10; armor += 2; melee += 7; remote += 5
                if (job == "D"):
                    hp += 15; armor += 5; melee += 3; remote += 1
                if (job == "R"):
                    hp += 12; armor += 2; melee += 4; remote += 5
                if (job == "S"):
                    hp += 8; armor += 1; melee += 2; remote += 6

                rk -= 1

            # 角色随机化
            hp += random.uniform(0, 4)
            armor += random.uniform(0, 4)
            melee += random.uniform(0, 4)
            remote += random.uniform(0, 4)

            # 角色状态
            status = True
            charpool.append([count, name, job, rank, int(hp), int(armor), int(melee), int(remote), status])
    return charpool


"""
流程：
初始化与导入
（可跳过）教学
正式游戏（创建人物池、解锁情报、选择战场、选择出击人物、选择战术、结算）
结局

术语表：
战役（Battle），即整局游戏。
战场（Field），游戏中争夺的焦点。共有3个战场，玩家要尽可能在3个战场取得胜利。
回合（Round），一个回合中两个玩家各执行一次解锁情报、选择战场、选择出击人物、选择战术流程。按照剧情，游玩玩家默认为后手。
"""
def introduction():
    text_in = [
        "收到请求，正在确认通讯……", "通讯建立……", "身份确认完成，已确认访问权限为：T0……",
        "解析完成，开始通讯……", "……", "“议长大人。”", "“现在情况非常危急，我们不得不请求您下达指示。”",
        "“我知道，向议长大人请求军事指令会让您感到为难，可如今我们别无他法。”",
        "“联军已经将我们逼到了菲尔德区域，现在我们死守着巴比伦墙、禹峡和博卓卡维亚三个地方。”", "“联军要是攻占了菲尔德的这三个地方，我们彻底完了。”",
        "“议长大人，现在我们还有10位干员率领着他们的小队。\n”请您向他们下达作战指示，告诉他们该前往何处。\n”战斗由他们完成。”",
        "“生死存亡，在此一役。”", "作战开始。\n♖指挥系统已上线。"
    ]

    for i in text_in:
        for _ in range(1000): print('\n')  # os.sys('cls')
        print(i, '\n\n\n')
        while (True):
            ip = input("输入【1】继续\t\t输入【0】跳过对话")
            try: ip = int(ip); break
            except: continue
        if (ip == 0): break
    return


def TrueEnd():
    text_te = [
        "为何会走到如此地步？",
        "起初，他们乘着穿梭艇到来时，我们欢迎。",
        "而后，他们筑起高墙，我们规避。",
        "后来，他们开始争夺我们的资源，我们宽容。",
        "但现在，我们还能如何？",
        "一切开始的太突然，远超议事厅的预料。\n他们的军队从将自己圈起来的城墙里倾泻而出，一夜之间夺走了我们的全部。",
        "议事厅败了，败在对他们实力的低估。\n现在所有人都相信，即使远隔几十个光年，他们仍能在新世界的土地上完整展现旧世界的一切，包括那边充满血与铁的历史。",
        "所幸的是，议事厅还算有所准备。",
        "他们称这里为“菲尔德”，但他们肯定不知道，这是我们一个咒语的名字。",
        "“执行‘拓影计划’。”",
        "……",
        "……",
        "……",
        "若干年后……菲尔德区域……",
        "“你看，我说的没错吧。这里就是古战场。”",
        "“我难以想象，他们居然有这样的技术。你看这，这是……雕塑？但是完全无法触碰啊。我的手从这个东西里面穿过去了？”",
        "“看来我们要去物理系找几位老伙计了。老兄，无论如何，这将是个大考古发现啊！”",
        "“我感觉……很奇怪。我知道，几百年前我们在这儿有些不光彩的行径。\n“但是，如果真按你的假说，为何是现在我们才发现那些被封锁在所谓‘零动能区’里的遗迹？\n“而且，如果他们有这个技术，为何在古代没有大范围投入作战？”",
        "“也许是制造力不足吧。当时他们的领土大面积被侵占。至于突然出现，这个得咨询专业人士了！”",
        "“我们得快一点了，总之我对这个东西……感觉不太好。\n”物理上有个能量守恒律，我确实不懂，但是要封印这么大的区域长达几百年。”",
        "“消耗的能量从哪儿来？或者，积累的能量要往哪儿去？”"

    ]

    for i in text_te:
        for _ in range(1000): print('\n')  # os.sys('cls')
        print(i, '\n\n\n')
        while (True):
            ip = input("输入【1】继续\t\t输入【0】跳过对话")
            try:
                ip = int(ip); break
            except:
                continue
        if (ip == 0): break
    return


# 展示人物数据、战场情况一览
def display_data(round):
    for _ in range(1000): print('\n')   # os.sys('cls')
    # 显示标题
    print("--------------------------------------------------------------------------")
    print("第", round + 1, "回合\t\t", round + 1, " / 4")

    # 显示人物情报，参考透视表（recon_list）
    display_plpool = []
    for i in charpool_pl:
        number, name, job, rank, hp, armor, melee, remote, status = i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]
        job = job.replace("V", "先锋").replace("D", "护卫").replace("S", "狙击").replace("R", "突袭")
        starrank = ""
        for i in range(int(rank)):
            starrank += "★"
        display_plpool.append([number, name, job, starrank, hp, armor, melee, remote, "良好" if status else " X "])

    display_aipool = []
    for i in charpool_ai:
        if (recon_list[i[0] - 1]):
            number, name, job, rank, hp, armor, melee, remote, status = i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], \
                                                                        i[8]
            job = job.replace("V", "先锋").replace("D", "护卫").replace("S", "狙击").replace("R", "突袭")
        else:
            name = job = hp = armor = melee = remote = "???"
            number, rank, status = i[0], i[3], i[8]
        starrank = ""
        for i in range(int(rank)):
            starrank += "★"
        display_aipool.append([number, name, job, starrank, hp, armor, melee, remote, "良好" if status else " X "])

    print("【T.】我方信息\t\t\t【E.】敌方信息")
    make_table = []
    for i in range(10):
        a = []
        for j in range(9): a.append(display_plpool[i][j])
        a.append(" ")
        for j in range(9): a.append(display_aipool[i][j])
        make_table.append(a)
    make_table = pd.DataFrame(make_table,
                              columns=["T.No.", "T.Name", "T.Occu.", "T.Rank", "T.Mora.", "T.Def.", "T.Mel.", "T.Rem.",
                                       "T.Status", " ",
                                       "E.No.", "E.Name", "E.Occu.", "E.Rank", "E.Mora.", "E.Def.", "E.Mel.", "E.Rem.",
                                       "E.Status"])
    make_table.index += 1
    print(make_table, '\n')

    # 显示战场部署情况
    print("战场情况一览")
    for i in range(4):
        if (i == 0): print("我方未出战", field_sum_pl[i], "；敌方未出战", field_sum_ai[i])
        else: print("序号", i, "：", field_pool[i], "，我方部署", field_sum_pl[i], "；敌方部署", field_sum_ai[i])
    print("--------------------------------------------------------------------------")

    return


# 展示模拟作战情况
def display_field(fid, f, pl_list, ai_list):
    for _ in range(1000): print('\n')  # os.sys('cls')

    print("在序号：", fid, " ", field_pool[fid], "发生战斗。")

    # 画"叶图"
    d_f = [[], [], [], [], [], [], []]
    for i in f:
        a, a_isAI, a_loc = i[0], i[2], i[3]
        if (a_isAI):
            a_job = charpool_ai[a - 1][2]
            a_st = charpool_ai[a - 1][8]
        else:
            a_job = charpool_pl[a - 1][2]
            a_st = charpool_pl[a - 1][8]

        if (a_st): a_show = "★" if a_isAI else "♖"
        else: a_show = "†"
        a_show += a_job
        d_f[a_loc].append(a_show)

    # 展示
    m_r = 0
    for i in range(len(d_f)):
        m_r = max(m_r, len(d_f[i]))
    for j in range(m_r):
        for i in range(len(d_f)):
            try: print(d_f[i][j], end= " ")
            except: print("  ", end=" ")
        print()

    # 显示参战双方人物数据
    cpl, cpa = [], []
    for i in pl_list: cpl.append(charpool_pl[i - 1])
    for i in ai_list: cpa.append(charpool_ai[i - 1])

    print()
    display_plpool = []
    for i in cpl:
        number, name, job, rank, hp, armor, melee, remote, status = i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]
        job = job.replace("V", "先锋").replace("D", "护卫").replace("S", "狙击").replace("R", "突袭")
        starrank = ""
        for i in range(int(rank)):
            starrank += "★"
        display_plpool.append([number, name, job, starrank, hp, armor, melee, remote, "良好" if status else " X "])

    display_aipool = []
    for i in cpa:
        if (recon_list[i[0] - 1]):
            number, name, job, rank, hp, armor, melee, remote, status = i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], \
                                                                        i[8]
            job = job.replace("V", "先锋").replace("D", "护卫").replace("S", "狙击").replace("R", "突袭")
        else:
            name = job = hp = armor = melee = remote = "???"
            number, rank, status = i[0], i[3], i[8]
        starrank = ""
        for i in range(int(rank)):
            starrank += "★"
        display_aipool.append([number, name, job, starrank, hp, armor, melee, remote, "良好" if status else " X "])

    row = max(len(cpl), len(cpa))
    make_table = []
    for i in range(row):
        a = []
        for j in range(9):
            try: a.append(display_plpool[i][j])
            except: a.append("-")
        a.append(" ")
        for j in range(9):
            try: a.append(display_aipool[i][j])
            except: a.append("-")
        make_table.append(a)

    print("【T.】我方信息\t\t\t【E.】敌方信息")
    make_table = pd.DataFrame(make_table,
                              columns=["T.No.", "T.Name", "T.Occu.", "T.Rank", "T.Mora.", "T.Def.", "T.Mel.", "T.Rem.",
                                       "T.Status", " ",
                                       "E.No.", "E.Name", "E.Occu.", "E.Rank", "E.Mora.", "E.Def.", "E.Mel.", "E.Rem.",
                                       "E.Status"])
    make_table.index += 1
    print(make_table, '\n')

    time.sleep(0.5)
    print('\n')

    return


# 计算是否在某一个战场获胜
# 输入f为int，表示战场编号
# 输出为int, 玩家获胜1，AI获胜-1，平局或无结果0
def field_montecarlo(f):
    print("序号：", f, " ", field_pool[f]); time.sleep(1)

    # 调取部署数据
    combat_pl = field_sum_pl[f][:]
    combat_ai = field_sum_ai[f][:]

    combat_seq = []
    for i in combat_pl:
        number = i ; move = charpool_pl[i - 1][2]; isAI = False
        move = move.replace("R", "4").replace("V", "3").replace("S", "2").replace("D", "1")
        move = int(move) + charpool_pl[i - 1][3] * 0.5 + random.uniform(-0.1, 0.1)

        # 建立战场坐标。玩家VD在[1]，玩家RS在[0]；AI的VD在[5],AI的RS在[6]
        if (charpool_pl[i - 1][2] == "V" or charpool_pl[i - 1][2] == "D"): loc = 1
        if (charpool_pl[i - 1][2] == "R" or charpool_pl[i - 1][2] == "S"): loc = 0
        combat_seq.append([number, move, isAI, loc])
    for i in combat_ai:
        number = i ; move = charpool_ai[i - 1][2]; isAI = True
        move = move.replace("R", "4").replace("V", "3").replace("S", "2").replace("D", "1")
        move = int(move) + charpool_ai[i - 1][3] * 0.5 + random.uniform(-0.1, 0.1)

        # 建立战场坐标。玩家VD在[1]，玩家RS在[0]；AI的VD在[5],AI的RS在[6]
        if (charpool_ai[i - 1][2] == "V" or charpool_ai[i - 1][2] == "D"): loc = 5
        if (charpool_ai[i - 1][2] == "R" or charpool_ai[i - 1][2] == "S"): loc = 6
        combat_seq.append([number, move, isAI, loc])

    # 确定作战顺序。
    combat_seq = sorted(combat_seq, key=lambda x: x[1], reverse=True)

    # 开始作战
    # while(len(combat_ai) != 0 or len(combat_pl) != 0):      # 决斗
    for t in range(6):
        # 作战顺序：R - V - S - D。按顺序判断能否攻击，并造成伤害。
        if (len(combat_ai) == 0 or len(combat_pl) == 0): break

        ct = 0
        for i in combat_seq:
            display_field(f, combat_seq, field_sum_pl[f], field_sum_ai[f])
            # 读取攻击方数据
            atk, a_sw, a_isAI, a_loc = i[0], i[1], i[2], i[3]
            if (a_isAI):
                a_slice = charpool_ai[atk - 1]
                a_nu, a_na, a_job, a_rk, a_hp, a_ar, a_me, a_re, a_st = a_slice[0], a_slice[1], a_slice[2], a_slice[3], \
                                                                        a_slice[4], a_slice[5], a_slice[6], a_slice[7], \
                                                                        a_slice[8]
            else:
                a_slice = charpool_pl[atk - 1]
                a_nu, a_na, a_job, a_rk, a_hp, a_ar, a_me, a_re, a_st = a_slice[0], a_slice[1], a_slice[2], a_slice[3], \
                                                                        a_slice[4], a_slice[5], a_slice[6], a_slice[7], \
                                                                        a_slice[8]
            if (not a_st):      # 攻击者已战败
                ct += 1; continue

            # 为了平衡性，最后还是采取了"随缘剑法"：抽取对方一个幸运观众进行进攻。
            target_list = combat_seq[:]
            random.shuffle(target_list)

            no_att = True
            if (no_att == False): break
            for j in target_list:
                # 读取被攻击方数据
                de, d_isAI, d_loc = j[0], j[2], j[3]
                if (d_isAI):
                    d_slice = charpool_ai[de - 1]
                    d_nu, d_na, d_job, d_rk, d_hp, d_ar, d_me, d_re, d_st = d_slice[0], d_slice[1], d_slice[2], d_slice[3], \
                                                                            d_slice[4], d_slice[5], d_slice[6], d_slice[7], \
                                                                            d_slice[8]
                else:
                    d_slice = charpool_pl[de - 1]
                    d_nu, d_na, d_job, d_rk, d_hp, d_ar, d_me, d_re, d_st = d_slice[0], d_slice[1], d_slice[2], d_slice[3], \
                                                                            d_slice[4], d_slice[5], d_slice[6], d_slice[7], \
                                                                            d_slice[8]

                # 判断有无必要进攻这个目标
                if (a_isAI == d_isAI): continue         # 同阵营，暂不开放友伤系统
                if (atk == de and (a_isAI == d_isAI)): continue     # 自己，暂不开放自裁系统
                if (not d_st): continue                 # 目标已战败
                if (abs(a_loc - d_loc) > 2): continue      # 打不着
                if (a_re <= d_ar and a_me <= d_ar): continue    # 打不穿

                # 攻击与伤害判定，同时解锁对方情报。
                if (abs(a_loc - d_loc) == 2):   # 只能远程，狙击的远程无视80%的护甲
                    d_hp -= max((a_re - d_ar), 1) * 0.95 if (a_job != "S") else max((a_re - d_ar * 0.2), 1)
                    a_hp -= max((d_re - a_ar), 1) * 0.95 if (d_job != "S") else max((d_re - a_ar * 0.2), 1)  # 回击
                else:
                    d_hp -= max((a_me - d_ar), 3)
                    a_hp -= max((d_me - a_ar), 3) * 0.8  # 回击
                    if (a_isAI): recon_list[atk - 1] = True
                    if (d_isAI): recon_list[de - 1] = True

                # 对战败方做标记，并移出战场
                if (d_hp <= 0):
                    d_st = False
                    d_hp = 0
                    if(d_isAI): combat_ai.remove(de)
                    else: combat_pl.remove(de)
                if (a_hp <= 0):
                    a_st = False
                    a_hp = 0
                    if(a_isAI): combat_ai.remove(atk)
                    else: combat_pl.remove(atk)

                # 更新数据
                if (d_isAI): d_slice = charpool_ai[de - 1] = [d_nu, d_na, d_job, d_rk, d_hp, d_ar, d_me, d_re, d_st]
                else: d_slice = charpool_pl[de - 1] = [d_nu, d_na, d_job, d_rk, d_hp, d_ar, d_me, d_re, d_st]
                if (a_isAI): a_slice = charpool_ai[atk - 1] = [a_nu, a_na, a_job, a_rk, a_hp, a_ar, a_me, a_re, a_st]
                else: a_slice = charpool_pl[atk - 1] = [a_nu, a_na, a_job, a_rk, a_hp, a_ar, a_me, a_re, a_st]

                no_att = False
                break

            # 人物移动与展示。
            # 狙击移动到战场中央（2、4）后移动概率下降为10%，其他职业越过中线后移动概率降为25%
            rd = random.uniform(0, 100)
            move_ctrl = True
            if (a_job == "S" and a_loc == 4 and a_isAI):     move_ctrl = True if (rd <= 10) else False
            if (a_job == "S" and a_loc == 2 and not a_isAI): move_ctrl = True if (rd <= 10) else False
            if (a_job != "S" and a_loc == 3):                move_ctrl = True if (rd <= 30) else False
            if (a_job != "S" and a_loc == 2 and a_isAI):     move_ctrl = True if (rd <= 5) else False
            if (a_job != "S" and a_loc == 4 and not a_isAI): move_ctrl = True if (rd <= 5) else False


            # 若下一格敌方阻挡数 <= 我方阻挡数。突袭无视阻挡。狙击在前一格有友军时不移动。
            if (move_ctrl):
                dire = -1 if a_isAI else 1
                next_loc = a_loc
                if (a_job == "R"): next_loc += 1 * dire

                if (a_job == "S"):
                    for j in combat_seq:
                        p, l = j[2], j[3]
                        if (p != a_isAI and l == a_loc + 1 * dire):
                            next_loc -= 2 * dire
                            next_loc = min(max(next_loc, 0), 6)
                            break
                        if (p == a_isAI and l == a_loc + 1 * dire):
                            next_loc -= 1 * dire
                            break
                    next_loc += 1 * dire

                else:
                    # 计算阻挡数
                    a_blo, d_blo = 0, 0
                    for j in combat_seq:
                        n, p, l = j[0], j[2], j[3]
                        # 本方阻挡数
                        if (p == a_isAI and l == a_loc and a_st): a_blo += 1
                        if (p == a_isAI and abs(l - a_loc) == 1 and a_st): a_blo += 0.5  # 在我方前后一格的友军
                        # 对方阻挡数
                        d_st = charpool_ai[n - 1][8] if p else charpool_pl[n - 1][8]
                        if (p != a_isAI and l == a_loc + 1 * dire and d_st): d_blo += 1
                        if (p != a_isAI and abs(l - (a_loc + 1 * dire)) == 1 and d_st): d_blo += 0.5

                    if (a_job == "V" or a_job == "D"):
                        if (a_blo > d_blo): next_loc += 1 * dire
                        elif(d_blo - a_blo >= 2): next_loc -= 1 * dire

            next_loc = max(next_loc, 1) if a_isAI else min(next_loc, 5)
            combat_seq[ct] = [atk, a_sw, a_isAI, next_loc]
            ct += 1

    # 更新战后部署数据
    field_sum_pl[f] = combat_pl[:]
    field_sum_ai[f] = combat_ai[:]

    # 判定战场胜负
    if (len(combat_pl) == len(combat_ai)): return 0
    else: return 1 if (len(combat_pl) > len(combat_ai)) else -1


# AI的决策卡
def field_AIdeploy(round):
    # 整队，查看剩余角色
    remain_ai = []
    for t in field_sum_ai:
        for i in t:
            remain_ai.append(i)

    r_limchar = min(len(remain_ai), 3)
    r_char_ai = []
    r_field_ai = -1

    if (r_limchar == 0): return

    # 抽取战略卡
    rd_seed = random.uniform(0, 100)

    # 1.听天由命：放弃治疗，抽到谁就是谁
    if (rd_seed <= 5): r_field_ai = random.randint(1, 3)

    # 2.新战场：选择当前AI方人数最少的战场，
    elif (rd_seed - 19 * 1 - 5 <= 0):
        min_f = 0
        r_sel = [1]
        for i in range(1, 4, 1):
            if (min_f >= len(field_sum_ai[i])):
                r_sel.append(i)
                min_f = len(field_sum_ai[i])
        r_field_ai = random.sample(r_sel, 1); r_field_ai = r_field_ai[0]

    # 3.站稳脚跟：选择当前AI方人数最多的战场，
    elif (rd_seed - 19 * 2 - 5 <= 0):
        max_f = 0
        r_sel = [1]
        for i in range(1, 4, 1):
            if (max_f <= len(field_sum_ai[i])):
                r_sel.append(i)
                max_f = len(field_sum_ai[i])
        r_field_ai = random.sample(r_sel, 1); r_field_ai = r_field_ai[0]

    # 4.歼灭战：选择当前玩家方人数最少的战场，
    elif (rd_seed - 19 * 3 - 5 <= 0):
        min_f = 0
        r_sel = [1]
        for i in range(1, 4, 1):
            if (min_f >= len(field_sum_pl[i])):
                r_sel.append(i)
                min_f = len(field_sum_pl[i])
        r_field_ai = random.sample(r_sel, 1); r_field_ai = r_field_ai[0]

    # 5.大合战：选择当前玩家方人数最多的战场，但部署后AI方在该地人数不少于玩家方。
    elif (rd_seed - 19 * 4 - 5 <= 0):
        max_f = 0
        r_sel = [1]
        for i in range(1, 4, 1):
            if (max_f <= len(field_sum_pl[i])
                    and len(field_sum_ai[i]) + len(remain_ai) >= len(field_sum_pl[i])):     # 杜绝人数上的"欢乐送"
                r_sel.append(i)
                max_f = len(field_sum_pl[i])
        r_field_ai = random.sample(r_sel, 1); r_field_ai = r_field_ai[0]

    # 6.援军：选择当前AI方与玩家方人数差距最小的战场
    else:
        diff = 0
        r_sel = [1]
        for i in range(1, 4, 1):
            if (diff >= abs(len(field_sum_pl[i]) - len(field_sum_ai[i]))):
                r_sel.append(i)
                diff = abs(len(field_sum_pl[i]) - len(field_sum_ai[i]))
        r_field_ai = random.sample(r_sel, 1); r_field_ai = r_field_ai[0]

    # 抽取决策卡
    rd_seed = random.uniform(0, 100)
    r_char_temp = []

    # 1.听天由命：放弃治疗，抽到谁就是谁
    if (rd_seed - 1 * 100 / 6 <= 0):
        r_maxchar = random.randint(1, r_limchar)
        r_char_temp = random.sample(remain_ai, r_maxchar)

    # 2.优先生命值
    elif (rd_seed - 2 * 100 / 6 <= 0):
        r_maxchar = r_limchar
        pool_temp = charpool_ai[:]
        pool_temp = sorted(pool_temp, key = lambda x: x[4], reverse= True)

        ct = 0
        for t in range(10):
            if (ct == r_maxchar): break

            if (pool_temp[t][8]):
                r_char_temp.append(pool_temp[t][0])
                ct += 1

    # 3.优先近战
    elif (rd_seed - 3 * 100 / 6 <= 0):
        r_maxchar = r_limchar
        pool_temp = charpool_ai[:]
        pool_temp = sorted(pool_temp, key=lambda x: x[6], reverse=True)

        ct = 0
        for t in range(10):
            if (ct == r_maxchar): break

            if (pool_temp[t][8]):
                r_char_temp.append(pool_temp[t][0])
                ct += 1

    # 4.优先远程, S-nS
    elif (rd_seed - 4 * 100 / 6 <= 0):
        r_maxchar = r_limchar
        pool_temp = charpool_ai[:]
        pool_temp = sorted(pool_temp, key=lambda x: x[7], reverse=True)

        ct = 0
        for t in range(10):
            if (ct == r_maxchar): break

            if (ct == 1):   # 狙击太菜了，需要强制配一个非远程
                if (t >= 7):
                    r_char_temp.append(pool_temp[t][0])
                    ct += 1    # 正常情况下只需要3个。如果找到第7个还是狙击就算了
                    continue
                if (pool_temp[t][2] != "S" and pool_temp[t][8]):
                    r_char_temp.append(pool_temp[t][0])
                    ct += 1

                else: continue
            elif (pool_temp[t][8]):
                r_char_temp.append(pool_temp[t][0])
                ct += 1

    # 5.优先rank
    elif (rd_seed - 5 * 100 / 6 <= 0):
        r_maxchar = r_limchar
        pool_temp = charpool_ai[:]
        pool_temp = sorted(pool_temp, key=lambda x: x[3], reverse=True)

        ct = 0
        for t in range(10):
            if (ct == r_maxchar): break

            if (pool_temp[t][8]):
                r_char_temp.append(pool_temp[t][0])
                ct += 1

    # 6.rank均衡, 3-2-1
    elif (rd_seed - 6 * 100 / 6 <= 0):
        r_maxchar = r_limchar
        pool_temp = charpool_ai[:]
        pool_temp = sorted(pool_temp, key=lambda x: x[3], reverse=True)

        ct = 0
        for t in range(10):
            if (ct == r_maxchar): break

            if (ct == 1 and pool_temp[t][8]):
                r_char_temp.append(pool_temp[-1][0])
                ct += 1
            elif (pool_temp[t][8]):
                r_char_temp.append(pool_temp[t][0])
                ct += 1


    # 将人物移动，先移出再移入
    for i in r_char_temp:
        for t in field_sum_ai:
            try: t.remove(i)
            except: continue
        r_char_ai.append(i)

    r_char_ai = sorted(r_char_ai)
    field_sum_ai[r_field_ai] = r_char_ai[:]

    # 通报结果
    for _ in range(1000): print('\n')  # os.sys('cls')
    print("AI将序号为", r_char_ai, "的部队移动到", field_pool[r_field_ai])

    ip = input("请按回车键继续……")
    return


# 玩家决策并输入部署指令
def field_operate(round):
    # 1. 整队，查看剩余角色
    remain_pl = []
    for t in field_sum_ai:
        for i in t:
            remain_pl.append(i)

    if (len(remain_pl) == 0): return

    # 1.5. 第一回合获取情报
    if (round == 0):
        while (True):
            order = input('你希望获取敌方哪一个部队的信息？')
            try: order = int(order)
            except: continue
            if (int(order) >= 1 and int(order) <= 10): break
        r_spy_act = order - 1
        recon_list[r_spy_act] = True
        display_data(round)
        print("情报解析成功。请展开部署。")

    # 2. 选择战场
    while (True):
        order = input('请选择本回合战场：')
        try: order = int(order)
        except: continue
        if(int(order) == 1 or int(order) == 2 or int(order) == 3): break
    r_field_pl = order

    # 3. 选择人物
    while (True):
        order = input('你要派遣多少支编队？（最多%s支）：' % min(len(remain_pl), 3))
        try: order = int(order)
        except: continue
        if(int(order) >= 1 and int(order) <= 3): break
    r_maxchar = order

    # temp = []
    temp = field_sum_pl[r_field_pl][:]
    for i in range(r_maxchar):
        while (True):
            order = input('请选择第%s支出阵编队的代号（T.No.）：' % (i + 1))
            try: order = int(order)     # 注意此处玩家输入的是一般思考的数字，计算时要-1
            except: continue

            # 不能重复选择
            re_type = False
            for j in temp:
                if(order == j):
                    print("角色重复。"); re_type = True; continue

            # 不能选择战败角色
            if (not charpool_pl[order - 1][8]):
                print("该角色已战败。"); re_type = True; continue

            if(not re_type and int(order - 1) >= 0 and int(order - 1) <= 9): break

        r_char_pl = order - 1

        # 将人物移动，先移出再移入
        for t in field_sum_pl:
            try:
                t.remove(r_char_pl + 1)
            except: continue
        temp.append(r_char_pl + 1)
        print("将", charpool_pl[r_char_pl][1], "移动到", field_pool[r_field_pl])
        field_sum_pl[r_field_pl].append(r_char_pl + 1)

    for i in field_sum_pl: i = sorted(i)
    display_data(round)

    return


# 计算回合后每个战场的情况。判定结局。
def field_judge(round):

    round_sum = [0, 0, 0, 0]    # round_sum[0] 无意义

    for f in range(1, 4, 1):
        if(len(field_sum_pl[f]) != 0 and len(field_sum_ai[f]) != 0):
            # 作战模拟
            round_sum[f] = field_montecarlo(f)


        elif(len(field_sum_pl[f]) != 0 and len(field_sum_ai[f]) == 0):
            round_sum[f] = 1
        elif(len(field_sum_pl[f]) == 0 and len(field_sum_ai[f]) != 0):
            round_sum[f] = -1
        elif(len(field_sum_pl[f]) == 0 and len(field_sum_ai[f]) == 0):
            round_sum[f] = 0

    # 写战况
    display_data(round)
    print("战斗结束，战场情况如下：")
    ct = 0
    for f in range(1, 4, 1):
        if(round_sum[f] == 1): print("我们在序号", f, "：", field_pool[f], "取得优势。"); ct += 1
        if(round_sum[f] == -1): print("我们在序号", f, "：", field_pool[f], "处于劣势。")
        if(round_sum[f] == 0): print("序号", f, "：", field_pool[f], "暂时稳定。")

    ip = input("请按回车键继续……")

    # 判断赢得了几个战场
    return ct


# 正式游戏流程，主要函数
def battle():
    # task 1: 回合开始
    max_round = 4
    for round in range(max_round):
        # 回合提示
        for _ in range(1): print('\n')
        print("====================================================================================================================================")
        print("第", round + 1, "回合", "等待电脑计算……")

        field_AIdeploy(round)

        for _ in range(1): print('\n')
        print("第", round + 1, "回合", "请展开部署。")

        time.sleep(1)

        display_data(round)
        print("部署阶段。")
        field_operate(round)
        pl_win = field_judge(round)     # 判断玩家赢得了几个战场

    # 4个回合结束后，判断我方与敌方战损
    remain_pl = []
    remain_ai = []
    for i in range(10):
        if (charpool_pl[i][8]): remain_pl.append(charpool_pl[i][1])
        if (charpool_ai[i][8]): remain_ai.append(charpool_ai[i][1])

    n_pl, n_ai = len(remain_pl), len(remain_ai)

    # 触发结局
    for _ in range(1000): print('\n')   # os.sys('cls')
    # Bad End: 没有赢得一个战场
    if (pl_win == 0): print("Bad End.\n无人生还。")

    # Good End 1: 只赢得一个战场且我方存活少于对方
    elif (pl_win == 1 and n_pl <= n_ai): print("Good End 1.\n在敌方的强烈攻打下，我们存活下来，但损失惨重。\n计划失败，但活下去就有希望。")

    # True End: 赢得三个战场，且我方存活比对方多
    elif (pl_win == 3 and n_pl > n_ai):
        ip = input("True End.\n请按回车键继续……")
        TrueEnd()

    # Good End 2: 其他情况
    else:
        print("Good End 2.\n敌方煞费苦心的进攻遭到了猛烈回击。自此，他们再也不敢轻视我们了。\n至少短时间内如此。")

    return


if __name__ == "__main__" :
    # task 0: introduction
    introduction()

    # task 1: 创建双方人物池
    charpool_pl = set_pool_character()
    charpool_ai = set_pool_character()

    # task 2: 创建战场
    display_data(-1)
    print("♖ 作战指挥系统准备完毕 ♖")

    ip = input("请按回车键继续……")
    battle()

