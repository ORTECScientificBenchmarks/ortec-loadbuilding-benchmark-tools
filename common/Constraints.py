from common.Requirements import BaseConstraint, ExistenceRequirement, PropositionalRequirement
from common.NgoiMatrix import NgoiMatrix
from common.utils import key, Orientation
from solution.ThreeDplacement import ThreeDplacement

# When implementing a base class that should not be listed in the CONSTRAINT_LIST,
# use the following template (not tested with multiple inheritance):
#
#  class ____Constraint(superclass):
#      ...
#
#      @classmethod
#      def _IsActiveRequirement_(c,cls):
#          return len(cls.mro()) > len(superclass.mro()) + 1
class AxleWeightConstraint(BaseConstraint):
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
    def Validate(threeDsolution):
        b,e = True, [""]
        for container in threeDsolution.containers:
            L_min, L_max =  float("inf"), -float("inf")
            for loadingspace in threeDsolution.threeDinstance.containerkinds[container.kindid].loadingspaces:
                L_min, L_max = min(L_min, loadingspace.position[0]), max(L_max, loadingspace.position[0] + loadingspace.boundingBox[0])
            C_min, C_max = container.GetCOGbounds()
            C_min, C_max = max(C_min, L_min), min(C_max, L_max)
            x            = container.GetCOG()
            if x[0] < C_min or x[0] > C_max:
                b = False
                e.append("Container with id " + str(container.id) + " and kind " + str(container.kindid) + " c.o.g.: " + str(x[0]) + " not in [" + str(C_min) + ", " + str(C_max) + "] <- VIOLATION")
            else:
                e.append("Container with id " + str(container.id) + " and kind " + str(container.kindid) + " c.o.g.: " + str(x[0]) + " in [" + str(C_min) + ", " + str(C_max) + "]")
        return b, ("All" if b else "Not all") + " containers adhere to their axle weight constraints:" + "\n\t- ".join(sorted(e))

class MaximumWeightConstraint(BaseConstraint):
    name = "maximum_weight"
    containerkindRequirements = [ExistenceRequirement("maxWeight", float("inf"), float),
                                 PropositionalRequirement("maxWeight", lambda x: x>=0, "maxWeight must be non-negative")]
    itemkindRequirements = [ExistenceRequirement("weight", 0., float),
                            PropositionalRequirement("weight", lambda x: x>=0, "weight must be non-negative")]
    boxkindRequirements = [ExistenceRequirement("weight", 0., float),
                           PropositionalRequirement("weight", lambda x: x>=0, "weight must be non-negative")]
    palletkindRequirements = [ExistenceRequirement("weight", 0., float),
                              PropositionalRequirement("weight", lambda x: x>=0, "weight must be non-negative")]
    def Validate(threeDsolution):
        b,e = True, [""]
        for container in threeDsolution.containers:
            total_weight = container.GetTotalWeight()
            rep = "Container with id " + str(container.id) + " and kind " + str(container.kindid) + ": " + str(total_weight) + "/" + str(container.maxWeight)
            if total_weight > container.maxWeight:
                b = False
                rep += " <- VIOLATION"
            e.append(rep)
        return b, ("All" if b else "Not all") + " containers adhere to their maximum weight constraints:" + "\n\t- ".join(sorted(e))

class MustPlaceConstraint(BaseConstraint):
    name = "must_place"
    palletkindRequirements = [ExistenceRequirement("place", True, bool)]
    boxkindRequirements    = [ExistenceRequirement("place", True, bool)]
    itemkindRequirements   = [ExistenceRequirement("place", True, bool)]
    def Validate(threeDsolution):
        b,e = True, [""]
        if threeDsolution.unplaced != []:
            for placement in threeDsolution.unplaced:
                if placement.place:
                    b = False
                    e.append(placement.type.capitalize() + " with id " + str(placement.id) + " should be placed <- VIOLATION")
        if b:
            return True, "All necessary placements were placed."
        else:
            return False, "Not all necessary placements were placed:" + "\n\t- ".join(sorted(e))

class ReadableItemLabelConstraint(BaseConstraint):
    name = "readable_item_labels"
    itemkindRequirements = [ExistenceRequirement("label", "L", str),
                            PropositionalRequirement("label", lambda x: x in ['L','W','H','l','w','h'], "label must be one of L,W,H,l,w,h")]

    class Dummy(ThreeDplacement):
        def __init__(self):
            super(ReadableItemLabelConstraint.Dummy, self).__init__()
        @staticmethod
        def TypeString():
            return "label of item"

    def GetDummies(loadingspace):
        dummies = []
        for placement in loadingspace.placements:
            if hasattr(placement, "label"):
                dummy = ReadableItemLabelConstraint.Dummy()
                dummy.__dict__ = {x: placement.__dict__[x] for x in placement.__dict__ if x not in ['position', 'boundingBox']}
                dummy.position    = list(placement.position)
                dummy.boundingBox = list(placement.boundingBox)
                global_label = Orientation.ApplyToSide(Orientation.GetFromAlias(dummy.orientation), dummy.label)
                if global_label == 'l':
                    dummy.boundingBox[0] = dummy.position[0]
                    dummy.position[0] = 0
                elif global_label == 'w':
                    dummy.boundingBox[1] = dummy.position[1]
                    dummy.position[1] = 0
                elif global_label == 'h':
                    dummy.boundingBox[2] = dummy.position[2]
                    dummy.position[2] = 0
                elif global_label == 'L':
                    dummy.position[0] = dummy.position[0] + dummy.boundingBox[0]
                    dummy.boundingBox[0] = loadingspace.boundingBox[0] - dummy.position[0]
                elif global_label == 'W':
                    dummy.position[1] = dummy.position[1] + dummy.boundingBox[1]
                    dummy.boundingBox[1] = loadingspace.boundingBox[1] - dummy.position[1]
                elif global_label == 'H':
                    dummy.position[2] = dummy.position[2] + dummy.boundingBox[2]
                    dummy.boundingBox[2] = loadingspace.boundingBox[2] - dummy.position[2]
                dummies.append((dummy, global_label))
        return dummies

    def Validate(threeDsolution):
        valid, errors = True, [""]
        for pallet in threeDsolution.pallets:
            ngoi = NgoiMatrix(*pallet.loadingspace.boundingBox)
            # Add dummy objects to each placement that represent the free space required for label visibility
            dummies_labels = ReadableItemLabelConstraint.GetDummies(pallet.loadingspace)
            dummies, _ = zip(*dummies_labels)
            dummies = list(dummies)
            for dummy,label in dummies_labels:
                if label.upper() == 'H':
                    valid = False
                    errors.append("Label of item with id " + str(dummy.id) + " was facing along H-direction <- VIOLATION")
            for placement in sorted(pallet.loadingspace.placements + dummies, key=lambda x: x.position[2]):
                ngoi.addCuboid(placement)
            for pair in ngoi.overlaps():
                pair.sort(key=key("id"))
                if pair[0].TypeString() != "label of item" or pair[1].TypeString() != "label of item":
                    valid = False
                    errors.append(pair[0].TypeString().capitalize() + " with id " + str(pair[0].id) + " overlaps with " + pair[1].TypeString().capitalize() + " with id " + str(pair[1].id) + " <- VIOLATION")
            errors += ngoi.overlap_report
        return valid, ("All" if valid else "Not all") + " item labels were visible" + ("." if valid else ":" + "\n\t- ".join(sorted(set(errors))))
            

# Support constraint validate uses stored values of Ngoi matrix obtained from the DecorateSolution(..)-method
class SupportConstraint(BaseConstraint):
    name = "support"
    itemkindRequirements = [ExistenceRequirement("support", 1.0, float),
                            PropositionalRequirement("support", lambda x: x>=0 and x<=1.0, "support must be in the interval [0, 1]")]
    boxkindRequirements = [ExistenceRequirement("support", 1.0, float),
                           PropositionalRequirement("support", lambda x: x>=0 and x<=1.0, "support must be in the interval [0, 1]")]
    palletkindRequirements = [ExistenceRequirement("support", 1.0, float),
                              PropositionalRequirement("support", lambda x: x>=0 and x<=1.0, "support must be in the interval [0, 1]")]
    def Validate(threeDsolution):
        b,e = True, [""]
        for container in threeDsolution.containers:
            for loadingspace in container.loadingspaces:
                b = b and loadingspace.ngoi.support_valid
                e += loadingspace.ngoi.support_report
        for pallet in threeDsolution.pallets:
            b = b and pallet.loadingspace.ngoi.support_valid
            e += pallet.loadingspace.ngoi.support_report
        return b, ("All" if b else "Not all") + " items are properly supported:" + "\n\t- ".join(sorted(e))

class ExactStackingConstraint(BaseConstraint):
    name = "exact_stacking"
    
    def Validate(threeDsolution):
        return True, ""
        b,e = True, [""]
        for container in threeDsolution.containers:
            for loadingspace in container.loadingspaces:
                b = b and loadingspace.ngoi.support_valid
                e += loadingspace.ngoi.support_report
                print(loadingspace.ngoi[1])
        for pallet in threeDsolution.pallets:
            b = b and pallet.loadingspace.ngoi.support_valid
            e += pallet.loadingspace.ngoi.support_report
        # go through each ngoi cell, and note for each placement id the id of the placement directly underneath it
        

#class ShipTogetherConstraint(BaseConstraint):
#    name = "ship_together"
#    itemkindRequirements = [ExistenceRequirement("group", None, int)]
#    def Validate(threeDsolution):
#        return False, "\n\t- ".join(["","Item 1","Item 2"])

#class TopBottomConstraint(BaseConstraint):
#    name = "top_bottom"
#    itemkindRequirements = [ExistenceRequirement("top_loaded", False, bool),
#                            ExistenceRequirement("bottom_loaded", False, bool)]
#    boxkindRequirements = [ExistenceRequirement("top_loaded", False, bool),
#                           ExistenceRequirement("bottom_loaded", False, bool)]
#    palletkindRequirements = [ExistenceRequirement("top_loaded", False, bool),
#                              ExistenceRequirement("bottom_loaded", False, bool)]
#    def Validate(threeDsolution):
#        b,e = True, [""]
#        for container in threeDsolution.containers:
#            for loadingspace in container.loadingspaces:
#                pass
#        return b, "\n\t- ".join(sorted(e))