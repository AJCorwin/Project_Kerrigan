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

            #Unit production
            await self.queens()


    async def on_first_step(self):
        await self.chat_send("Project Abathur Bot")
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        self.extractor_limit = len(self.townhalls(UnitTypeId.HATCHERY).ready) * 2


    async def on_every_step(self):
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        self.extractor_limit = len(self.townhalls(UnitTypeId.HATCHERY).ready) * 2
        await self.distribute_workers()

    async def build_workers(self):
        drone_count = self.units(DRONE)
        drone_limit = (len(self.headquarter) * 16) + (self.extractor_limit * 3)
        drones = self.units(DRONE)
        if len(drone_count) < drone_limit and self.can_afford(UnitTypeId.DRONE):
            for loop_larva in self.larva:
                if loop_larva.tag in self.unit_tags_received_action:
                    continue
                loop_larva.train(UnitTypeId.DRONE)

    async def increase_supply(self):
        if self.supply_left < self.supply_cap * 0.20:
            for loop_larva in self.larva:
                if loop_larva.tag in self.unit_tags_received_action:
                    continue
                if self.can_afford(UnitTypeId.OVERLORD):
                    if not self.already_pending(OVERLORD):
                        loop_larva.train(UnitTypeId.OVERLORD)

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
 
    async def queens(self):
        self.headquarter = self.townhalls(UnitTypeId.HATCHERY) or self.townhalls(UnitTypeId.LAIR) or self.townhalls(UnitTypeId.HIVE)
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if not self.units(UnitTypeId.QUEEN) and headquarter.is_idle:
                if self.can_afford(UnitTypeId.QUEEN):
                    hq.train(UnitTypeId.QUEEN)

sc2.run_game(
    sc2.maps.get("AutomatonLE"),
    [Bot(sc2.Race.Zerg, Project_Abathur()), Computer(sc2.Race.Zerg, sc2.Difficulty.Easy)],
    realtime = True,
)