import time
import math
import random
import sc2
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId


from sc2.constants import *

class Project_Tychus(BotAI):
    
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


    async def on_first_step(self):
        self.worker_cap = 34
        self.refinery_limit = 0
        self.expansion_locations_keys = list(self.expansion_locations.keys())
        await self.chat_send("Project Tychus Bot")


        
    async def on_every_step(self):
        #self.zealots = self.units(ZEALOT)
        #self.stalkers = self.units(STALKER)
        #self.army = self.zealots + self.stalkers
        #self.collectedActions = []
        #self.ready_commandcenteres = self.units(COMMANDCENTER).ready
        self.ready_commandcenteres = self.townhalls(UnitTypeId.COMMANDCENTER).ready
        self.ready_ccs = self.units(COMMANDCENTER).ready
        #self.commandcenter = self.townhalls.same_tech(UnitTypeId.COMMANDCENTER)
        #self.worker_cap = (len(self.units(COMMANDCENTER))* 16) + (len(self.units(COMMANDCENTER)) * 3)
        #self.enemy_units_cost = self.get_food_cost(self.enemy_units) + self.get_food_cost(self.enemy_defense_structures)
        #self.enemy_defense_structures = []

    async def build_workers(self):
        ideal_harvesters = 0
        assigned_harvesters = 0
        for commandcenter in self.ready_commandcenteres:
            ideal_harvesters = ideal_harvesters + commandcenter.ideal_harvesters
            assigned_harvesters = assigned_harvesters + commandcenter.assigned_harvesters
            
        for commandcenter in self.ready_commandcenteres:
        # build workers when there is a shortage at the commandcenter.    
            scvs = self.units(SCV)
            if len(scvs) <= self.worker_cap:
                if ideal_harvesters > assigned_harvesters:
                    if commandcenter.noqueue:
                        if self.supply_left <= 1 and self.already_pending(SUPPLYDEPOT):
                            if self.can_afford(UnitTypeId.SCV):
                                #await self.do(commandcenter.train(UnitTypeId.SCV))
                                commandcenter.train(UnitTypeId.SCV)
                        elif self.supply_left >= 1:
                            if self.can_afford(UnitTypeId.SCV):
                                #await self.do(commandcenter.train(UnitTypeId.SCV))
                                commandcenter.train(UnitTypeId.SCV)

    async def increase_supply(self):
        if self.can_afford(UnitTypeId.SUPPLYDEPOT):
            if not self.already_pending(SUPPLYDEPOT):
                if self.supply_left < self.supply_cap * 0.20:
                    worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    # Worker_candidates can be empty
                    if worker_candidates:
                        map_center = self.game_info.map_center
                        position_towards_map_center = self.start_location.towards(map_center, distance=5)
                        placement_position = await self.find_placement(UnitTypeId.SUPPLYDEPOT, near=position_towards_map_center, placement_step=1)
                        # Placement_position can be None
                        if placement_position:
                            build_worker = worker_candidates.closest_to(placement_position)
                            build_worker.build(UnitTypeId.SUPPLYDEPOT, placement_position)
    

    async def collect_gas(self):
        refinerys = len(self.units(REFINERY)) + self.already_pending(REFINERY)
        self.refinery_limit = len(self.townhalls(UnitTypeId.COMMANDCENTER).ready) * 2
        vespene_deposits = []
        if self.refinery_limit > refinerys:
            for commandcenter in self.ready_commandcenteres:
                vespene_deposits += self.state.vespene_geyser.closer_than(20.0, commandcenter)
                if self.can_afford(REFINERY):
                    vespene_deposit = random.choice(vespene_deposits)
                    scv = self.select_build_worker(vespene_deposit.position)
                    if scv:
                        #await self.do(scv.build(UnitTypeId.REFINERY, vespene_deposit))
                        await self.do(scv.build(REFINERY, vespene_deposit))



sc2.run_game(
    sc2.maps.get("AutomatonLE"),
    [Bot(sc2.Race.Terran, Project_Tychus()), Computer(sc2.Race.Terran, sc2.Difficulty.Easy)],
    realtime=True,
)