#!/usr/bin/env python3
from collections import namedtuple
from enum import Enum
import random
import logging

import urwid


logging.basicConfig(filename="log.txt", level=logging.DEBUG)


PALETTE = [
    ("disabled", "dark gray", ""),
    ("reversed", "standout", ""),
    ("warn", "dark red", ""),
]


class CharInfo:
    def __init__(self):
        self.stats = {stat: 0 for stat in STATS}
        self.char_class = None
        self.skills = set()

    def __repr__(self):
        return (
            "CharInfo("
            f"stats: {self.stats}"
            f"class: {self.char_class}"
            f"skills: {self.skills}"
            ")"
        )


class IntEditArrows(urwid.IntEdit):
    def keypress(self, size, key):
        if key in ("right", "l"):
            self.set_edit_text(str(self.value() + 1))
            self.set_edit_pos(len(self.get_edit_text()))
        elif key in ("left", "h"):
            self.set_edit_text(str(self.value() - 1))
            self.set_edit_pos(len(self.get_edit_text()))
        else:
            return super().keypress(size, key)


class ListBoxVikeys(urwid.ListBox):
    def keypress(self, size, key):
        # hack: translate vikeys into direction keys
        if key == "j":
            key = "down"
        elif key == "k":
            key = "up"
        return super().keypress(size, key)


class CHAR_CLASSES(Enum):
    FIGHTING_MAN = "Fighting Man"
    MAGIC_USER = "Magic User"
    CLERIC = "Cleric"

    def __repr__(self):
        return self.value


class STATS(Enum):
    AGE = "LVL"
    PTS = "PTS"
    STR = "STR"
    DEX = "DEX"
    CON = "CON"
    INT = "INT"
    WIS = "WIS"
    CHA = "CHA"
    LUC = "LUC"
    MON = "$$$"
    REP = "REP"

    def __repr__(self):
        return self.value


POINT_BUY_STATS = [
    STATS.STR,
    STATS.DEX,
    STATS.CON,
    STATS.INT,
    STATS.WIS,
    STATS.CHA,
    STATS.LUC,
]

CHAR_CLASS_STAT_BONUSES = {
    CHAR_CLASSES.FIGHTING_MAN: {STATS.STR: 2, STATS.DEX: 2, STATS.CON: 2},
    CHAR_CLASSES.MAGIC_USER: {STATS.INT: 2, STATS.CHA: 2, STATS.DEX: 2},
    CHAR_CLASSES.CLERIC: {STATS.WIS: 2, STATS.CON: 2, STATS.LUC: 2},
}

CHAR_CLASS_DESC_FRAGMENTS = {
    CHAR_CLASSES.FIGHTING_MAN: [
        "Fight.",
        "Hit the bad guys.",
        "Swing the sharp thing around.",
        "Real tough.",
        "Strong.",
        "Big muscles.",
        "Huge muscles.",
        "Hold a big stick.",
        "Jump real high.",
        "Heavy armor proficiency.",
    ],
    CHAR_CLASSES.MAGIC_USER: [
        "Eat manna.",
        "Abracadabra.",
        "Big pointy hat.",
        "Zip zoop zap!",
        "Stroke the beard.",
        "You shall not pass.",
        "Accurate missiles.",
        "Float in the air?",
        "Start with force bolt.",
    ],
    CHAR_CLASSES.CLERIC: [
        "Pray.",
        "Wololo.",
        "Wear the fanciest hats.",
        "Dear lord.",
        "Get more HPs.",
        "Not afraid of skeletons.",
        "Protection is a racket.",
        "Turn into stone.",
        "Turn spooky bois around.",
        "Turn on the light.",
    ],
}


class SKILLS(Enum):
    JUMP = "Jumping"
    CLIMB = "Climbing"
    READ = "Decipher Runes"
    WRITE = "Runic Composition"
    CLOVER = "Four-Leaf Clover"
    TIME = "Celestial Lore"
    HERBOLOGY = "Herbology"
    EMPATHY = "Empathy"
    DETECTIVE = "Detective"
    IDENTIFY = "Identify"
    ARCHAEOLOGY = "Archaeology"
    COSMOLOGY = "Cosmology"

    NUMEROLOGY_1 = "Numerology I"
    NUMEROLOGY_2 = "Numerology II"
    NUMEROLOGY_3 = "Numerology III"

    def __repr__(self):
        return self.value


SKILL_DESCS = {
    SKILLS.JUMP: "You can jump very high. Gives +5 on jump height rolls.",
    SKILLS.CLIMB: "You can scale ropes, trees, walls, and more with ease."
    " Adds a d12 to rolls involving scaling obstacles.",
    SKILLS.READ: "Parse the secrets scrawled onto walls and other places.",
    SKILLS.WRITE: "Store your mystical secrets for later."
    " Necessary for the creation of magical scrolls.",
    SKILLS.CLOVER: "ALL d4 rolls become d8 rolls.",
    SKILLS.TIME: "Knowledge behind the motion of celestial bodies.",
    SKILLS.HERBOLOGY: "Grow and nurture plants.",
    SKILLS.EMPATHY: "Understand others. Understand yourself.",
    SKILLS.DETECTIVE: "Read between the lines, uncover the mystery.",
    SKILLS.IDENTIFY: "Ascertain the instrinsic nature of an entity.",
    SKILLS.ARCHAEOLOGY: "Know human behavior by studying artifacts and landscapes.",
    SKILLS.COSMOLOGY: "Unlock the secrets of the universe.",
    SKILLS.NUMEROLOGY_1: "Divine the relationship between abstract"
    " numerical entities.",
    SKILLS.NUMEROLOGY_2: "Unveil the mystery of geometric forms.",
    SKILLS.NUMEROLOGY_3: "Untangle the calculus of intertwined dimensions.",
}

SKILL_PREREQS = {
    SKILLS.WRITE: [SKILLS.READ],
    SKILLS.ARCHAEOLOGY: [SKILLS.READ],
    SKILLS.DETECTIVE: [SKILLS.IDENTIFY],
    SKILLS.COSMOLOGY: [SKILLS.TIME],
    SKILLS.NUMEROLOGY_2: [SKILLS.NUMEROLOGY_1],
    SKILLS.NUMEROLOGY_3: [SKILLS.NUMEROLOGY_2],
}

SKILL_STAT_PREREQS = {
    SKILLS.READ: {STATS.INT: 5},
    SKILLS.WRITE: {STATS.INT: 10},
    SKILLS.JUMP: {STATS.STR: 10},
    SKILLS.CLIMB: {STATS.STR: 15},
    SKILLS.CLOVER: {STATS.LUC: 20},
    SKILLS.EMPATHY: {STATS.WIS: 12},
    SKILLS.IDENTIFY: {STATS.INT: 13},
    SKILLS.DETECTIVE: {STATS.INT: 15},
    SKILLS.COSMOLOGY: {STATS.WIS: 13, STATS.INT: 10},
    SKILLS.NUMEROLOGY_1: {STATS.INT: 12},
    SKILLS.NUMEROLOGY_2: {STATS.INT: 15},
    SKILLS.NUMEROLOGY_3: {STATS.INT: 15},
}


def get_skill_desc(skill):
    desc = SKILL_DESCS[skill]
    if skill in SKILL_PREREQS:
        desc += f'\n\nPrereqs: {", ".join(s.value for s in SKILL_PREREQS[skill])}'
    if skill in SKILL_STAT_PREREQS:
        desc += "\n\nRequired stats:"
        for stat in SKILL_STAT_PREREQS[skill]:
            desc += f"\n    {SKILL_STAT_PREREQS[skill][stat]} {stat.value}"

    return desc


class HOBBY(Enum):
    RUN = "Running"
    READ = "Reading"
    BIRDWATCHING = "Birdwatching"


HOBBY_DESC_FRAGMENTS = {
    HOBBY.RUN: [
        "Run like the wind.",
        "Scout the area.",
        "Runners' high.",
        "Feet tough and blackened.",
        "Strong legs.",
        "Tough on your joints.",
    ],
    HOBBY.READ: [
        "Go to the library.",
        "Eyes straining under candlelight.",
        "Only limited by your imagination.",
        "Trains focus.",
        "Words words words.",
    ],
    HOBBY.BIRDWATCHING: [
        "See the birds.",
        "Watch the birds.",
        "See them fly.",
        "Quiet in the forest.",
        "Sounds all around.",
        "Sit very still.",
    ],
}

StatCheck = namedtuple("StatCheck", ["stat", "num_dice", "sides", "dc"])


class Event:
    def __init__(self, desc, choices, prereq_fn=lambda player: True):
        self.desc = desc
        self.choices = choices
        self.prereq_fn = prereq_fn


EventChoice = namedtuple(
    "EventChoice", ["name", "skill_reqs", "checks", "success", "failure"]
)


class EventResult:
    def __init__(self, desc, stat_mods={}, trigger_events=()):
        self.desc = desc
        self.stat_mods = stat_mods
        self.trigger_events = trigger_events


EVENTS = {
    "hunger": Event(
        desc="You're hungry.",
        choices=[
            EventChoice(
                name="Buy bread",
                skill_reqs=set(),
                checks=[StatCheck(STATS.MON, num_dice=0, sides=4, dc=1)],
                success=EventResult(
                    desc="You buy and eat bread.", stat_mods={STATS.MON: -1}
                ),
                failure=EventResult(
                    desc="You have no money!", stat_mods={STATS.CON: -1}
                ),
            ),
            EventChoice(
                name="Grow bread",
                skill_reqs={SKILLS.HERBOLOGY},
                checks=(),
                success=EventResult(
                    desc="You grab a piece of bread off of your bread tree."
                    " You sell the extra bread!",
                    stat_mods={STATS.MON: +5},
                ),
                failure=None,
            ),
        ],
    ),
    "rain": Event(
        desc="It's raining outside.",
        choices=[
            EventChoice(
                name="Read a book",
                skill_reqs={SKILLS.READ},
                checks=[StatCheck(STATS.INT, num_dice=1, sides=20, dc=20)],
                success=EventResult(
                    desc="It's fascinating.", stat_mods={STATS.INT: +2}
                ),
                failure=EventResult(desc="It's too hard to understand.", stat_mods={}),
            ),
            EventChoice(
                name="Splash in puddles",
                skill_reqs={},
                checks=[StatCheck(STATS.CON, 1, 20, 20)],
                success=EventResult(desc="", stat_mods={STATS.WIS: +2},),
                failure=EventResult(
                    desc="You catch a cold.", stat_mods={STATS.CON: -2},
                ),
            ),
            EventChoice(
                name="Conduct a sun ritual",
                skill_reqs={},
                checks=[StatCheck(STATS.WIS, 1, 20, 20)],
                success=EventResult(desc="The rain slows.", stat_mods={STATS.WIS: +2},),
                failure=EventResult(
                    desc="Nothing happens.", stat_mods={STATS.WIS: +1},
                ),
            ),
        ],
    ),
    "leaves": Event(
        desc="Leaves for dinner.",
        choices=[
            EventChoice(
                name="Eat the green crap.",
                skill_reqs=[],
                checks=[StatCheck(STATS.WIS, num_dice=1, sides=20, dc=20)],
                success=EventResult(desc="You get it down.", stat_mods={STATS.CON: +2}),
                failure=EventResult(desc="You spit it out.", stat_mods={STATS.CON: -1}),
            ),
            EventChoice(
                name="Pretend to eat it.",
                skill_reqs=[],
                checks=[StatCheck(STATS.DEX, 1, 20, 22)],
                success=EventResult(desc="", stat_mods={STATS.CON: -1, STATS.DEX: +2},),
                failure=EventResult(desc="", stat_mods={STATS.CON: -2},),
            ),
            EventChoice(
                name="Run away from home.",
                skill_reqs=[],
                checks=[StatCheck(STATS.DEX, 1, 20, 30)],
                success=EventResult(
                    desc="You live on your own.",
                    stat_mods={STATS.WIS: +2, STATS.DEX: +2, STATS.CON: +2},
                ),
                failure=EventResult(desc="", stat_mods={},),
            ),
        ],
    ),
    "mountain": Event(
        prereq_fn=lambda player: player.stats[STATS.AGE] > 5,
        desc="You encounter a tall mountain. What do you do?",
        choices=[
            EventChoice(
                name="Hike to the top!",
                skill_reqs=[SKILLS.CLIMB],
                checks=[StatCheck(STATS.STR, num_dice=1, sides=20, dc=20)],
                success=EventResult(
                    desc="You make it to the top. What a beautiful view!",
                    stat_mods={STATS.WIS: +1, STATS.STR: +1, STATS.REP: +1},
                ),
                failure=EventResult(
                    desc="You collapse on the way up.", stat_mods={STATS.STR: +1}
                ),
            ),
            EventChoice(
                name="Investigate strange rock formation",
                skill_reqs=[SKILLS.ARCHAEOLOGY],
                checks=[StatCheck(STATS.INT, 1, 20, 23)],
                success=EventResult(
                    desc="It seems to have been built by gnomes long ago."
                    " Some scrawlings on the surface indicate directions to"
                    " an ancient dungeon.",
                    stat_mods={},
                    trigger_events=["scrawlings"],
                ),
                failure=EventResult(desc="", stat_mods={STATS.CON: -2}),
            ),
            EventChoice(
                name="Explore caves",
                skill_reqs=[],
                checks=[StatCheck(STATS.WIS, num_dice=1, sides=20, dc=20)],
                success=EventResult(
                    desc="You find a beautiful underground lake.",
                    stat_mods={STATS.WIS: +2},
                ),
                failure=EventResult(desc="You get lost in a maze of twisty passages."),
            ),
        ],
    ),
    "scrawlings": Event(
        prereq_fn=lambda player: False,
        desc="The scrawlings contain a map to a legendary amulet located"
        " under the mountain.",
        choices=[
            EventChoice(
                name="Follow the directions.",
                skill_reqs=[],
                checks=[StatCheck(STATS.WIS, num_dice=1, sides=20, dc=20)],
                success=EventResult(
                    desc="Your search leads you deep into the mountain...",
                    trigger_events=["nethack"],
                ),
                failure=EventResult(desc="You cannot find it.",),
            ),
            EventChoice(
                name="Forget about it.",
                skill_reqs=[],
                checks=[],
                success=EventResult(desc="",),
                failure=None,
            ),
        ],
    ),
    "nethack": Event(
        prereq_fn=lambda player: False,
        desc="You find yourself in the middle of an huge yet familiar dungeon.",
        choices=[
            EventChoice(
                name="Search for the amulet.",
                skill_reqs=[SKILLS.JUMP],
                checks=[
                    StatCheck(STATS.WIS, num_dice=1, sides=20, dc=20),
                    StatCheck(STATS.CON, num_dice=1, sides=20, dc=20),
                    StatCheck(STATS.LUC, num_dice=1, sides=20, dc=20),
                ],
                success=EventResult(
                    desc="You find the Amulet of Yendor.", stat_mods={STATS.PTS: 1000}
                ),
                failure=EventResult(
                    desc="You are eaten by a giant ant.", stat_mods={STATS.CON: -100}
                ),
            ),
            EventChoice(
                name="Escape while you still can.",
                skill_reqs=[],
                checks=[StatCheck(STATS.LUC, num_dice=1, sides=20, dc=15)],
                success=EventResult(desc="",),
                failure=None,
            ),
        ],
    ),
}


def fragment_desc_getter(fragments, n):
    return lambda x: " ".join(random.sample(fragments[x], n))


class BetterButton(urwid.Button):
    button_left = urwid.Text("-")
    button_right = urwid.Text("")


class SplitMenu(urwid.WidgetWrap):
    def __init__(
        self,
        title,
        choices,
        display_fn=str,
        description_fn=lambda c: "",
        is_enabled_fn=lambda c: True,
        callback=lambda c: None,
    ):
        body = [urwid.Text(title), urwid.Divider()]

        def item_chosen(button, choice):
            callback(choice)

        choices = sorted(choices, key=is_enabled_fn, reverse=True)
        for c in choices:
            if is_enabled_fn(c):
                button = BetterButton(display_fn(c))
                urwid.connect_signal(button, "click", item_chosen, c)
            else:
                button = BetterButton(("disabled", display_fn(c)))
            body.append(urwid.AttrMap(button, None, focus_map="reversed"))
        menu = urwid.SimpleFocusListWalker(body)
        listbox = ListBoxVikeys(menu)
        right_txt = urwid.Text("")
        right_fill = urwid.Filler(right_txt, valign="middle")

        def on_focus_changed():
            focused_index = menu.get_focus()[1]
            focused_choice = choices[focused_index - 2]
            right_txt.set_text(description_fn(focused_choice))

        urwid.connect_signal(menu, "modified", on_focus_changed)

        columns = urwid.Columns([listbox, right_fill])
        super().__init__(columns)


class PointBuy(urwid.WidgetWrap):
    TOTAL_POINTS = 24

    def get_points_remaining(self):
        points_remaining = PointBuy.TOTAL_POINTS
        for stat in POINT_BUY_STATS:
            val = self.stat_editors[stat].value()
            points_remaining -= min(val, 16) - 10
            if val > 16:
                points_remaining -= (val - 16) * 2
        return points_remaining

    def __init__(self, callback, bonuses):
        self.stat_editors = {}
        points_left_text = urwid.Text(f"Points left: {PointBuy.TOTAL_POINTS}")
        self.warning_text = urwid.Text("")
        self.callback = callback
        self.bonuses = bonuses

        body = [
            urwid.Text("CHOOSE YOUR STATS"),
            points_left_text,
            self.warning_text,
            urwid.Divider(),
        ]

        def on_change(*args):
            points_left_text.set_text(f"Points left: {self.get_points_remaining()}")

        stat_edit_column = [urwid.Text("STATS")]
        stat_bonus_column = [urwid.Text("CLASS BONUSES")]
        for s in POINT_BUY_STATS:
            stat_edit = IntEditArrows(f"{s.value}: ", 10)
            urwid.connect_signal(stat_edit, "postchange", on_change)
            self.stat_editors[s] = stat_edit
            stat_edit_column.append(stat_edit)
            if s in bonuses:
                stat_bonus_column.append(urwid.Text(f"+{bonuses[s]}"))
            else:
                stat_bonus_column.append(urwid.Divider())
        stat_edit_column = urwid.Pile(stat_edit_column)
        stat_bonus_column = urwid.Pile(stat_bonus_column)
        body.append(urwid.Columns([(10, stat_edit_column), stat_bonus_column]))

        menu_walker = urwid.SimpleFocusListWalker(body)
        menu = ListBoxVikeys(menu_walker)
        urwid.connect_signal(menu_walker, "modified", on_change)
        super().__init__(menu)

    def keypress(self, key, raw):
        key = super().keypress(key, raw)
        if any(editor.value() <= 0 for editor in self.stat_editors.values()):
            self.warning_text.set_text(("warn", "Stats must be above zero"))
        else:
            self.warning_text.set_text("")
        if key in ("enter", " "):
            if self.get_points_remaining() != 0:
                self.warning_text.set_text(("warn", "Must have zero points remaining."))
                return
            stats = {
                stat: editor.value() + self.bonuses.get(stat, 0)
                for (stat, editor) in self.stat_editors.items()
            }
            self.callback(stats)
            return None
        return key


class PlayerDisplay(urwid.WidgetWrap):
    def __init__(self):
        self.class_info = urwid.Text("??")
        self.stat_infos = {stat: urwid.Text("??") for stat in STATS}
        pile_contents = [self.class_info]
        pile_contents.extend([self.stat_infos[stat] for stat in STATS])
        self.skill_pile = urwid.Pile([])
        pile_contents.append(self.skill_pile)
        self.pile = urwid.Pile(pile_contents)
        self.revealed_stats = set()
        super().__init__(urwid.Filler(self.pile, "top"))

    def update(self, char_info):
        logging.debug(f"Player: {char_info}")
        if char_info.char_class is not None:
            self.class_info.set_text(char_info.char_class.value)
        for (stat, val) in char_info.stats.items():
            if stat == STATS.AGE:
                if SKILLS.TIME in char_info.skills:
                    self.revealed_stats.add(stat)
            elif val != 0:
                self.revealed_stats.add(stat)

            if stat in self.revealed_stats:
                self.stat_infos[stat].set_text(f"{stat.value}: {val}")
        self.skill_pile.contents.clear()
        for skill in sorted(char_info.skills, key=lambda s: s.value):
            self.skill_pile.contents.append((urwid.Text(skill.value), ("pack", None)))


class Game:
    def __init__(self):
        self.main_widget_container = urwid.Padding(urwid.Edit(), left=1, right=1)
        self.player_display = PlayerDisplay()
        columns = urwid.Columns([self.main_widget_container, self.player_display])
        padded = urwid.Padding(columns, left=2, right=2)
        overlay = urwid.Overlay(
            padded,
            urwid.SolidFill("\N{MEDIUM SHADE}"),
            align="center",
            width=("relative", 80),
            valign="middle",
            height=("relative", 80),
        )
        self.top = overlay
        self.player = CharInfo()
        self.seen_events = set()
        self.widgets_iter = self.play_linear()
        self.next_screen()
        self.loop = None

    def dice(self, n, s):
        """ Rolls NdS """
        if SKILLS.CLOVER in self.player.skills and s == 4:
            s = 8
        return sum(random.randint(1, s) for _ in range(n))

    def set_main_widget(self, widget):
        self.main_widget_container.original_widget = widget

    def next_screen(self):
        self.player_display.update(self.player)
        self.set_main_widget(next(self.widgets_iter))

    def on_class_chosen(self, char_class):
        self.player.char_class = char_class
        self.next_screen()

    def on_point_buy_done(self, stats):
        for (stat, val) in stats.items():
            self.player.stats[stat] = val
        self.next_screen()

    def on_skill_chosen(self, skill):
        self.player.skills.add(skill)
        self.next_screen()

    def choose_class_menu(self):
        return SplitMenu(
            "CHOOSE YOUR CLASS",
            list(CHAR_CLASSES),
            display_fn=lambda c: c.value,
            description_fn=fragment_desc_getter(CHAR_CLASS_DESC_FRAGMENTS, 3),
            callback=self.on_class_chosen,
        )

    def point_buy(self):
        return PointBuy(
            callback=self.on_point_buy_done,
            bonuses=CHAR_CLASS_STAT_BONUSES[self.player.char_class],
        )

    def player_can_choose_skill(self, skill):
        skill_prereqs = SKILL_PREREQS.get(skill, {})
        if not self.player.skills.issuperset(skill_prereqs):
            return False
        stat_prereqs = SKILL_STAT_PREREQS.get(skill, {})
        if any(self.player.stats[stat] < req for (stat, req) in stat_prereqs.items()):
            return False
        return True

    def choose_skill(self):
        skills = list(set(SKILLS).difference(self.player.skills))
        if not any(self.player_can_choose_skill(skill) for skill in skills):
            logging.warning("No skills available for player to choose!")
            return

        skill_graph = {skill: [] for skill in set(SKILLS)}
        for a1, a0s in SKILL_PREREQS.items():
            for a0 in a0s:
                skill_graph[a0].append(a1)

        no_prereqs = set(
            skill
            for skill in skills
            if (
                (
                    skill not in SKILL_PREREQS
                    or all(
                        req_skill in self.player.skills
                        for req_skill in SKILL_PREREQS[skill]
                    )
                )
            )
            and skill not in self.player.skills
        )
        agenda = list(self.player.skills | no_prereqs)
        one_off = set()
        for item in agenda:
            for next_skill in skill_graph[item]:
                if (
                    next_skill not in no_prereqs
                    and next_skill not in self.player.skills
                ):
                    one_off.add(next_skill)

        yield SplitMenu(
            "CHOOSE A SKILL",
            list(one_off | no_prereqs),
            display_fn=lambda c: c.value,
            description_fn=get_skill_desc,
            is_enabled_fn=self.player_can_choose_skill,
            callback=self.on_skill_chosen,
        )

    def on_hobby(self, hobby):
        self.player.hobby = hobby
        self.next_screen()

    def choose_hobby(self):
        return SplitMenu(
            "CHOOSE AN ACTIVITY",
            list(HOBBY),
            description_fn=fragment_desc_getter(HOBBY_DESC_FRAGMENTS, 3),
            display_fn=lambda c: c.value,
            callback=self.on_hobby,
        )

    def make_popup(self, widget):
        return urwid.Overlay(
            urwid.LineBox(widget),
            self.main_widget_container.original_widget,
            width=("relative", 100),
            height=("relative", 70),
            align="center",
            valign="middle",
        )

    def popup_message(self, text, callback):
        text = urwid.Padding(
            urwid.Filler(urwid.Text(text, align="center"), valign="top"),
            left=1,
            right=1,
        )
        ok_button = BetterButton("OK")

        def on_ok(*args):
            self.close_popup()
            callback()

        urwid.connect_signal(ok_button, "click", on_ok)
        ok_button = urwid.AttrMap(ok_button, None, focus_map="reversed")
        layout = urwid.Frame(text, footer=ok_button, focus_part="footer")
        return self.make_popup(layout)

    def close_popup(self):
        self.set_main_widget(self.main_widget_container.original_widget.bottom_w)

    def roll_stat_check(self, stat, num_dice, sides):
        return self.player.stats[stat] + self.dice(num_dice, sides)

    def play_random_event(self):
        events = list(
            (name, event)
            for (name, event) in EVENTS.items()
            if name not in self.seen_events and event.prereq_fn(self.player)
        )
        if not events:
            logging.warning("Ran out of random events")
            return
        (name, _) = random.choice(events)
        yield from self.play_event(name)

    def play_event(self, event_name):
        logging.info(f"Triggered {event_name} event")
        self.seen_events.add(event_name)
        event = EVENTS[event_name]
        choice = None

        def on_choice(selected):
            nonlocal choice
            choice = selected
            self.next_screen()

        def player_has_skill_prereqs(choice):
            return self.player.skills.issuperset(choice.skill_reqs)

        def description_fn(choice):
            desc = ""
            if choice.skill_reqs:
                desc += "Required skills:\n"
            for skill in choice.skill_reqs:
                desc += f" {skill.value}"
            return desc

        yield SplitMenu(
            event.desc,
            event.choices,
            description_fn=description_fn,
            display_fn=lambda choice: choice.name,
            is_enabled_fn=player_has_skill_prereqs,
            callback=on_choice,
        )
        logging.info(f"Player chose {choice.name}")
        assert choice is not None
        overall_success = True
        msg = ""
        if choice.checks:
            for stat_check in choice.checks:
                (stat, num_dice, sides, dc) = stat_check
                total = self.roll_stat_check(stat, num_dice, sides)
                check_success = total >= dc
                if not check_success:
                    overall_success = False
                msg += f'{"SUCCESS" if check_success else "FAILURE"}'
                msg += f" {num_dice}d{sides} + {stat.value} = {total} vs {dc}\n\n"
        result = choice.success if overall_success else choice.failure
        msg += result.desc
        for (stat, mod) in result.stat_mods.items():
            msg += f" {mod:+} {stat.value}"
            self.player.stats[stat] += mod
        yield self.popup_message(msg, self.next_screen)

        for event_name in result.trigger_events:
            yield from self.play_event(event_name)

    def play_hobby(self):
        yield self.choose_hobby()
        if self.player.hobby == HOBBY.READ and SKILLS.READ not in self.player.skills:
            yield self.popup_message(
                "You don't know how to read!", self.next_screen,
            )
        else:
            stat = {
                HOBBY.RUN: STATS.DEX,
                HOBBY.READ: STATS.INT,
                HOBBY.BIRDWATCHING: STATS.WIS,
            }[self.player.hobby]
            bonus = self.dice(1, 4)
            self.player.stats[stat] += bonus
            yield self.popup_message(f"+1d4={bonus} {stat.value}!", self.next_screen)

    def play_linear(self):
        yield self.choose_class_menu()
        yield self.point_buy()
        self.player.stats[STATS.AGE] += 1
        yield from self.choose_skill()
        self.player.stats[STATS.AGE] += 1
        yield from self.choose_skill()
        yield from self.play_hobby()
        while True:
            yield from self.play_random_event()
            yield from self.choose_skill()
            self.player.stats[STATS.AGE] += 1
            if self.player.stats[STATS.AGE] > 5:
                yield self.aging_check()
            if self.player.stats[STATS.CON] <= 0:
                yield self.popup_message("YOU DIE", self.next_screen)
                break
        raise urwid.ExitMainLoop()

    def aging_check(self):
        msg = "TIME TAKES ITS TOLL"
        con_debuff = self.dice(2, 4)
        self.player.stats[STATS.CON] -= con_debuff
        msg += f"\n\n-2d4=-{con_debuff} CON"
        return self.popup_message(msg, self.next_screen)

    def run(self):
        self.loop = urwid.MainLoop(self.top, palette=PALETTE)
        self.loop.run()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
