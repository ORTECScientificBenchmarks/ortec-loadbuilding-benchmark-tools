from common.Requirements import BaseObjective, ExistenceRequirement, PropositionalRequirement
from common.utils import prod, mean

# When implementing a base class that should not be listed in the OBJECTIVE_LIST,
# use the following template (not tested with multiple inheritance):
#
#  class ____Objective(superclass):
#      ...
#
#      @classmethod
#      def _IsActiveRequirement_(c,cls):
#          return len(cls.mro()) > len(superclass.mro()) + 1

#def representsInt(string):
#    try:
#        int(string)
#        return True
#    except Exception:
#        return False

# MINIMIZE
class AxleWeightObjective(BaseObjective):
    name = "axle_weight"
    containerkindRequirements = [ExistenceRequirement("axle1", None, float),
                                 ExistenceRequirement("axle2", None, float),
                                 ExistenceRequirement("minWeightAxle1", 0.0, float),
                                 ExistenceRequirement("minWeightAxle2", 0.0, float),
                                 ExistenceRequirement("maxWeightAxle1", float("inf"), float),
                                 ExistenceRequirement("maxWeightAxle2", float("inf"), float)]
    itemkindRequirements = [ExistenceRequirement("weight", 0., float),
                            PropositionalRequirement("weight", lambda x: x>=0, "weight must be non-negative")]
    boxkindRequirements = [ExistenceRequirement("weight", 0., float),
                           PropositionalRequirement("weight", lambda x: x>=0, "weight must be non-negative")]
    palletkindRequirements = [ExistenceRequirement("weight", 0., float),
                              PropositionalRequirement("weight", lambda x: x>=0, "weight must be non-negative")]
    def Evaluate(threeDsolution):
        obj = 0
        for container in threeDsolution.containers:
            L_min, L_max =  float("inf"), -float("inf")
            for loadingspace in threeDsolution.threeDinstance.containerkinds[container.kindid].loadingspaces:
                L_min, L_max = min(L_min, loadingspace.position[0]), max(L_max, loadingspace.position[0] + loadingspace.boundingBox[0])
            C_min, C_max = container.GetCOGbounds()
            C_min, C_max = max(C_min, L_min), min(C_max, L_max)
            x            = container.GetCOG()
            obj += max(abs(x[0] - (C_min+C_max)/2) - (C_max-C_min)/2, 0)
        return obj

# MINIMIZE
class ContainerCountObjective(BaseObjective):
    name = "container_count"
    def Evaluate(threeDsolution):
        return len(threeDsolution.containers)

# MAXIMIZE
class ItemCountObjective(BaseObjective):
    name = "item_count"
    def Evaluate(threeDsolution):
        return -sum([1 for placement in threeDsolution.GetAllPlacements() if placement.position != placement.UNPLACED and placement.itemid is not None])

# MINIMIZE
class BoxCountObjective(BaseObjective):
    name = "box_count"
    def Evaluate(threeDsolution):
        return len(threeDsolution.boxes)

# MINIMIZE
class PalletCountObjective(BaseObjective):
    name = "pallet_count"
    def Evaluate(threeDsolution):
        return len(threeDsolution.pallets)

def fillRates(threeDsolution):
    fill_rates = list()
    for container in threeDsolution.containers:
        container_volume = sum([prod(loadingspace.boundingBox) for loadingspace in container.loadingspaces])
        fill_volume = sum([sum([prod(placement.boundingBox) for placement in loadingspace.placements]) for loadingspace in container.loadingspaces])
        fill_rates.append(fill_volume/container_volume)
    return fill_rates

# Average container fill rate (MAXIMIZE)
class AverageFillRateObjective(BaseObjective):
    name = "average_fill_rate"
    def Evaluate(threeDsolution):
        return -mean(fillRates(threeDsolution))

# Worst container fill rate (MAXIMIZE)
class WorstFillRateObjective(BaseObjective):
    name = "worst_fill_rate"
    def Evaluate(threeDsolution):
        return -min(fillRates(threeDsolution))