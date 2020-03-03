#!/usr/bin/env python3
from enum import Enum

import urwid


def menu(title, choices, display_fn=str):
    selected = None
    body = [urwid.Text(title), urwid.Divider()]

    def item_chosen(button, choice):
        nonlocal selected
        selected = choice
        raise urwid.ExitMainLoop()

    for c in choices:
        button = urwid.Button(display_fn(c))
        urwid.connect_signal(button, "click", item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))
    widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
    urwid.MainLoop(widget).run()
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
