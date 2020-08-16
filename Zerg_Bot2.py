import time
import math
import random
import sc2
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.player import Bot, Computer
from sc2.data import race_townhalls
from sc2.constants import *

class Project_Abathur(BotAI):
    
    async def on_step(self, iteration: int):
            self.iteration = iteration
            if iteration == 0:
                await self.on_first_step()
                #pass
            if iteration % 30 == 0:
                #await self.display_data()
                pass
            #SCV Stuff
            await self.on_every_step()
            # Increase Supply
            await self.increase_supply()
            # Build SCVs
            await self.build_workers()
            # Collect Gas
            await self.collect_gas()
            # Not sure if this works | Basic Idle work limit and worker distribution
            #await self.worker_control()
            # Build Spawning Pool
            await self.build_sp()
            # Build Hydra Den
            await self.build_hydra_den()


            await self.expansion_time()

            # Unit production
            await self.queens()
            await self.op_speedlings()
            await self.op_hydras()

            # Abilities
                # Assigned queens to hatchers and have them inject 
                    # Note to self, break this down later when Python understanding is better.
            await self.injector_queens()
            await self.queen_injects()

            #await self.operation_tumors()
            await self.economy_upgrades()
            # Combat
            await self.conquer()

    async def on_first_step(self):
        # Create Queen Injector list & Hatchery List
        self.QueenAssignedHatcheries = {}
        self.TownhallHatcheryList = {}


        await self.chat_send("Project Abathur Bot")
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        self.extractor_limit = len(self.headquarter) * 2

        # Enable creep spread
        #self.enableCreepSpread = True


    async def on_every_step(self):
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        self.extractor_limit = len(self.headquarter) * 2
        await self.distribute_workers()

    async def build_workers(self):
        drone_limit = (len(self.headquarter) * 16) + (self.extractor_limit * 3)
        drones = self.units(DRONE)
        drone_count = len(drones)
        if self.supply_workers < drone_limit and self.can_afford(UnitTypeId.DRONE):
            for loop_larva in self.larva:
                if loop_larva.tag in self.unit_tags_received_action:
                    continue
                if self.already_pending(UnitTypeId.DRONE) < 99:
                    loop_larva.train(UnitTypeId.DRONE)
                    break

    async def increase_supply(self):
        if self.supply_left < self.supply_cap * 0.20:
            for loop_larva in self.larva:
                if loop_larva.tag in self.unit_tags_received_action:
                    continue
                if self.can_afford(UnitTypeId.OVERLORD):
                    if not self.already_pending(OVERLORD):
                        loop_larva.train(UnitTypeId.OVERLORD)
                        break


    async def collect_gas(self):
        vespene_deposits = []
        drones = self.units(DRONE)
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        #hq: Unit = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        hq: Unit = self.townhalls.first
        if len(drones) >= 14:
            if self.can_afford(UnitTypeId.EXTRACTOR) and (self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) > 0) : #and self.already_pending(EXTRACTOR)
                worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                if worker_candidates:
                    if self.can_afford(UnitTypeId.EXTRACTOR) and self.already_pending(UnitTypeId.EXTRACTOR) == 0:
                        for vg in self.vespene_geyser.closer_than(10, hq):
                            drone: Unit = self.workers.random
                            drone.build_gas(vg)
                            break

    async def build_sp(self):
        drones = self.units(DRONE)
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        if len(drones) >= 14:
            if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
                if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    if worker_candidates:
                            map_center = self.game_info.map_center
                            position_towards_map_center = self.start_location.towards(map_center, distance=5)
                            await self.build(UnitTypeId.SPAWNINGPOOL, near=position_towards_map_center, placement_step=1)
 
    async def build_hydra_den(self):
        drones = self.units(DRONE)
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        if self.townhalls(UnitTypeId.LAIR).ready:
            if self.structures(UnitTypeId.HYDRALISKDEN).amount + self.already_pending(UnitTypeId.HYDRALISKDEN) == 0:
                if self.can_afford(UnitTypeId.HYDRALISKDEN):
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    if worker_candidates:
                            map_center = self.game_info.map_center
                            position_towards_map_center = self.start_location.towards(map_center, distance=5)
                            await self.build(UnitTypeId.HYDRALISKDEN, near=position_towards_map_center, placement_step=1)

    async def queens(self):
        hq: Unit = self.townhalls.first
        queens_count = self.units(QUEEN)
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if hq.is_idle:
                if self.can_afford(UnitTypeId.QUEEN):
                    if len(queens_count) < len(self.headquarter) + 1:
                        hq.train(UnitTypeId.QUEEN)

    # injector queens inspiried by https://github.com/BurnySc2/burny-bots-python-sc2/blob/master/CreepyBot/CreepyBot.py
    async def injector_queens(self, maxAmountInjectQueens = 5):
        
        # hasattr: https://www.programiz.com/python-programming/methods/built-in/hasattr
        # The hasattr() method returns true if an object has the given named attribute and false if it does not.
        if not hasattr(self, "queensAssignedHatcheries"):
            self.queensAssignedHatcheries = {}
            # if there is no list for queens assigned to hatcheries this creates it
        
        if maxAmountInjectQueens == 0:
            self.queensAssignedHatcheries = {}
            # if no queens in assigned hatcheries then create this list

        #Lambda is a self contained function / function within another https://www.w3schools.com/python/python_lambda.asp
        queensNoInjectPartner = self.units(QUEEN).filter(lambda q: q.tag not in self.QueenAssignedHatcheries.keys())
        basesNoInjectPartner = self.townhalls.filter(lambda h: h.tag not in self.queensAssignedHatcheries.values() and h.build_progress > 0.8)
        # assigns queens and hatcheries together if they do not have one. Hatcheries need to be at 80% built to have a queen asigned.

        for queen in queensNoInjectPartner:
            if basesNoInjectPartner.amount == 0:
                break
            closestBase = basesNoInjectPartner.closest_to(queen)
            self.queensAssignedHatcheries[queen.tag] = closestBase.tag
            basesNoInjectPartner = basesNoInjectPartner - [closestBase]
            break # so one hatch gets only one queen
            # .tag is part of the library, it returns all unit tags as a set 
            # .tags_in(other) Filters all units that have their tags in the ‘other’ set/list/dict
            # .tags_not_in(other) Filters all units that have their tags not in the ‘other’ set/list/dict
            # https://burnysc2.github.io/python-sc2/docs/units/index.html

    async def queen_injects(self):
        aliveQueenTags = [queen.tag for queen in self.units(QUEEN)] # list of numbers (tags / unit IDs)
        aliveBasesTags = [base.tag for base in self.townhalls]

        # make queens inject if they have 25 or more energy
        toRemoveTags = []


        if hasattr(self, "queensAssignedHatcheries"):
            for queenTag, hatchTag in self.queensAssignedHatcheries.items():
                # queen is no longer alive
                if queenTag not in aliveQueenTags: 
                    toRemoveTags.append(queenTag)
                    continue
                # hatchery / lair / hive is no longer alive
                if hatchTag not in aliveBasesTags:
                    toRemoveTags.append(queenTag)
                    continue
                # queen and base are alive, try to inject if queen has 25+ energy
                queen = self.units(QUEEN).find_by_tag(queenTag)            
                hatch = self.townhalls.find_by_tag(hatchTag)            
                if hatch.is_ready:
                    if queen.energy >= 25 and queen.is_idle and not hatch.has_buff(QUEENSPAWNLARVATIMER):
                        #await self.do(queen(EFFECT_INJECTLARVA, hatch))
                        queen(AbilityId.EFFECT_INJECTLARVA, hatch)
                else:
                    if queen.is_idle and queen.position.distance_to(hatch.position) > 10:
                        queen(AbilityId.MOVE, hatch.position.to2)


            # clear queen tags (in case queen died or hatch got destroyed) from the dictionary outside the iteration loop
            for tag in toRemoveTags:
                self.queensAssignedHatcheries.pop(tag)


    '''async def operation_tumors(self):

        for self.unit(QUEEN) not in self.queensAssignedHatcheries:'''

    async def op_speedlings(self):
        zergling_count = self.units(ZERGLING)
        if self.can_afford(UnitTypeId.ZERGLING):
            for loop_larva in self.larva:
                if loop_larva.tag in self.unit_tags_received_action:
                    continue
                if self.already_pending(UnitTypeId.ZERGLING) < 15:
                    if len(zergling_count) <= 50:
                        loop_larva.train(UnitTypeId.ZERGLING)
                    else:
                        break

    async def op_hydras(self):
        hydra_count = self.units(HYDRALISK)
        if self.can_afford(UnitTypeId.HYDRALISK) and self.structures(UnitTypeId.HYDRALISKDEN).ready:
            for loop_larva in self.larva:
                if loop_larva.tag in self.unit_tags_received_action:
                    continue
                if self.already_pending(UnitTypeId.HYDRALISK) < 15:
                    if len(hydra_count) <= 50:
                        loop_larva.train(UnitTypeId.HYDRALISK)
                    else:
                        break

    async def expansion_time(self):
        if self.townhalls.ready.amount + self.already_pending(HATCHERY) < 3:
            if self.can_afford(UnitTypeId.HATCHERY):
                await self.expand_now()

    async def conquer(self):
        if self.supply_army >= 90:
            for army in self.units(UnitTypeId.HYDRALISK):
                targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                if targets:
                    target = targets.closest_to(army)
                    army.attack(target)
                else:
                    army.attack(self.enemy_start_locations[0])

        if self.supply_army >= 90:
            for army in self.units(UnitTypeId.ZERGLING):
                targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                if targets:
                    target = targets.closest_to(army)
                    army.attack(target)
                else:
                    army.attack(self.enemy_start_locations[0])
    #async def combat_upgrades(self):
    

    async def economy_upgrades(self):
        hq: Unit = self.townhalls.first
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if not self.townhalls(UnitTypeId.LAIR):
                if self.can_afford(UnitTypeId.LAIR):
                    hq.build(UnitTypeId.LAIR)


sc2.run_game(
    sc2.maps.get("AutomatonLE"),
    [Bot(sc2.Race.Zerg, Project_Abathur()), Computer(sc2.Race.Terran, sc2.Difficulty.Easy)],
    realtime = True,
)
