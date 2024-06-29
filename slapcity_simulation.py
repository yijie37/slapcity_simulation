from constants import ARENA_INFO, TOTAL_ARENAS
from utils import Player, Arena, info

NUM_DICKIES = 30
MISSION_TIMES = 10

def main():
    # arenas
    arenas = []
    for i in range(TOTAL_ARENAS):
        arena = Arena(i)
        arenas.append(arena)

    # player
    player = Player(num_dickies=NUM_DICKIES, mission_times=MISSION_TIMES)

    # before
    items0, _ = player.player_info()

    # do missions
    player.do_missions(arenas=arenas)

    # after
    items1, total_coin = player.player_info()

    # get gain info
    info(total_coin, items0, items1, ARENA_INFO)

if __name__ == '__main__':
    main()