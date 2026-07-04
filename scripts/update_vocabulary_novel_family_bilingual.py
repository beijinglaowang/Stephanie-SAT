from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "artifacts" / "vocabulary_fiction_novel.md"
CSV_PATH = ROOT / "artifacts" / "vocabulary_flashcards_complete_deduped_source.csv"


CHINESE_VERSION = """# 中文版：Stephanie and the Riverlight Edict

_中文版用于帮助理解剧情；正式词汇学习以英文版为准。_

## 第一章：玻璃之城

Ilyr城的雨不是从云里落下来的，而是由议会的玻璃高塔分配。Stephanie Venn在透镜大厅工作，她细心、好奇，也越来越怀疑那些关于“缺水”的官方说法。

很多年前，Stephanie的奶奶Grandma Lin和爷爷Grandpa Bruce教过她：光会暴露挡住它的那只手。她的哥哥Brandon、姐姐Melissa、爸爸Yamin、妈妈Jimin都知道，这个家族一直不相信议会。Stephanie的两个好朋友Grace和Ada也一直帮她保守秘密。

当Stephanie在透镜里看到一束不正常的蓝光时，她意识到城下可能有一条被隐藏的河。Melissa带来偷出的地图，Brandon用他的档案知识确认旧记录被篡改。三个人决定寻找证据。

## 第二章：钟屋

Stephanie、Melissa和Brandon沿着复杂的地下通道来到钟屋附近。他们在那里见到Grandma Lin。奶奶曾经是著名工程师，因为拒绝替议会撒谎，被当成异端。

Grandma Lin告诉他们，高塔并不制造水，只是控制水。真正的河流就在城下，足够养活所有人。可是高塔也支撑着城市，不能鲁莽摧毁。唯一安全的办法，是找到Prime Lens，在全城面前展示真相。

## 第三章：学者监狱

钟屋同时也是关押学者的监狱。Melissa说，妈妈Jimin被关在那里。Brandon伪造文件，Melissa带路，Stephanie用透镜打开封印。

他们找到Jimin，也找到虚弱的Grandpa Bruce。Jimin曾写文章嘲笑议会的假慈善，因此被关押。Grandpa Bruce把破裂的Prime Lens交给Stephanie，告诉她：议会最大的弱点是傲慢。

## 第四章：节日前的计划

Grandpa Bruce知道议会如何制造周期性的缺水，用痛苦控制人民。Stephanie修复Prime Lens，Brandon研究节日程序，Melissa负责行动路线。爸爸Yamin一开始很怀疑，认为大家只有勇气，没有计划，但当他看到地下河的影像时，也沉默了。

Grace和Ada作为Stephanie最好的朋友加入了计划。Grace在诊所照顾缺水的病人，Ada帮助联系旧井看守人。后来她们又认识了新朋友Zoe。Zoe熟悉运河区，能把消息传到普通人中间。

## 第五章：坏人Prince

坏人Prince是议会的统治者。他住在华丽宫殿里，懂得怎样用恐惧管理城市。他的调查官Malrec向他报告：Stephanie一家正在寻找河流的证据。

Prince不想立刻杀死他们，因为他害怕制造英雄。他命令Malrec把逮捕伪装成日常检查，让真相看起来像偶然的麻烦。他真正害怕的不是一副透镜，而是故事传播开来。

## 第六章：下城区

Stephanie和Melissa去下城区寻找证人。她们看到病人、干井、缺水的学校。Grace带她们进入诊所，Ada和Zoe帮助联系愿意作证的人。越来越多普通人加入：面包师、歌手、钟表匠、印刷工。

困难也越来越多。有人被抓，暗号出错，车辆坏掉。Melissa想用武力解决问题，Stephanie提醒她不能把每个问题都当成战斗。Yamin带来消息：Malrec已经搜查了Grandma Lin的工作室。时间不多了。

## 第七章：旧水厂

Prime Lens还缺一个银环，藏在旧水厂。那里充满蒸汽、塌陷的齿轮和危险通道。Stephanie靠河光辨认方向，Brandon记录墙上的旧文字，Melissa负责保护大家。

他们发现第一代工程师留下的警告：不要让任何权力独占公共的河。拿到银环后，Malrec包围了他们。关键时刻，Grandpa Bruce打开蒸汽阀，大家趁乱逃走。

## 第八章：没有真相的审判

Jimin为了掩护大家被抓。Prince把她带到大厅台阶上公开审判，想让她承认真相是假的。Jimin虽然受伤，却只说了一句：“Prince害怕水。”

这句话在人群中引起震动。Prince判她去劳役，想让同情变成恐惧。Stephanie很想立刻救妈妈，但Melissa提醒她，如果现在行动，整个计划都会失败。她们决定第二天在广场揭示地下河。

## 第九章：第一次雨的彩排

彩排那天，Prince站在高台上发表虚假的祝福。Stephanie爬进Great Prism塔，把Prime Lens和银环装好。Brandon用文书混乱拖住守卫，Melissa和Yamin制造烟雾引开巡逻。

阳光击中透镜，蓝色河光从广场升起。所有人都看见石板下真实流动的河。Stephanie通过号角说：河是真的，短缺是制造出来的。Grandpa Bruce、Brandon和Grace拿出证据，Prince的谎言开始崩塌。

## 第十章：Prince最后的手段

Prince不肯认输。他命令打开紧急水门，想制造洪水，让人民以为河流危险。Stephanie发现警报后，和Melissa、Grandpa Bruce、Yamin一起冲进控制坑。

水压巨大，阀门生锈。Yamin击中Stephanie指出的裂缝，压力开始下降。Malrec追来阻止他们，Melissa挡住他。最后Stephanie打开最后一道阀门，让河水进入城市水道，而不是毁掉城市。

## 第十一章：水之后

傍晚，干涸的广场有了喷泉，议会的权威开始崩塌。Prince被自己的守卫抓住，Malrec逃走。城市进入临时会议，所有人都争论如何补偿受害者、如何惩罚罪犯、如何公开档案。

Brandon提醒大家不要让复仇变成新的统治。Melissa要求坏官员负责。Grandma Lin坚持处罚必须符合证据。Grace提出给受害家庭补偿，Jimin要求把钟屋改成学校。Yamin起草了第一份公共宪章。

## 第十二章：透镜师的选择

几个月后，Stephanie回到透镜大厅。那里不再服务议会，而是向所有地区的孩子开放。Grandma Lin教工程，Brandon教法律，Melissa教逃生路线，Grace、Ada和Zoe帮助新的学生适应自由后的城市。

城市邀请Stephanie成为First Keeper of the Prism。她害怕头衔会变成新的牢笼，于是向Grandpa Bruce请教。爷爷告诉她：不要把谦逊和恐惧混在一起。Stephanie接受了职位，但要求所有记录公开、所有机械原理都被教学。

## 尾声：公共之河

多年后，学校会把这段历史写得更整齐、更简单。但Stephanie知道，真正的改变来自害怕却仍然互相信任的人。她的家人、朋友和新朋友Zoe一起证明了：真相不一定让世界完美，但能让人不再把口渴当作命运。

五十周年那天，年老的Stephanie坐在Great Prism下。一个学生问她当年是否确定会成功。她说：“不。大多数时候我都很害怕。”然后她补充：“记住，勇气不是没有恐惧；勇气是带着恐惧仍然去改变世界。”
"""


def strip_chinese_version(text: str) -> str:
    marker = "\n# 中文版"
    index = text.find(marker)
    if index != -1:
        text = text[:index].rstrip() + "\n"
    return text


def apply_relationships(text: str) -> str:
    text = strip_chinese_version(text)
    text = text.replace(
        "_A study novella using every unique word from the complete deduped flashcard set. Vocabulary words are bolded at first use._",
        "_Official English version using every unique word from the complete deduped flashcard set. A Chinese version follows after the English story._",
    )
    text = text.replace("Regent Vey", "Prince")
    text = text.replace("High Regent Odran Vey", "The bad guy Prince, the High Regent,")
    text = text.replace("Vey's", "Prince's")
    text = text.replace("Vey", "Prince")
    text = text.replace("Melissa Kest", "Melissa Venn")
    text = text.replace("Kest family", "Venn family")
    text = text.replace("Mara's", "Melissa's")

    replacements = [
        (
            "Years earlier, Stephanie's **venerable** Grandma Ada and Grandpa Bruce had taught her the **salient** rule of lenses: every beam reveals the hand that blocks it. Bruce had a **tenacious** faith in hidden rivers, but his proof was **tenuous**; Ada had to **truncate** every lesson whenever Council inspectors passed. By **serendipity**, Stephanie still owned one page from his notebook, a diagram with a **scintillating** blue arc. When a **supercilious** inspector dismissed it as childish, she kept it under her mattress until the city's lies reached their **zenith**.",
            "Years earlier, Stephanie's **venerable** Grandma Lin and Grandpa Bruce had taught her the **salient** rule of lenses: every beam reveals the hand that blocks it. Grandpa Bruce had a **tenacious** faith in hidden rivers, but his proof was **tenuous**; Grandma Lin had to **truncate** every lesson whenever Council inspectors passed. By **serendipity**, Stephanie still owned one page from his notebook, a diagram with a **scintillating** blue arc. When a **supercilious** inspector dismissed it as childish, she kept it under her mattress until the city's lies reached their **zenith**.",
        ),
        (
            "That evening, an **abrasive** knock rattled her door. A girl in an **unkempt** coat slipped inside before Stephanie could answer.",
            "That evening, an **abrasive** knock rattled her door. Stephanie's older sister Melissa slipped inside in an **unkempt** coat before Stephanie could answer.",
        ),
        (
            '"Melissa Venn. I need to **abscond** before the wardens decide to **arraign** me for breathing near a sealed archive."',
            '"Melissa Venn, your older sister. I need to **abscond** before the wardens decide to **arraign** me for breathing near a sealed archive."',
        ),
        (
            "Their first ally was Brandon, an **amiable** clerk with a talent for appearing **apathetic** while listening to everything. His family had once been **affluent**, before the Council declared their well a state instrument. He knew the **antecedent** to every modern law and could quote each old decree with miserable accuracy.",
            "Their first ally was Stephanie's older brother Brandon, an **amiable** clerk with a talent for appearing **apathetic** while listening to everything. His family had once been **affluent**, before the Council declared their well a state instrument. He knew the **antecedent** to every modern law and could quote each old decree with miserable accuracy. Brandon and Stephanie shared only sibling shorthand: arguments, loyalty, and the habit of finishing each other's plans.",
        ),
        (
            "At the edge waited Stephanie's grandmother, Ada Dain, in a blue coat.",
            "At the edge waited Stephanie's grandmother, Lin Dain, in a blue coat.",
        ),
        (
            '"Grandma Ada," Stephanie whispered. "My grandmother."',
            '"Grandma Lin," Stephanie whispered. "My grandmother."',
        ),
        (
            'Ada lifted her chin. "Once an **eminent** engineer. Now a heretic, according to **edict** seven hundred and nine."',
            'Grandma Lin lifted her chin. "Once an **eminent** engineer. Now a heretic, according to **edict** seven hundred and nine."',
        ),
        (
            'Melissa\'s face changed. The **bashful** bravado left it. "Jimin is in the Bell House. She owes me three figs and a rescue."',
            'Melissa\'s face changed. The **bashful** bravado left it. "Mom is in the Bell House. Jimin left a message through the printers."',
        ),
        (
            "Their guide was a **taciturn** prisoner named Jimin, thin and **pallid**, with eyes like sharpened slate. She had once written a **periodical** mocking the Council's **ostentatious** charity balls.",
            "Their guide was Stephanie's mother, Jimin Venn, a **taciturn** prisoner with **pallid** cheeks and eyes like sharpened slate. She had once written a **periodical** mocking the Council's **ostentatious** charity balls.",
        ),
        (
            '"Melissa Venn," she said. "You still owe me three figs."',
            '"Melissa," Jimin said. "Still reckless, still late."',
        ),
        (
            "A **cynic** named Yamin argued that citizens preferred lies if lies came with soup.",
            "Stephanie's father, Yamin Venn, a wary **cynic**, argued that citizens preferred lies if lies came with soup.",
        ),
        (
            "Their quarrel was interrupted by Yamin the cynic, who arrived with news: Malrec had seized Grandma Lin's workshop.",
            "Their quarrel was interrupted by Yamin, Stephanie's father, who arrived with news: Malrec had seized Grandma Lin's workshop.",
        ),
        (
            'Prince\'s smile did not change. "A **fatuous** remark from a man at his **nadir**."',
            'Prince\'s smile did not change. "A **fatuous** remark from a woman at her **nadir**."',
        ),
        (
            "The nurse, Grace, was **magnanimous** even in exhaustion. She ran a **philanthropic** clinic with no patron except stubborn decency.",
            "Stephanie's best friend Grace, now training as a nurse, was **magnanimous** even in exhaustion. She ran a **philanthropic** clinic with no patron except stubborn decency.",
        ),
        (
            "The ceremony required the High Regent to stand beneath the Great Prism and **expound** on civic **piety**.",
            "The ceremony required Prince to stand beneath the Great Prism and **expound** on civic **piety**.",
        ),
        (
            '"Can your lens truly reveal water?" he asked.',
            '"Can your lens truly reveal water?" Grace asked.',
        ),
        (
            "They met others: a **loquacious** baker who could not keep secrets but could hide people in flour carts; a **bashful** singer whose voice could carry across the square; a **punctilious** watchmaker who built timing devices small enough to fit inside prayer beads.",
            "Ada, Stephanie's other best friend, arrived with Zoe, a new friend from the canal quarter. Zoe knew a **loquacious** baker who could not keep secrets but could hide people in flour carts; Ada recruited a **bashful** singer whose voice could carry across the square; Grace found a **punctilious** watchmaker who built timing devices small enough to fit inside prayer beads.",
        ),
        (
            "At the central chamber, they found the ring mounted above a dry fountain. Around it were names of the first engineers, including Ada's grandmother, the **epitome** of the old guild's **prowess**.",
            "At the central chamber, they found the ring mounted above a dry fountain. Around it were names of the first engineers, including Grandma Lin's grandmother, the **epitome** of the old guild's **prowess**.",
        ),
        (
            '"A city is not loved," Prince told Malrec. "It is managed."',
            '"A city is not family," Prince told Malrec. "It is managed."',
        ),
        (
            "Months later, Stephanie returned to the Hall of Lenses. It no longer served the Council. Apprentices from every district studied there, including children who once would have been dismissed as **marginal** or **servile**. Grandma Ada taught engineering with **brusque** affection. Brandon taught law and occasionally forgot not to be proud. Melissa taught escape routes, though the new assembly refused to make that an official subject.",
            "Months later, Stephanie returned to the Hall of Lenses. It no longer served the Council. Apprentices from every district studied there, including children who once would have been dismissed as **marginal** or **servile**. Grandma Lin taught engineering with **brusque** affection. Brandon taught law with older-brother patience and occasionally forgot not to be proud. Melissa taught escape routes, though the new assembly refused to make that an official subject. Grace, Ada, and Zoe helped new students find their places.",
        ),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    text = text.replace("Grandma Ada's", "Grandma Lin's")
    text = text.replace("Grandma Ada", "Grandma Lin")
    text = text.replace("Ada's grandmother", "Grandma Lin's grandmother")
    text = text.replace("soften Grandma Lin's sarcasm", "soften Grandma Lin's sarcasm")
    text = text.replace("The Regent", "Prince")
    text = text.replace("the Regent", "Prince")

    if "Grace and Ada, Stephanie's best friends" not in text:
        anchor = "She tried to **ascertain** the cause, but the Hall records had been altered."
        text = text.replace(
            anchor,
            "Grace and Ada, Stephanie's best friends, were the only people outside her family who knew she kept the forbidden diagram.\n\n" + anchor,
        )

    if "Zoe" not in text:
        anchor = "Their circle widened in **sporadic** meetings and whispered pledges."
        text = text.replace(
            anchor,
            "Their circle widened in **sporadic** meetings and whispered pledges. A new friend named Zoe carried messages through the canal quarter.",
        )

    return text.strip() + "\n\n" + CHINESE_VERSION.strip() + "\n"


def validate(text: str) -> None:
    english = text.split("\n# 中文版", 1)[0]
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as handle:
        words = [row["word"] for row in csv.DictReader(handle)]

    missing = [
        word
        for word in words
        if not re.search(r"\b" + re.escape(word) + r"\b", english, flags=re.IGNORECASE)
    ]
    if missing:
        raise SystemExit(f"Missing vocabulary words in English version: {missing}")

    required = [
        "older brother Brandon",
        "older sister Melissa",
        "Stephanie's father, Yamin",
        "Stephanie's mother, Jimin",
        "Grace and Ada, Stephanie's best friends",
        "bad guy Prince",
        "Prince",
        "Zoe",
        "Grandma Lin",
        "Grandpa Bruce",
        "# 中文版",
    ]
    missing_required = [item for item in required if item not in text]
    if missing_required:
        raise SystemExit(f"Missing required relationship/story markers: {missing_required}")


def main() -> None:
    text = MD_PATH.read_text(encoding="utf-8")
    text = apply_relationships(text)
    validate(text)
    MD_PATH.write_text(text, encoding="utf-8", newline="\n")
    print(MD_PATH)


if __name__ == "__main__":
    main()
