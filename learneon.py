import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from poke_env.player import Player
from poke_env.environment import Battle
import BattleUtilities


class Learneon(Player):
    prevDamagePercent = 100 
    currentdamagePercent = 100 
    usedMovePreviously = False 
    currentOpponent = None
    previousOpponent = None

    def choose_move(self, battle):
        self.currentOpponent = battle.opponent_active_pokemon
        if battle.finished:
            return battle.close()

        if self.currentOpponent != self.previousOpponent: 
            self.currentDamagePercent = 100
            self.previousDamagePercent = 100
            # print(f"New opponent is {self.currentOpponent}")
        else: 
            self.currentDamagePercent = battle.opponent_active_pokemon.current_hp
        #    if self.usedMovePreviously: 
                # print(f'Actual damage % done was {(self.prevDamagePercent - self.currentDamagePercent)}, previous health % was {self.prevDamagePercent}, current health percentage is {self.currentDamagePercent}%')
        self.prevDamagePercent = self.currentDamagePercent
        self.usedMovePreviously = False
        self.previousOpponent = self.currentOpponent
        

        # If Pokemon is out of moves, switch to best option
        if not battle.available_moves: 
            best_switch = self.choose_best_switch(battle)
            if best_switch is None: 
                return self.choose_default_move()
            return self.create_order(best_switch)
        
        # Use info such as type matchup and relative speed to determine who to switch to
        matchup_score = self.get_matchup_score(battle.active_pokemon, battle.opponent_active_pokemon)
        # If negative situation exceeds threshold, switch Pokemon
        if matchup_score >= 1:
            best_switch = self.choose_best_switch(battle)
            if best_switch is not None: 
                return self.create_order(best_switch)
        

        # finds the best move among available ones
        self.usedMovePreviously = True
        best_move = max(battle.available_moves, key=lambda move: BattleUtilities.calculate_damage(move, battle.active_pokemon, battle.opponent_active_pokemon, True, True))
        # print(f'Best move was {best_move}, Calculated damage value was {self.calculate_damage(best_move, battle)}')
        return self.create_order(best_move)
    

    def choose_best_switch(self, battle): 
        if not battle.available_switches: 
            return None
        # Go through each Pokemon that can be switched to, and choose one with the best type matchup
        # (smaller multipliers are better) 
        best_score = float('inf')
        best_switch = battle.available_switches[0] 
        for switch in battle.available_switches: 
            score = self.get_matchup_score(switch, battle.opponent_active_pokemon)
            if score < best_score: 
                best_score = score
                best_switch = switch
        return best_switch
    

    

    def get_matchup_score(self, my_pokemon, opponent_pokemon):
        score = 0
        defensive_multiplier = BattleUtilities.get_defensive_type_multiplier(my_pokemon, opponent_pokemon)
        # A multiplier greater than 1 means we are at a type disadvantage. If there is a better type match, switch
        if defensive_multiplier == 4:
            score += 1
        elif defensive_multiplier == 2:
            score += 0.5
        elif defensive_multiplier == 0.5:
            score -= 0.5
        elif defensive_multiplier == 0.25:
            score -= 1
        if BattleUtilities.opponent_can_outspeed(my_pokemon, opponent_pokemon):
            score += 0.5
        return score
        

 