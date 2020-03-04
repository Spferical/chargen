#!/usr/bin/env python3
from enum import Enum
import random
import logging

import urwid


logging.basicConfig(filename="log.txt", level=logging.DEBUG)


class CharInfo:
    def __init__(self):
        self.stats = {stat: 0 for stat in STATS}
        self.char_class = None
        self.skills = set()


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


class STATS(Enum):
    STR = "STR"
    DEX = "DEX"
    CON = "CON"
    INT = "INT"
    WIS = "WIS"
    CHA = "CHA"
    LUC = "LUC"


class SKILLS(Enum):
    JUMP = "Jumping"
    CLIMB = "Climbing"


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


SKILL_DESCS = {
    SKILLS.JUMP: "You can jump very high. Gives +5 on jump height rolls.",
    SKILLS.CLIMB: "You can scale ropes, trees, walls, and more with ease."
    "Adds a d12 to rolls involving scaling obstacles.",
}


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
        callback=lambda c: None,
    ):
        body = [urwid.Text(title), urwid.Divider()]

        def item_chosen(button, choice):
            callback(choice)

        for c in choices:
            button = BetterButton(display_fn(c))
            urwid.connect_signal(button, "click", item_chosen, c)
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
        for stat in STATS:
            val = self.stat_editors[stat].value()
            points_remaining += 10 - val
        return points_remaining

    def __init__(self, callback, bonuses):
        self.stat_editors = {}
        points_left_text = urwid.Text(f"Points left: {PointBuy.TOTAL_POINTS}")
        self.callback = callback
        self.bonuses = bonuses

        body = [urwid.Text("CHOOSE YOUR STATS"), points_left_text, urwid.Divider()]

        def on_change(*args):
            points_left_text.set_text(f"Points left: {self.get_points_remaining()}")

        stat_edit_column = [urwid.Text("STATS")]
        stat_bonus_column = [urwid.Text("CLASS BONUSES")]
        for s in STATS:
            stat_edit = IntEditArrows(f"{s.value}: ", 10)
            urwid.connect_signal(stat_edit, "postchange", on_change)
            self.stat_editors[s] = stat_edit
            stat_edit_column.append(stat_edit)
            stat_bonus_column.append(urwid.Text(f"+{bonuses.get(s, 0)}"))
        stat_edit_column = urwid.Pile(stat_edit_column)
        stat_bonus_column = urwid.Pile(stat_bonus_column)
        body.append(urwid.Columns([(10, stat_edit_column), stat_bonus_column]))

        menu_walker = urwid.SimpleFocusListWalker(body)
        menu = ListBoxVikeys(menu_walker)
        urwid.connect_signal(menu_walker, "modified", on_change)
        super().__init__(menu)

    def keypress(self, key, raw):
        key = super().keypress(key, raw)
        if key in ("enter", " ") and self.get_points_remaining() == 0:
            stats = {
                stat: editor.value() + self.bonuses.get(stat, 0)
                for (stat, editor) in self.stat_editors.items()
            }
            self.callback(stats)
            return None
        return key


def char_class_desc(cclass):
    return " ".join(random.sample(CHAR_CLASS_DESC_FRAGMENTS[cclass], 3))


class Game:
    def __init__(self):
        placeholder = urwid.SolidFill()
        padded = urwid.Padding(placeholder, left=2, right=2)
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
        self.widgets_iter = self.play_linear()
        self.next_screen()

    def next_screen(self):
        self.set_main_widget(next(self.widgets_iter))

    def set_main_widget(self, widget):
        self.top.top_w.original_widget = widget

    def on_class_chosen(self, char_class):
        self.player.char_class = char_class
        self.next_screen()

    def on_point_buy_done(self, stats):
        self.player.stats = stats
        self.next_screen()

    def on_skill_chosen(self, skill):
        self.player.skills.add(skill)
        self.next_screen()

    def play_linear(self):
        yield SplitMenu(
            "CHOOSE YOUR CLASS",
            list(CHAR_CLASSES),
            display_fn=lambda c: c.value,
            description_fn=char_class_desc,
            callback=self.on_class_chosen,
        )

        yield PointBuy(
            callback=self.on_point_buy_done,
            bonuses=CHAR_CLASS_STAT_BONUSES[self.player.char_class],
        )

        yield SplitMenu(
            "CHOOSE A SKILL",
            list(set(SKILLS).difference(self.player.skills)),
            display_fn=lambda c: c.value,
            description_fn=lambda skill: SKILL_DESCS[skill],
            callback=self.on_skill_chosen,
        )

    def run(self):
        urwid.MainLoop(self.top, palette=[("reversed", "standout", "")]).run()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
