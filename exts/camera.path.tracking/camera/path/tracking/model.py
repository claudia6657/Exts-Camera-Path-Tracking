import omni.usd
from pxr import Usd, Sdf, Gf
import omni.timeline
import omni.kit.commands

from .data_controller import *

# =========================================================================
#
# ExtensionModel
#
# =========================================================================

# Variable
defaultTranslate = (0, 100, 0)
primPath = r'/World/RouteCameras/Camera/camera'
cameraPath = r'/World/RouteCameras/SettingCamera/camera'
temp_routeName = 'routes_01'

class ExtensionModel:

    def __init__(self):
        # init Info
        Attachment_Info.StartUp()

        # Default Variable 
        self.defaultTranslate = (0, 100, 0)
        self.defaultRotate = (0, 0, 0)
        self.speed = Attachment_Info.speed
        self.targetNum = 1
        self.targetBasePath = r'/World/Target/Cube'
        self.stage = omni.usd.get_context().get_stage()


        
        # attachment init
        self.info_Startup()

        # Create Camera
 
        self.primPath = r'/World/RouteCameras/Camera/camera'
        self.camPath = r'/World/RouteCameras/SettingCamera/camera'
        omni.kit.commands.execute('CreatePrimWithDefaultXformCommand', prim_type='Camera', prim_path=self.primPath, attributes={'focusDistance': 400, 'focalLength': 24})
        omni.kit.commands.execute('CreatePrimWithDefaultXformCommand', prim_type='Camera', prim_path=self.camPath, attributes={'focusDistance': 400, 'focalLength': 24})
        
        self.getPrim = self.stage.GetPrimAtPath(self.primPath)
        self.getCamPrim = self.stage.GetPrimAtPath(self.camPath)

        # Set Default translate
        if self.getPrim:
            self.translate = self.getPrim.CreateAttribute('xformOp:translate', Sdf.ValueTypeNames.Double3, True)
            self.rotate = self.getPrim.CreateAttribute('xformOp:rotateYXZ', Sdf.ValueTypeNames.Double3, True)
            self.set_default_translate()

    # ==========================================================================
    # Movement
    # ==========================================================================
    
    # Move Camera Translation
    def move_to_target():
        
        targetSet = dataController.get_route_data(Attachment_Info.routeName(), "Translate")
        # Get targets        
        currentTarget = Attachment_Info.target
        targetT, currentT = ExtensionModel.get_target_data(currentTarget, "Translate")
        targetR, currentR = ExtensionModel.get_target_data(currentTarget, "Rotation")

        currentTran = ExtensionModel.get_Translate().Get()
        currentRot = ExtensionModel.get_Rotation().Get()
        print(currentTarget)
        
        # Target to Time
        SPT = Attachment_Info.SecondPerTarget
        secondThisTarget = SPT[currentTarget-1]
        secondThisTarget = float(secondThisTarget)
        APT = Attachment_Info.AnglePerTarget
        angleThisTarget = APT[currentTarget-1]
        Dir = Attachment_Info.TranslateDirection[currentTarget-1]

        # Get time
        current_time = ExtensionModel.get_current_time()
        accuTime = ExtensionModel.accumulate_target_time(current_time, SPT, currentTarget)
        targetTime = current_time - accuTime
        print(float(SPT[currentTarget-1]), targetTime)

        # Trigger
        Arrived = True
        for i in range(0, len(Dir)):
            distance = targetT[i]-currentTran[i]
            if ((abs(distance)) > 0.5) and (targetTime <= float(SPT[currentTarget-1])):
                Arrived = False
        
        # Next Target
        if Arrived == True:
            print("CHANGE TARGET")
            if (len(targetSet)) > currentTarget:
                currentTarget += 1
                Attachment_Info.add_cam_target()
        
        # Translate change
        if Arrived == False:
            ExtensionModel.move_translate(targetT, currentT, secondThisTarget, targetTime)
            ExtensionModel.move_rotation(currentR, secondThisTarget, angleThisTarget, targetTime)

        return 0

    # Set New Translate
    def move_translate(target, default, secondThisTarget, PTime):

        diff = (target[0] - default[0], target[1] - default[1], target[2] - default[2])
        disPerSec = (diff[0] / secondThisTarget, diff[1] / secondThisTarget, diff[2] / secondThisTarget)
        addX, addY, addZ = (disPerSec[0] * PTime, disPerSec[1] * PTime, disPerSec[2] * PTime)
        newTranslate = (default[0]+addX, default[1]+addY, default[2]+addZ)

        getTrans = ExtensionModel.get_Translate()
        ExtensionModel.set_Translate(getTrans, newTranslate)
    
    # Set New Rotation
    def move_rotation(default, secondThisTarget, angleThisTarget, PTime):
        anglePerSec = [angleThisTarget[0]/secondThisTarget, angleThisTarget[1]/secondThisTarget, angleThisTarget[2]/secondThisTarget]
        addX, addY, addZ = (anglePerSec[0]*PTime, anglePerSec[1]*PTime, anglePerSec[2]*PTime)
        newRotate = (default[0]+addX, default[1]+addY, default[2]+addZ)

        getRot = ExtensionModel.get_Rotation()
        ExtensionModel.set_Translate(getRot, newRotate)

    # Get Target
    def get_target_data(currentTarget, att):
        targetSet = dataController.get_route_data(Attachment_Info.routeName(), att)
        #if len(targetSet) <= currentTarget :return
        target = targetSet["Target_"+str(currentTarget)]
        default = targetSet["Target_"+str(currentTarget-1)]

        return target, default
    
    # Time Accumulation
    def accumulate_target_time(current_time, SPT, current_target):
        accuTime = 0
        for second in range(0, current_target-1):
            accuTime = accuTime + float(SPT[second])
        
        return accuTime

    # Default Camera Position
    def set_default_translate(self):
        self.translate.Set(self.defaultTranslate)
        self.rotate.Set(self.defaultRotate)

    # Get current Translate
    def get_Translate():
        stage = omni.usd.get_context().get_stage()
        getPrim = stage.GetPrimAtPath(primPath)

        return getPrim.GetAttribute('xformOp:translate')

    # Set Translate
    def set_Translate(Translate, newTranslate):
        Translate.Set(newTranslate)

    # Get current Rotation
    def get_Rotation():
        stage = omni.usd.get_context().get_stage()
        getPrim = stage.GetPrimAtPath(primPath)

        return getPrim.GetAttribute('xformOp:rotateYXZ')

    # Set Translate
    def set_Rotation(Rotation, newRotation):
        Rotation.Set(newRotation)

    # ==========================================================================
    # Commands
    # ==========================================================================

    # Add new camera
    def create_new_camera(self, Path):
        omni.kit.commands.execute("CreatePrimCommand", prim_type='Camera', prim_path=Path, attributes={'focusDistance': 400, 'focalLength': 24})
        self.getPrim = self.stage.GetPrimAtPath(self.primPath)
        translate = self.getPrim.CreateAttribute('xformOp:translate', Sdf.ValueTypeNames.Double3, True)
        translate.Set(self.defaultTranslate)
    
    # Create New Prim
    def import_prim(self, primType, trans, rot, num):
        primpath = self.targetBasePath + '_' + str(num)

        omni.kit.commands.execute("CreatePrimWithDefaultXformCommand", prim_type=primType, prim_path=primpath)
        getPrim = self.stage.GetPrimAtPath(primpath)
        translate = getPrim.CreateAttribute('xformOp:translate', Sdf.ValueTypeNames.Double3, True)
        translate.Set(Gf.Vec3d(trans))
        rotate = getPrim.CreateAttribute('xformOp:rotateYXZ', Sdf.ValueTypeNames.Double3, True)
        rotate.Set(Gf.Vec3d(rot))

    # Create New Prim
    def create_prim(self, primType, trans, rot):
        primpath = self.count_prim_name(self.targetBasePath, 0)
        if not primpath:
            primpath = self.newTargetPath
        omni.kit.commands.execute("CreatePrimWithDefaultXformCommand", prim_type=primType, prim_path=primpath)
        getPrim = self.stage.GetPrimAtPath(primpath)
        translate = getPrim.CreateAttribute('xformOp:translate', Sdf.ValueTypeNames.Double3, True)
        translate.Set(Gf.Vec3d(trans))
        rotate = getPrim.CreateAttribute('xformOp:rotateYXZ', Sdf.ValueTypeNames.Double3, True)
        rotate.Set(Gf.Vec3d(rot))

    def count_prim_name(self, prim_path, prim_num):
        new_prim_path = prim_path + '_' + str(prim_num)
        print(new_prim_path)
        exists = self.is_Exists(new_prim_path)
        if exists == True:
            self.count_prim_name(prim_path, int(prim_num)+1)
        else:
            self.newTargetPath = new_prim_path
            return exists

    def is_Exists(self, primPath):
        getPrim = self.stage.GetPrimAtPath(primPath)
        if getPrim:
            return True
        
    # =========================================================================
    # Info Set
    # =========================================================================

    def info_Startup(self):
        self.count_Dist_FPT()
        self.count_anglepersec()
        # init target
        transData = dataController.get_route_data(Attachment_Info.routeName(), "Translate")
        rotateData = dataController.get_route_data(Attachment_Info.routeName(), "Rotation")

        for i in range(0, len(transData)):
            target = 'Target_'+ str(i)
            self.import_prim('Cube', transData[target], rotateData[target], i)
        
    # Count Eu-Dist and FPT AND keep info. in Attachment
    def count_Dist_FPT(self):
        target_trans = dataController.get_route_data(Attachment_Info.routeName(), "Translate")

        for i in range(0, len(target_trans)-1):
            targetN1 = 'Target_'+ str(i)
            targetN2 = 'Target_'+ str(i+1)
            ins1 = target_trans[targetN1]
            ins2 = target_trans[targetN2]

            Attachment_Info.add_euclideanDistance(ins1, ins2, 3)
            Attachment_Info.add_transDirection(ins1, ins2)
        
        distHub = Attachment_Info.distanceHub

        for dist in distHub:
            dist = float(dist)
            Second = dist /self.speed
            Attachment_Info.add_SPT(Second)
        
        print(Attachment_Info.SecondPerTarget)
        return 0

    def count_anglepersec(self):
        target_rotates = dataController.get_route_data(Attachment_Info.routeName(), "Rotation")

        for i in range(0, len(target_rotates)-1):
            targetN1 = 'Target_'+ str(i)
            targetN2 = 'Target_'+ str(i+1)
            ins1 = target_rotates[targetN1]
            ins2 = target_rotates[targetN2]

            Attachment_Info.add_APT(ins1, ins2)
        print(Attachment_Info.AnglePerTarget)

        return 0

# =========================================================================
#
# Timeline
#
# =========================================================================

    def get_current_time():
        timeline = omni.timeline.get_timeline_interface()
        current_time = timeline.get_current_time()

        return current_time

    # Timeline Event
    def timeline_event(event):
        # on play press
        if event.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
            global time
            time = 0.0
            ExtensionModel.move_to_target()
        # on stop press
        if event.type == int(omni.timeline.TimelineEventType.STOP):
            pass

    # Timeline interface
    timeline = omni.timeline.get_timeline_interface()
    stream = timeline.get_timeline_event_stream()
    _timeline_subscription = stream.create_subscription_to_pop(timeline_event)
