"""Функции, связанные с действиями игрока."""

from labyrinth_game.constants import ROOMS
from labyrinth_game.utils import describe_current_room, random_event


def get_input(prompt: str = "> ") -> str:
    """
    Получает ввод от пользователя с обработкой прерываний.

    Args:
        prompt: Текст приглашения для ввода

    Returns:
        Введенная пользователем строка
    """
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def show_inventory(game_state: dict) -> None:
    """Отображает содержимое инвентаря игрока."""
    inventory = game_state["player_inventory"]

    if inventory:
        print(f"\nВаш инвентарь: {', '.join(inventory)}")
    else:
        print("\nВаш инвентарь пуст.")


def move_player(game_state: dict, direction: str) -> None:
    """
    Перемещает игрока в указанном направлении.

    Args:
        game_state: Состояние игры
        direction: Направление движения (north, south, east, west)
    """
    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    if direction not in room_data["exits"]:
        print("Нельзя пойти в этом направлении.")
        return

    next_room = room_data["exits"][direction]

    # Проверка доступа к treasure_room
    if next_room == "treasure_room":
        if "rusty_key" in game_state["player_inventory"]:
            print(
                "Вы используете найденный ключ, чтобы открыть путь в комнату сокровищ."
            )
        else:
            print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
            return

    # Перемещение
    game_state["current_room"] = next_room
    game_state["steps_taken"] += 1

    # Описание новой комнаты
    describe_current_room(game_state)

    # Случайное событие
    random_event(game_state)


def take_item(game_state: dict, item_name: str) -> None:
    """
    Подбирает предмет из текущей комнаты.

    Args:
        game_state: Состояние игры
        item_name: Название предмета
    """
    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    # Специальная обработка для treasure_chest
    if item_name == "treasure_chest":
        print("Вы не можете поднять сундук, он слишком тяжелый.")
        return

    if item_name in room_data["items"]:
        room_data["items"].remove(item_name)
        game_state["player_inventory"].append(item_name)
        print(f"Вы подняли: {item_name}")
    else:
        print("Такого предмета здесь нет.")


def use_item(game_state: dict, item_name: str) -> None:
    """
    Использует предмет из инвентаря.

    Args:
        game_state: Состояние игры
        item_name: Название предмета
    """
    if item_name not in game_state["player_inventory"]:
        print("У вас нет такого предмета.")
        return

    # Обработка использования разных предметов
    if item_name == "torch":
        print("Вы зажгли факел. Стало светлее!")

    elif item_name == "sword":
        print("Вы держите меч. Чувствуете себя увереннее!")

    elif item_name == "bronze_box":
        print("Вы открываете бронзовую шкатулку...")
        if "rusty_key" not in game_state["player_inventory"]:
            print("Внутри ржавый ключ!")
            game_state["player_inventory"].append("rusty_key")
        else:
            print("Шкатулка пуста.")

    elif item_name == "ancient_book":
        print("Вы листаете древнюю книгу. В ней мудрые советы о лабиринтах.")

    elif item_name == "treasure_key":
        print("Золотой ключ сияет в ваших руках. Он откроет путь к сокровищам.")

    elif item_name == "magic_amulet":
        print("Амулет излучает магическую энергию. Вы чувствуете защиту.")

    elif item_name == "coin":
        print("Блестящая монетка. Может пригодиться!")

    else:
        print("Вы не знаете, как использовать этот предмет.")
