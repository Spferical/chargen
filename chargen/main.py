#!/usr/bin/env python3
from enum import Enum
import random
import logging

import urwid


logging.basicConfig(filename="chargen.log", level=logging.DEBUG)


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
    ],
    CHAR_CLASSES.CLERIC: [
        "Pray.",
        "Wololo.",
        "Fanciest hat of them all.",
        "Dear lord.",
        "Get more HPs.",
        "Not afraid of skeletons.",
        "The protection racket has been nerfed.",
        "Turn into stone.",
        "Turn spooky bois right round.",
    ],
}


class BetterButton(urwid.Button):
    button_left = urwid.Text("-")
    button_right = urwid.Text("")


def split_menu(title, choices, display_fn=str, description_fn=lambda c: ""):
    selected = None
    body = [urwid.Text(title), urwid.Divider()]

    def item_chosen(button, choice):
        nonlocal selected
        selected = choice
        raise urwid.ExitMainLoop()

    for c in choices:
        button = BetterButton(display_fn(c))
        urwid.connect_signal(button, "click", item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))
    menu = urwid.SimpleFocusListWalker(body)
    listbox = urwid.ListBox(menu)
    right_txt = urwid.Text("")

    def on_focus_changed():
        focused_index = menu.get_focus()[1]
        focused_choice = choices[focused_index - 2]
        right_txt.set_text(description_fn(focused_choice))

    urwid.connect_signal(menu, "modified", on_focus_changed)

    right_fill = urwid.Filler(right_txt, valign="top")
    right_pad = urwid.Padding(right_fill, left=1, right=1)
    columns = urwid.Columns([listbox, right_pad])
    padded = urwid.Padding(columns, left=2, right=2)
    overlay = urwid.Overlay(
        padded,
        urwid.SolidFill("\N{MEDIUM SHADE}"),
        align="center",
        width=("relative", 60),
        valign="middle",
        height=("relative", 60),
    )
    urwid.MainLoop(overlay, palette=[("reversed", "standout", "")]).run()
    return selected


def point_buy():
    total_points = 24
    body = [urwid.Text("CHOOSE YOUR STATS"), urwid.Divider()]
    points_left_text = urwid.Text(f"Points left: {total_points}")
    body.append(points_left_text)
    stat_editors = {}

    def get_points_remaining():
        points_remaining = total_points
        for stat in STATS:
            val = stat_editors[stat].value()
            points_remaining += 10 - val
        return points_remaining

    def on_change(*args):
        points_left_text.set_text(f"Points left: {get_points_remaining()}")

    for s in STATS:
        stat_edit = urwid.IntEdit(s.value + "=", 10)
        urwid.connect_signal(stat_edit, "postchange", on_change)
        stat_editors[s] = stat_edit
        body.append(stat_edit)
    menu_walker = urwid.SimpleFocusListWalker(body)
    menu = urwid.ListBox(menu_walker)

    def unhandled_input(key):
        if key == "enter":
            if get_points_remaining() == 0:
                raise urwid.ExitMainLoop()

    urwid.connect_signal(menu_walker, "modified", on_change)
    loop = urwid.MainLoop(menu, unhandled_input=unhandled_input)
    loop.run()
    return {stat: editor.value() for (stat, editor) in stat_editors.items()}


def char_class_desc(cclass):
    text = ""
    for _ in range(3):
        text += random.choice(CHAR_CLASS_DESC_FRAGMENTS[cclass]) + " "
    return text


def choose_class():
    return split_menu(
        "CHOOSE YOUR CLASS",
        list(CHAR_CLASSES),
        display_fn=lambda c: c.value,
        description_fn=char_class_desc,
    )


def main():
    char_class = choose_class()
    stats = point_buy()
    print(char_class, stats)


if __name__ == "__main__":
    main()
