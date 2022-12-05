import json
import os
import math
import omni
import omni.kit
import omni.usd
from omni.kit.viewport.utility import get_active_viewport

# Variable Hub
routeFilePath = 'D:/Exts/exts-camera-path/exts/camera.path.tracking/Json/transform.txt'
distanceHub = []
SecondPerTarget = []
AnglePerTarget = []
TranslateDirection = []
target = 1
speed = 200
routeCount = 0
selectedRoute = 2

class dataController:

    # Read Json file
    def get_json_data():
        base_dir = os.path.dirname(os.path.abspath((__file__)))
        with open(os.path.join(base_dir, routeFilePath), 'r', encoding="utf-8") as f:
            data = json.load(f)

        return data

    # Write back to JSON
    def write_json(file, data):
        with open(file, 'w', encoding="utf-8") as f:
            f.write(json.dumps(data))
            f.close()

    # Get routes xform
    def get_route_data(routeName, attri):
        data = dataController.get_json_data()
        get = data[routeName][attri]
        return get

    # New Target
    def add_new_target(routeName, posCam, rotCam):
        data = dataController.get_json_data()
        translate = dataController.get_route_data(routeName, 'Translate')
        rotate = dataController.get_route_data(routeName, 'Rotation')

        """ADD Translate {Key : VALUE}"""
        key = "Target_" + str(len(translate))
        newTranslate = {key:posCam}
        translate.update(newTranslate)
        data[routeName]['Translate'] = translate

        """ADD Translate {Key : VALUE}"""
        newRotate = {key:rotCam}
        rotate.update(newRotate)
        data[routeName]['Rotation'] = rotate

        dataController.write_json(routeFilePath, data)

        return True

    # Get camera Position
    def _get_camera_pos(cameraPath, cameraPrim):
        viewport = get_active_viewport()
        if not viewport:
            raise RuntimeError("No active Viewport")

        viewport.camera_path = cameraPath
        cameraTrans = cameraPrim.GetAttribute('xformOp:translate').Get()
        cameraRotate = cameraPrim.GetAttribute('xformOp:rotateYXZ').Get()
        return cameraTrans, cameraRotate

# =========================================================================
#
# Route Info
#
# =========================================================================

class Attachment_Info:

    global distanceHub
    global SecondPerTarget
    global AnglePerTarget
    global TranslateDirection
    global target
    global speed
    global routeCount
    global selectedRoute

    def StartUp():
        Attachment_Info.distanceHub = []
        Attachment_Info.AnglePerTarget = []
        Attachment_Info.TranslateDirection = []
        Attachment_Info.SecondPerTarget = []
        Attachment_Info.AnglePerTarget = []
        Attachment_Info.target = target
        Attachment_Info.speed = speed
        Attachment_Info.routeCount = Attachment_Info.countRoute()
        Attachment_Info.selectedRoute = selectedRoute
        print(Attachment_Info.routeCount)
        
    def restart():
        Attachment_Info.target = target

    def countRoute():
        data = dataController.get_json_data()
        return len(data)
    
    def routeName():
        name = 'routes_0' + str(Attachment_Info.selectedRoute)
        print(name)
        return name
    
    def changeRoute(routenum):
        Attachment_Info.selectedRoute = routenum
        print(Attachment_Info.selectedRoute)

    def add_cam_target():
        Attachment_Info.target = Attachment_Info.target+1
        print("target:")
        print(Attachment_Info.target)

    # Eu. Distance
    def add_euclideanDistance(instance1,instance2,dimension=3):
        distance = 0
        for i in range(dimension):
            distance += (instance1[i] - instance2[i])**2
        distance = math.sqrt(distance)
        distance = round(distance, 3)
        
        # ADD attach_info
        distanceHub.append(str(distance))
        Attachment_Info.distanceHub = distanceHub

        return distance

    # Record Second Per Target
    def add_SPT(Second):
        SecondPerTarget.append(str(Second))
        Attachment_Info.SecondPerTarget = SecondPerTarget

    # Record Angle per Target
    def add_APT(ins1, ins2):
        a, b, c = ins1[0], ins1[1], ins1[2]
        A, B, C = ins2[0], ins2[1], ins2[2]
        diff = [A-a, B-b, C-c]

        AnglePerTarget.append(diff)
        Attachment_Info.AnglePerTarget = AnglePerTarget

    # Determine Target Translate Direction
    def add_transDirection(ins1, ins2):
        re = []
        dif = (ins2[0]-ins1[0], ins2[1]-ins1[1], ins2[2]-ins1[2])
        for data in dif:
            if data < 0:
                re.append(-1)
            elif data > 0:
                re.append(1)
            else:
                re.append(0)

        TranslateDirection.append(re)
        Attachment_Info.TranslateDirection = TranslateDirection
