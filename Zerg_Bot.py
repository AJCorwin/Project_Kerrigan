import sc2
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

from sc2.constants import *

class Project_Kerrigan(BotAI):
    
    async def on_step(self, iteration: int):
            self.iteration = iteration
            if iteration == 0:
                #await self.on_first_step()
                pass
            if iteration % 30 == 0:
                #await self.display_data()
                pass
            # Increase Supply
            await self.increase_supply()
            # Build Drones
            await self.build_workers()
    


    for loop_larva in self.larva:
        if loop_larva.tag in self.unit_tags_received_action:
            continue
        if self.can_afford(UnitTypeId.DRONE):
            loop_larva.train(UnitTypeId.DRONE)
        # Add break statement here if you only want to train one
        else:
        # Can't afford drones anymore
            break
        
    
    async def builder_workers(self):
        # Build drones when there is a shortage at the townhall
        townhalls = len((self.units_HATCHERIES.ready | self.units_LAIR.ready | self.units_HIVE.ready))
        self.extractor_limit = len(self.townhalls) * 2
        self.ideal_harvesters = 16 + (self.extractor_limit * 3)
        drones = self.units(DRONES)
        if len(drones) <= self.worker_cap:
            if ideal_drones > assigned_drones:
                if loop_larva.tag in self.unit_tags_received_action:
                    if self.supply_left >= 1:
                        if self.can_afford(UnitTypeId.DRONE):
                            larva.train(UnitTypeId.DRONE)
        assigned_harvesters = self.workers
        self.harvester_limit = len(self.ready_)

    async def hatchery_commands(self):
        # build drones
        assigned_harvesters = 0
        my_larva = self.larva.random
        #self.extractor_limit = len(self.ready_townhall) * 2
        ideal_harvesters = 16 #+ (self.extractor_limit * 3)
        self.worker_cap = 16 #+ (self.extractor_limit * 3)
        for larva in self.ready_larva:
            drones = self.units(DRONE)
            if loop_larva.tag in self.unit_tags_received_action:
                continue
            if len(drones) <= self.worker_cap:
                if ideal_harvesters > assigned_harvesters:
                    if my_larva > 0:
                        if self.can_afford(DRONE):
                            await self.do(train(UnitTypeId.DRONE))


    async def increase_supply(self):
        if self.supply_left < self.supply_cap * 0.20:
            if self.can_afford(UnitTypeId.OVERLORD):
                if not self.already_pending(OVERLORD):
                    loop_larva.train(UnitTypeId.OVERLORD)


        if self.can_afford(UnitTypeId.SPAWNINGPOOL) and self.already_pending(UnitTypeId.SPAWNINGPOOL) + self.structures.filter(lambda structure: structure.type_id == UnitTypeId.SPAWNINGPOOL and structure.is_ready).amount == 0:
            worker_candidates = self.workers.filter(lambda worker: (worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
            # Worker_candidates can be empty
            if worker_candidates:
                map_center = self.game_info.map_center
                position_towards_map_center = self.start_location.towards(map_center, distance=5)
                placement_position = await self.find_placement(UnitTypeId.SPAWNINGPOOL, near=position_towards_map_center, placement_step=1)
                # Placement_position can be None
                if placement_position:
                    build_worker = worker_candidates.closest_to(placement_position)
                    build_worker.build(UnitTypeId.SPAWNINGPOOL, placement_position)


sc2.run_game(
    sc2.maps.get("AutomatonLE"),
    [Bot(sc2.Race.Zerg, Project_Kerrigan()), Computer(sc2.Race.Zerg, sc2.Difficulty.Easy)],
    realtime=True,
)