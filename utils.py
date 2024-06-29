from constants import *
from collections import defaultdict
import random

class Arena(object):
    def __init__(self, i):
        self.arena_index = i
        self.arena_info = ARENA_INFO[i] 
        self.arena_probs = \
            self.arena_info[AREANA_SELECTIONS.COIN_PROBS] + \
            self.arena_info[AREANA_SELECTIONS.ITEM_PROBS] + \
            [self.arena_info[AREANA_SELECTIONS.LOOT_LOSS_PROB]]
        self.arena_probs = [p / sum(self.arena_probs) for p in self.arena_probs]

        self.acc_probs = []
        for i in range(len(self.arena_probs)):
            self.acc_probs.append( sum([self.arena_probs[j] for j in range(i + 1)]) )

    def do_mission(self):
        p = random.random()
        select = -1
        for i in range(len(self.acc_probs)):
            if p < self.acc_probs[i]:
                select = i
                break
        
        if select == len(self.acc_probs) - 1:
            # loot loss
            coin_gain = 0
            item_gain = -1
            item_loss = 1
        else:
            if select < 3:
                coin_range = self.arena_info[AREANA_SELECTIONS.COIN_RANGES][select]
                coin_gain = random.randint(coin_range[0], coin_range[1])
                item_gain = -1
                item_loss = -1
            elif select == 3:
                coin_gain = 0
                item_gain = 2 * self.arena_index + (select - 3)
                item_loss = -1
            else:
                coin_gain = 0
                item_gain = -1
                item_loss = 1

        return {
            'coin_gain': coin_gain,
            'item_gain': item_gain,
            'item_loss': item_loss
        }


class Dickey(object):
    def __init__(self):
        self.exp = DICKY_START_EXP
        self.items = []
        for i in range(3):
            self.items.append(random.randint(0, 9))
        self.time_costs = 0
        self.coin_gain = 0
        self.exp_gain = 0

    def do_one_mission(self, arenas):
        arena_idx = random.randint(0, TOTAL_ARENAS - 1)
        arena_info = ARENA_INFO[arena_idx]
        mission_result = arenas[arena_idx].do_mission()
        mission_time = arena_info[AREANA_SELECTIONS.MISSION_TIME]
        lost_item = -1
        if mission_result['item_loss'] == 1:
            # decide which item to loss
            items_probs = [ITEM_LOOT_LOSS_RATE[i] for i in self.items]
            items_probs = [p / sum(items_probs) for p in items_probs]
            acc_probs = []
            for i in range(len(items_probs)):
                acc_probs.append( sum([items_probs[j] for j in range(i + 1)]) )
            p = random.random()
            select = -1
            for i in range(len(acc_probs)):
                if p < acc_probs[i]:
                    select = i
                    break
            if select != -1:
                lost_item = self.items[select]
                new_items = [item for item in self.items if item != lost_item]
                self.items = new_items
        self.time_costs += mission_time

        return {
            'coin_gain': mission_result['coin_gain'],
            'item_gain': mission_result['item_gain'],
            'item_loss': lost_item,
            'mission_time': mission_time
        }

class Player(object):
    def __init__(self, num_dickies, mission_times):
        self.mission_times = mission_times
        self.dickies = []
        self.total_coin = 0
        self.items = defaultdict(int)
        for i in range(num_dickies):
            dicky = Dickey()
            self.dickies.append(dicky)
        for dicky in self.dickies:
            for item in dicky.items:
                self.items[item] += 1

    def do_missions(self, arenas):
        for i in range(self.mission_times):
            items_gained = defaultdict(int)
            for dicky in self.dickies:
                result = dicky.do_one_mission(arenas)
                # print(i, result)
                self.total_coin += result['coin_gain']
                if result['item_gain'] >= 0:
                    self.items[result['item_gain']] += 1
                    items_gained[result['item_gain']] += 1
                if result['item_loss'] >= 0 and self.items[result['item_loss']] > 0:
                    self.items[result['item_loss']] -= 1
            # put on items
            for dicky in self.dickies:
                cnt = len(dicky.items)
                if cnt == 3:
                    continue
                for item in items_gained:
                    if item not in dicky.items:
                        dicky.items.append(item)
                        items_gained[item] -= 1
                        cnt += 1
                        if cnt == 3:
                            break
                    
                
    def player_info(self):
        self.items = {k: self.items[k] for k in range(TOTAL_ITEMS)}
        return self.items.copy(), self.total_coin


def info(coin_gain, items_before, items_after, arena_info):
    total_items_value = 0
    for i in range(TOTAL_ITEMS):
        arena_idx = i // 2
        item_idx = i % 2
        value_change = (items_after[i] - items_before[i]) * arena_info[arena_idx][AREANA_SELECTIONS.ITEM_PRICES][item_idx]
        total_items_value += value_change

    print('Total Coin Gain: ', coin_gain)
    print('Items Ghange: ')
    print('IDX\t%25s\tBEFORE\tAFTER\tDIFF' % 'ITEM_NAME')
    for i in range(TOTAL_ITEMS):
        print('%d\t%25s\t%d\t%d\t%d' % (i, ITEM_NAME[i], items_before[i], items_after[i], items_after[i] - items_before[i]))
    print('Items Value Change: ', total_items_value)
    print('Total Gain: ', coin_gain + total_items_value)