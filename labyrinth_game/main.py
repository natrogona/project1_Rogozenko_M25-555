#!/usr/bin/env python3
"""Главный модуль игры 'Лабиринт сокровищ'."""

from labyrinth_game.constants import COMMANDS
from labyrinth_game.player_actions import (
    get_input,
    move_player,
    show_inventory,
    take_item,
    use_item,
)
from labyrinth_game.utils import (
    attempt_open_treasure,
    describe_current_room,
    show_help,
    solve_puzzle,
)


def process_command(game_state: dict, command_line: str) -> None:
    """
    Обрабатывает команду, введенную пользователем.

    Args:
        game_state: Состояние игры
        command_line: Введенная команда
    """
    parts = command_line.strip().lower().split(maxsplit=1)

    if not parts:
        return

    command = parts[0]
    argument = parts[1] if len(parts) > 1 else ""

    # Обработка команд
    match command:
        case "look":
            describe_current_room(game_state)

        case "go":
            if argument:
                move_player(game_state, argument)
            else:
                print("Укажите направление: north, south, east, west")

        case "north" | "south" | "east" | "west":
            # Поддержка односложных команд направления
            move_player(game_state, command)

        case "take":
            if argument:
                take_item(game_state, argument)
            else:
                print("Укажите, что хотите поднять.")

        case "use":
            if argument:
                use_item(game_state, argument)
            else:
                print("Укажите, что хотите использовать.")

        case "inventory":
            show_inventory(game_state)

        case "solve":
            # В treasure_room solve открывает сундук
            if game_state["current_room"] == "treasure_room":
                attempt_open_treasure(game_state)
            else:
                solve_puzzle(game_state)

        case "help":
            show_help(COMMANDS)

        case "quit" | "exit":
            print("Спасибо за игру!")
            game_state["game_over"] = True

        case _:
            print(f"Неизвестная команда: {command}. Введите 'help' для списка команд.")


def main() -> None:
    """Точка входа в игру."""
    # Инициализация состояния игры
    game_state = {
        "player_inventory": [],
        "current_room": "entrance",
        "game_over": False,
        "steps_taken": 0,
    }

    # Приветствие
    print("\n" + "=" * 60)
    print("ДОБРО ПОЖАЛОВАТЬ В ЛАБИРИНТ СОКРОВИЩ!")
    print("=" * 60)
    print(
        "\nВы — отважный исследователь древнего лабиринта."
        "\nВаша цель — найти главное сокровище!"
        "\nВведите 'help' для списка команд.\n"
    )

    # Описание стартовой комнаты
    describe_current_room(game_state)

    # Основной игровой цикл
    while not game_state["game_over"]:
        command_line = get_input("\n> ")
        process_command(game_state, command_line)

    # Финальное сообщение
    print("\n" + "=" * 60)
    print("ИГРА ОКОНЧЕНА")
    print("=" * 60)
    print(f"Вы сделали {game_state['steps_taken']} шагов.")
    print(f"Предметов в инвентаре: {len(game_state['player_inventory'])}")


if __name__ == "__main__":
    main()
