from model.hero import *
from model.map import Map
from model.parameters import Parameters
from model.state import State
from model.abilites import AbilityType
from model.teams import Teams
import json
import random
import time

game = json.loads(input())
game_map = Map(game)  # карта игрового мира
game_params = Parameters(game)  # параметры игры
game_teams = Teams(game)  # моя команда

while True:
    try:
        """ Получение состояния игры """
        state = State(input(), game_teams, game_params)

        my_buildings = state.my_buildings()
        my_squads = state.my_squads()
        # сортируем по остаточному пути
        my_squads.sort(key=lambda c: c.way.left, reverse=False)

        enemy_buildings = state.enemy_buildings()
        enemy_squads = state.enemy_squads()

        neutral_buildings = state.neutral_buildings()

        forges_buildings = state.forges_buildings()

        """ Играем за рунного кузнеца """
        if game_teams.my_her.hero_type == HeroType.BlackSmith:
            # Проверяем доступность абилки Щит
            if state.ability_ready(AbilityType.Armor):
                print(game_teams.my_her.armor(my_buildings[0].id))

            # Проверяем доступность абилки Разрушение
            if len(enemy_squads) > 4:
                if state.ability_ready(AbilityType.Area_damage):
                    location = game_map.get_squad_center_position(enemy_squads[2])
                    print(game_teams.my_her.area_damage(location))

            # Upgrade башни
            if my_buildings[0].level.id < len(game_params.tower_levels):
                # Если хватает стоимости на upgrade
                update_coast = game_params.get_tower_level(my_buildings[0].level.id + 1).update_coast
                if update_coast < my_buildings[0].creeps_count:
                    print(game_teams.my_her.upgrade_tower(my_buildings[0].id))
                    my_buildings[0].creeps_count -= update_coast

            # Атакуем башню противника
            # определяем расстояние между башнями
            distance = game_map.towers_distance(my_buildings[0].id, enemy_buildings[0].id)

            # определяем сколько тиков идти до нее со стандартной скоростью
            ticks = distance / game_params.creep.speed
            # new_ticks = new_dist / game_params.creep.speed

            # определяем прирост башни в соответствии с ее уровнем
            enemy_creeps = 0
            if enemy_buildings[0].creeps_count >= enemy_buildings[0].level.player_max_count:
                # если текущее количество крипов больше чем положено по уровню
                enemy_creeps = enemy_buildings[0].creeps_count
            else:
                # если меньше - будет прирост
                grow_creeps = ticks / enemy_buildings[0].level.creep_creation_time
                enemy_creeps = enemy_buildings[0].creeps_count + grow_creeps
                if enemy_creeps >= enemy_buildings[0].level.player_max_count:
                    enemy_creeps = enemy_buildings[0].level.player_max_count
            # определяем количество крипов с учетом бонуса защиты
            enemy_defence = enemy_creeps * (1 + enemy_buildings[0].DefenseBonus)

            # если получается в моей башне крипов больше + 4 на червя - идем на врага всей толпой
            i = 0
            for my_building in my_buildings:
                if i < len(neutral_buildings):
                    i += 1
                dist1 = game_map.towers_distance(my_building.id, neutral_buildings[i].id)
                dist2 = game_map.towers_distance(my_building.id, neutral_buildings[0].id)
                if enemy_defence + 4 < my_building.creeps_count:
                    print(game_teams.my_her.move(my_building.id, enemy_buildings[0].id, 1/2))
                    print(game_teams.my_her.move(my_building.id, forges_buildings[0].id, 1/2))
                if enemy_defence == my_building.creeps_count:
                    print(game_teams.my_her.move(my_building.id, enemy_buildings[0].id, 1))
                if dist1 < dist2:
                    if enemy_defence - 3 == my_building.creeps_count:
                        print(game_teams.my_her.move(my_building.id, neutral_buildings[i].id, 1))
                elif dist1 >= dist2:
                    if enemy_defence - 3 == my_building.creeps_count:
                        print(game_teams.my_her.move(my_building.id, neutral_buildings[0].id, 1))
                else:
                    print(game_teams.my_her.move(my_building.id, enemy_buildings[0].id, 1))


        # Применение абилки ускорение
        if len(my_squads) > 4:
            if state.ability_ready(AbilityType.Speed_up):
                location = game_map.get_squad_center_position(my_squads[2])
                print(game_teams.my_her.speed_up(location))


    except Exception as e:
        print(str(e))
    finally:
        """ Требуется для получения нового состояния игры  """
        print("end")
