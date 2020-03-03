#!/usr/bin/env python3
from enum import Enum

import urwid


class BetterButton(urwid.Button):
    button_left = urwid.Text("-")
    button_right = urwid.Text("")


def menu(title, choices, display_fn=str):
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
    menu_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
    right_txt = urwid.Text("foo")
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
    urwid.MainLoop(padded, palette=[("reversed", "standout", "")]).run()
    return selected


class CLASSES(Enum):
    FIGHTING_MAN = "Fighting Man"
    MAGIC_USER = "Magic User"
    CLERIC = "Cleric"


def choose_class():
    print(menu("CHOOSE YOUR CLASS", list(CLASSES), display_fn=lambda c: c.value))


def main():
    choose_class()


if __name__ == "__main__":
    main()
