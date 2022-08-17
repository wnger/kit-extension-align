
__all__ = ["AlignModel"]

# from turtle import pos
from typing import List
import numpy as np
import omni.usd
import omni.kit.commands
from pxr import Tf, Usd, UsdGeom, Sdf, Gf

class AlignModel:
    def __init__(self, stage):
        print('myModelPrim', stage)
        # super().__init__()
        # self._target_path = target_path
        # self._get_position()

    def get_selection() -> List[str]:
        """Get the list of currently selected prims"""
        return omni.usd.get_context().get_selection().get_selected_prim_paths()

    def get_size(self, prim):
        rangeTarget = self.get_bound(prim)
        bboxMinTarget = rangeTarget.GetMin()
        bboxMaxTarget = rangeTarget.GetMax()

        # Get size
        targetH = bboxMaxTarget[1] - bboxMinTarget[1]
        targetW = bboxMaxTarget[0] - bboxMinTarget[0]
        targetD = bboxMaxTarget[2] - bboxMinTarget[2]

        return np.array([targetW, targetH, targetD])

    def get_bound(self, prim):
        box_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        boundWorld = box_cache.ComputeWorldBound(prim)
        boundLocal = box_cache.ComputeLocalBound(prim)
        # print('bound')

        range = boundLocal.ComputeAlignedBox()
        return range

    def set_scale(self, stage, primPath, oldScale, targetScale, targetPrim, transVal):

        sourcePrim = stage.GetPrimAtPath(primPath)
        sourceScale = np.array([oldScale[0], oldScale[1], oldScale[2]])
        sourceSize = self.get_size(sourcePrim)
        targetSize = self.get_size(targetPrim)
        newScale = (targetSize/sourceSize)
        
        # Constrain scaling to only 1 axis to maintain proportion
        if transVal[0] == True:
            diff = newScale[0]
        if transVal[1] == True:
            diff = newScale[1]
        if transVal[2] == True:
            diff = newScale[2]
        
        # Calculate amount to scale
        targetScale = sourceScale*diff

        newScale = oldScale

        newScale[0] = targetScale[0]
        newScale[1] = targetScale[1]
        newScale[2] = targetScale[2]

        print('Source scale', sourceScale)
        print('Source S', sourceSize)
        print('Target S', targetSize)
        print('Diff S', diff)
        print('Target Scale', targetScale)
        print('New Scale', newScale)

        omni.kit.commands.execute('TransformPrimSRT',
            path=Sdf.Path(primPath),
            new_translation=None,
            new_rotation_euler=None,
            new_rotation_order=None,
            new_scale=newScale,
            old_translation=None,
            old_rotation_euler=None,
            old_rotation_order=None,
            old_scale=None)

    def set_rotate(self, primPath, oldRotate, targetRotate, transVal):

        newRotate = oldRotate
        if transVal[0] == True:
            newRotate[0] = targetRotate[0]
        if transVal[1] == True:
            newRotate[1] = targetRotate[1]
        if transVal[2] == True:
            newRotate[2] = targetRotate[2]

        omni.kit.commands.execute('TransformPrimSRT',
            path=Sdf.Path(primPath),
            new_translation=None,
            new_rotation_euler=newRotate,
            new_rotation_order=None,
            new_scale=None,
            old_translation=None,
            old_rotation_euler=None,
            old_rotation_order=None,
            old_scale=None)

    def set_transform(self, stage, primPath, oldPos, targetPrim, targetPos, faceVal, transVal):

        newPos = targetPos
        sourcePrim = stage.GetPrimAtPath(primPath)

        # Set new position to old position
        newX = oldPos[0]
        newY = oldPos[1]
        newZ = oldPos[2]

        print('Source path', primPath)
   
        # Get source prim info
        rangeSource = self.get_bound(sourcePrim)
        bboxMinSource = rangeSource.GetMin()
        bboxMaxSource = rangeSource.GetMax()
        bbMinSource = Gf.Vec3f(bboxMinSource)
        bbMaxSource = Gf.Vec3f(bboxMaxSource)

        # Get center
        bbCenterSource = (bbMinSource + bbMaxSource) * 0.5

        # Get pivot offset if any
        pivotPosSource = bbCenterSource - oldPos

        # Get source size
        sourceH = bboxMaxSource[1] - bboxMinSource[1]
        sourceW = bboxMaxSource[0] - bboxMinSource[0]
        sourceD = bboxMaxSource[2] - bboxMinSource[2]
    
        # If source is too small, eg. Xform
        if sourceH < 0:
            sourceH = 0
        if sourceW < 0:
            sourceW = 0
        if sourceD < 0:
            sourceD = 0

        # Get target prim info
        rangeTarget = self.get_bound(targetPrim)
        bboxMinTarget = rangeTarget.GetMin()
        bboxMaxTarget = rangeTarget.GetMax()

        # Get target size
        targetH = bboxMaxTarget[1] - bboxMinTarget[1]
        targetW = bboxMaxTarget[0] - bboxMinTarget[0]
        targetD = bboxMaxTarget[2] - bboxMinTarget[2]

        # If target is too small
        if targetH < 0:
            targetH = 0
        if targetW < 0:
            targetW = 0
        if targetD < 0:
            targetD = 0
        
        # Set new position to target center if has size
        if targetH > 0 or targetW > 0 or targetD > 0:
            bbMinTarget = Gf.Vec3f(bboxMinTarget)
            bbMaxTarget = Gf.Vec3f(bboxMaxTarget)
            bbCenterTarget = (bbMinTarget + bbMaxTarget) * 0.5
            newPos = bbCenterTarget


        print('newPos', newPos)
        
        # Set axis value
        if transVal[0] == True:
            newX = newPos[0]
        if transVal[1] == True:
            newY = newPos[1]
        if transVal[2] == True:
            newZ = newPos[2]

        # Target has no size
        if targetH == 0 and targetW == 0 and targetD == 0:
            if faceVal == 1:
                # Top
                newY += sourceH*0.5
            elif faceVal == 2:
                # Bottom
                newY -= sourceH*0.5
            elif faceVal == 3:
                # Left
                newX -= sourceW*0.5
            elif faceVal == 4:
                # Right
                newX += sourceW*0.5
            elif faceVal == 5:
                # Front
                newZ += sourceD*0.5
            elif faceVal == 6:
                # Back
                newZ -= sourceD*0.5
        # Target has size
        else:
            if faceVal == 1:
                # Top
                newY = bboxMaxTarget[1] + (sourceH*0.5)
            elif faceVal == 2:
                # Bottom
                newY = bboxMinTarget[1] - (sourceH*0.5)
            elif faceVal == 3:
                # Left
                newX = bboxMinTarget[0] - (sourceW*0.5)
            elif faceVal == 4:
                # Right
                newX = bboxMaxTarget[0] + (sourceW*0.5)
            elif faceVal == 5:
                # Front
                newZ = bboxMaxTarget[2] + (sourceD*0.5)
            elif faceVal == 6:
                # Back
                newZ = bboxMinTarget[2] - (sourceD*0.5)

        # Grouped objects automatically add pivot transform attribute, we have to add pivot values into transform
        if sourcePrim.HasProperty('xformOp:translate:pivot'):
            sourcePivotVal = sourcePrim.GetProperty('xformOp:translate:pivot').Get()
            newX -= sourcePivotVal[0]
            newY -= sourcePivotVal[1]
            newZ -= sourcePivotVal[2]

        # Offset pivot values if any
        if sourceH > 0 or sourceW > 0 or sourceD > 0:
            newX -= pivotPosSource[0]
            newY -= pivotPosSource[1]
            newZ -= pivotPosSource[2]

        pos = [newX, newY, newZ]

        omni.kit.commands.execute('TransformPrimSRT',
            path=Sdf.Path(primPath),
            new_translation=Gf.Vec3d(pos[0], pos[1], pos[2]),
            new_rotation_euler=None,
            new_rotation_order=None,
            new_scale=None,
            old_translation=None,
            old_rotation_euler=None,
            old_rotation_order=None,
            old_scale=None)

    def _set_pivot(self, prim):
        Xformable = UsdGeom.Xformable(prim)
        xform = UsdGeom.XformCommonAPI(Xformable)
        t = xform.GetXformVectors(Usd.TimeCode.Default())
        t[3][0] += t[0][0]
        t[3][1] += t[0][1]
        t[3][2] += t[0][2]
        return t

    def set_align(self, tabVal, faceVal, transVal):
        """Returns position of currently selected object"""
        stage = omni.usd.get_context().get_stage()

        selectedPrims = omni.usd.get_context().get_selection().get_selected_prim_paths()

        # if len(selectedPrims) == 1:
        #     sourcePrim = stage.GetPrimAtPath(selectedPrims[0])
        #     return

        if len(selectedPrims) > 1:
            targetPrim = stage.GetPrimAtPath(selectedPrims[-1])
            t = self._set_pivot(targetPrim)
            targetTransform = [t[2],t[1],t[3],t[3]]

            # Start group commands
            omni.kit.undo.begin_group()
            for prim in selectedPrims[:-1]:
                sourcePrim = stage.GetPrimAtPath(prim)
                t = self._set_pivot(sourcePrim)
                oldTransform = [t[2],t[1],t[3],t[3]]

                if tabVal == 'Transform':
                    oldPos = oldTransform[3]
                    targetPos = targetTransform[3]
                    self.set_transform(stage, prim, oldPos, targetPrim, targetPos, faceVal, transVal)
                elif tabVal == 'Scale':
                    oldScale = oldTransform[0]
                    targetScale = targetTransform[0]
                    self.set_scale(stage, prim, oldScale, targetScale, targetPrim, transVal)
                elif tabVal == 'Rotate':
                    oldRotate = oldTransform[1]
                    targetRotate = targetTransform[1]
                    self.set_rotate(prim, oldRotate, targetRotate, transVal)

            # End group commands
            omni.kit.undo.end_group()