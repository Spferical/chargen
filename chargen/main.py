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
    ],
    CHAR_CLASSES.MAGIC_USER: [
        "Eat manna.",
        "Abracadabra.",
        "Big pointy hat.",
        "Zip zoop zap!",
        "Stroke the beard.",
        "You shall not pass.",
        "Accurate missile targeting.",
    ],
    CHAR_CLASSES.CLERIC: [
        "Pray.",
        "Wololo.",
        "Fanciest hat of them all.",
        "Dear lord.",
        "Get more HPs.",
        "Not afraid of skeletons.",
        "The protection racket has been nerfed.",
    ],
}


class BetterButton(urwid.Button):
    button_left = urwid.Text("-")
    button_right = urwid.Text("")


def menu(title, choices, display_fn=str, description_fn=lambda c: ""):
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
    menu_walker = urwid.SimpleFocusListWalker(body)
    menu_widget = urwid.ListBox(menu_walker)
    right_txt = urwid.Text("")

    def on_focus_changed():
        focused_index = menu_widget.get_focus()[1]
        focused_choice = choices[focused_index - 2]
        right_txt.set_text(description_fn(focused_choice))

    urwid.connect_signal(menu_walker, "modified", on_focus_changed)

    right_fill = urwid.Filler(right_txt, valign="top")
    right_pad = urwid.Padding(right_fill, left=1, right=1)
    columns = urwid.Columns([menu_widget, right_pad])
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


def char_class_desc(cclass):
    text = ""
    for _ in range(3):
        text += random.choice(CHAR_CLASS_DESC_FRAGMENTS[cclass]) + " "
    return text


def choose_class():
    print(
        menu(
            "CHOOSE YOUR CLASS",
            list(CHAR_CLASSES),
            display_fn=lambda c: c.value,
            description_fn=char_class_desc,
        )
    )


def main():
    choose_class()


if __name__ == "__main__":
    main()
