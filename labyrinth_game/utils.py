"""Вспомогательные функции для игры."""

import math

from labyrinth_game.constants import (
    EVENT_PROBABILITY,
    EVENT_TYPES,
    PUZZLE_ALTERNATIVES,
    ROOMS,
    TRAP_DAMAGE_RANGE,
    TRAP_DAMAGE_THRESHOLD,
)


def describe_current_room(game_state: dict) -> None:
    """Выводит описание текущей комнаты игрока."""
    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    # Название комнаты
    print(f"\n== {current_room.upper().replace('_', ' ')} ==")

    # Описание комнаты
    print(room_data["description"])

    # Предметы в комнате
    if room_data["items"]:
        print(f"Заметные предметы: {', '.join(room_data['items'])}")

    # Доступные выходы
    exits = ", ".join(room_data["exits"].keys())
    print(f"Выходы: {exits}")

    # Наличие загадки
    if room_data["puzzle"]:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def show_help(commands: dict) -> None:
    """Выводит список доступных команд."""
    print("\nДоступные команды:")
    for command, description in commands.items():
        print(f"  {command:<16} - {description}")


def pseudo_random(seed: int, modulo: int) -> int:
    """
    Генерирует псевдослучайное число на основе seed.

    Args:
        seed: Исходное значение для генерации
        modulo: Диапазон результата [0, modulo)

    Returns:
        Псевдослучайное целое число
    """
    value = math.sin(seed * 12.9898) * 43758.5453
    fractional_part = value - math.floor(value)
    return int(fractional_part * modulo)


def trigger_trap(game_state: dict) -> None:
    """
    Активирует ловушку с негативными последствиями для игрока.

    Если у игрока есть предметы, теряет случайный предмет.
    Если инвентарь пуст, получает урон и может погибнуть.
    """
    print("Ловушка активирована! Пол задрожал...")

    inventory = game_state["player_inventory"]

    if inventory:
        # Теряем случайный предмет
        index = pseudo_random(game_state["steps_taken"], len(inventory))
        lost_item = inventory.pop(index)
        print(f"Вы потеряли предмет: {lost_item}!")
    else:
        # Получаем урон
        damage_roll = pseudo_random(game_state["steps_taken"], TRAP_DAMAGE_RANGE)
        if damage_roll < TRAP_DAMAGE_THRESHOLD:
            print("Ловушка оказалась смертельной... Вы погибли.")
            game_state["game_over"] = True
        else:
            print("Вам удалось уцелеть, но было страшно!")


def random_event(game_state: dict) -> None:
    """
    Генерирует случайное событие во время перемещения игрока.

    Возможные события:
    - Находка монеты
    - Испуг от шороха
    - Срабатывание ловушки
    """
    # Проверяем, произойдет ли событие
    if pseudo_random(game_state["steps_taken"], EVENT_PROBABILITY) != 0:
        return

    # Выбираем тип события
    event_type = pseudo_random(game_state["steps_taken"] + 1, EVENT_TYPES)
    current_room = game_state["current_room"]

    if event_type == 0:
        # Находка
        print("\nВы нашли на полу монетку!")
        ROOMS[current_room]["items"].append("coin")

    elif event_type == 1:
        # Испуг
        print("\nВы слышите шорох в темноте...")
        if "sword" in game_state["player_inventory"]:
            print("Вы отпугиваете существо мечом!")

    elif event_type == 2:
        # Ловушка в trap_room без факела
        if (
            current_room == "trap_room"
            and "torch" not in game_state["player_inventory"]
        ):
            print("\nОпасность! Темнота скрывает ловушки!")
            trigger_trap(game_state)


def check_answer(answer: str, correct: str) -> bool:
    """
    Проверяет правильность ответа на загадку.

    Поддерживает альтернативные варианты ответов.
    """
    answer_lower = answer.lower().strip()

    # Проверяем прямое совпадение
    if answer_lower == correct.lower():
        return True

    # Проверяем альтернативные варианты
    if correct in PUZZLE_ALTERNATIVES:
        return answer_lower in [alt.lower() for alt in PUZZLE_ALTERNATIVES[correct]]

    return False


def solve_puzzle(game_state: dict) -> None:
    """Позволяет игроку решить загадку в текущей комнате."""
    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    if not room_data["puzzle"]:
        print("Загадок здесь нет.")
        return

    question, correct_answer = room_data["puzzle"]
    print(f"\n{question}")

    from labyrinth_game.player_actions import get_input

    answer = get_input("Ваш ответ: ")

    if check_answer(answer, correct_answer):
        print("Верно! Загадка решена.")
        room_data["puzzle"] = None

        # Награда за решение загадки
        if current_room == "trap_room":
            print("Плиты стабилизировались. Теперь здесь безопаснее.")
        elif current_room == "library":
            if "treasure_key" not in game_state["player_inventory"]:
                print("Из свитка выпал золотой ключ!")
                game_state["player_inventory"].append("treasure_key")
        elif current_room == "hall":
            if "magic_amulet" not in game_state["player_inventory"]:
                print("Пьедестал открылся, внутри амулет!")
                game_state["player_inventory"].append("magic_amulet")
    else:
        print("Неверно. Попробуйте снова.")
        # Наказание за неверный ответ в trap_room
        if current_room == "trap_room":
            trigger_trap(game_state)


def attempt_open_treasure(game_state: dict) -> None:
    """
    Попытка открыть сундук с сокровищами.

    Можно открыть ключом treasure_key или кодом.
    """
    current_room = game_state["current_room"]

    if current_room != "treasure_room":
        print("Здесь нет сундука с сокровищами.")
        return

    # Проверка наличия ключа
    if "treasure_key" in game_state["player_inventory"]:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        if "treasure_chest" in ROOMS[current_room]["items"]:
            ROOMS[current_room]["items"].remove("treasure_chest")
        print("\nВ сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
        return

    # Попытка ввести код
    from labyrinth_game.player_actions import get_input

    response = get_input("Сундук заперт. Хотите попробовать ввести код? (да/нет): ")

    if response.lower() in ["да", "yes", "y"]:
        code = get_input("Введите код: ")
        puzzle = ROOMS[current_room]["puzzle"]

        if puzzle and check_answer(code, puzzle[1]):
            print("Код верный! Сундук открывается.")
            if "treasure_chest" in ROOMS[current_room]["items"]:
                ROOMS[current_room]["items"].remove("treasure_chest")
            print("\nВ сундуке сокровище! Вы победили!")
            game_state["game_over"] = True
        else:
            print("Код неверный. Сундук остается закрытым.")
    else:
        print("Вы отступаете от сундука.")
