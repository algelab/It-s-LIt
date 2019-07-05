"""
It's Lit: It's Lit v1 (06/19)
Copyright Algernon Quashie 2019

Name-US: It's Lit
Description-US: Create light based on current view. (ESC + Click for help)
"""

import c4d
from c4d import gui


# Get camera view or editor view position
def get_view_data():
    bd = doc.GetRenderBaseDraw()  # editor camera
    scene_cam = bd.GetSceneCamera(doc)  # scene camera
    if scene_cam is None:
        scene_cam = bd.GetEditorCamera()

    return [scene_cam.GetOffset(), scene_cam.GetAbsRot()]


# Null Object Instantiation
def target_null_setup():
    null = c4d.BaseObject(c4d.Onull).GetClone()
    null[c4d.ID_BASELIST_NAME] = 'target'
    null[c4d.NULLOBJECT_DISPLAY] = 13
    null[c4d.NULLOBJECT_ORIENTATION] = 2
    null[c4d.ID_BASEOBJECT_USECOLOR] = 2
    null[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1, 1, 1)

    return null


# Light Object Instantiation
def light_setup():
    """
    0 = Omni Light
    1 = Spot Light
    8 = Area Light
    3 = Infinite
    """

    # Default is Area Light, Press Shift for Spotlight
    light_type = 8  # Area Light

    # Spotlight after Shift click
    bc = c4d.BaseContainer()
    c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, c4d.BFM_INPUT_VALUE, bc)
    if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QUALIFIER_CTRL:
        light_type = 1

    # Create light and settings
    light = c4d.BaseObject(c4d.Olight).GetClone()
    light[c4d.ID_BASEOBJECT_REL_POSITION] = get_view_data()[0]
    light[c4d.ID_BASEOBJECT_REL_ROTATION] = get_view_data()[1]
    light[c4d.LIGHT_TYPE] = light_type
    light[c4d.LIGHT_SHADOWTYPE] = 1

    # If object selected, set Spotlight falloff to the distance of selected object
    if light_type == 1 and doc.GetActiveObject():
        light[c4d.LIGHT_DETAILS_FALLOFF] = c4d.LIGHT_DETAILS_FALLOFF_INVERSESQUARE
        start_distance = light.GetMg().off
        end_distance = doc.GetActiveObject().GetMg().off
        dist = (end_distance-start_distance).GetLength()
        light[c4d.LIGHT_DETAILS_OUTERDISTANCE] = dist

    return light


# Create Light and target tag to the active object
def create_active_object_target(light_object, tag_target):
    doc.StartUndo()  # ----Start UNDO

    target_null = target_null_setup()  # Create target null
    doc.AddUndo(c4d.UNDOTYPE_NEW, target_null)

    doc.InsertObject(light_object, checknames=True)  # Insert Light Object
    doc.AddUndo(c4d.UNDOTYPE_NEW, light_object)

    light_object.InsertTag(tag_target)  # add target tag to light
    doc.AddUndo(c4d.UNDOTYPE_NEW, tag_target)

    doc.InsertObject(target_null, pred=light_object, checknames=True)  # Insert null
    doc.AddUndo(c4d.UNDOTYPE_NEW, target_null)

    doc.EndUndo()  # ----End UNDO

    # Name the target null
    target_null[c4d.ID_BASELIST_NAME] = "target | {} | {}".format(
            light_object[c4d.ID_BASELIST_NAME],
            doc.GetActiveObject()[c4d.ID_BASELIST_NAME])

    # Null gets position of active object, add null to tag link
    offset = doc.GetActiveObject().GetMg()
    target_null[c4d.ID_BASEOBJECT_REL_POSITION] = offset.off
    tag_target[c4d.TARGETEXPRESSIONTAG_LINK] = target_null


# Create Light and target tag to new null object at (0,0,0)
def create_null_object_target(light_object, tag_target):
    doc.StartUndo()  # ----Start UNDO

    doc.InsertObject(light_object, checknames=True)  # Insert Light Object
    doc.AddUndo(c4d.UNDOTYPE_NEW, light_object)

    target_null = target_null_setup()  # Create target null
    doc.AddUndo(c4d.UNDOTYPE_NEW, target_null)

    light_object.InsertTag(tag_target)  # Insert target tag to light
    doc.AddUndo(c4d.UNDOTYPE_NEW, tag_target)

    doc.InsertObject(target_null, pred=light_object, checknames=True)  # Insert null
    doc.AddUndo(c4d.UNDOTYPE_NEW, target_null)

    doc.EndUndo()  # ----End UNDO

    # Name target null and link target tag to null
    target_null[c4d.ID_BASELIST_NAME] += ' | ' + light_object[c4d.ID_BASELIST_NAME]
    tag_target[c4d.TARGETEXPRESSIONTAG_LINK] = target_null


# Create Light at view
def create_light_at_view(light_object):
    doc.StartUndo()  # ----Start UNDO

    doc.InsertObject(light_object, checknames=True)  # Insert Light Object
    doc.AddUndo(c4d.UNDOTYPE_NEW, light_object)

    doc.EndUndo()  # ----End UNDO


# Assign current light object to current camera position
def change_light_position():
    doc.StartUndo()  # ----Start UNDO
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, doc.GetActiveObject())
    doc.GetActiveObject()[c4d.ID_BASEOBJECT_REL_POSITION] = get_view_data()[0]
    doc.EndUndo()  # ----End UNDO


# Create list of light objects in active document
def GetNodes(obj, nodelist=[]):
    while(obj):
        if obj.IsInstanceOf(c4d.Olight) and obj.GetTag(c4d.Ttargetexpression):
            nodelist.append(obj)
        if obj.GetDown():
            GetNodes(obj.GetDown(), nodelist)

        obj = obj.GetNext()

    return nodelist

# Main function
def main():
    light_object = light_setup()
    tag_target = c4d.BaseTag(c4d.Ttargetexpression)

    # Help F1 + Click
    bc1 = c4d.BaseContainer()
    if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, c4d.KEY_ESC, bc1):
        if bc1[c4d.BFM_INPUT_VALUE] == 1:
            gui.MessageDialog('CMD\\CTRL - Spotlight' + '\n'
                + 'OPT\\ALT - Light with Target Null' + '\n'
                + 'SHIFT - Renames targets to user set light name')

    # Container for keyboard input
    bc = c4d.BaseContainer()
    c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, c4d.BFM_INPUT_VALUE, bc)

    # Rename targets
    if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QUALIFIER_SHIFT:
        # Generate list for all lights with target tag
        # Start with first active object and find lights
        nodelist = GetNodes(doc.GetFirstObject())

        doc.StartUndo()  # ----Start UNDO

        # Rename items in nodelist
        if nodelist:
            for item in nodelist:
                null_target = item.GetTag(c4d.Ttargetexpression)[c4d.TARGETEXPRESSIONTAG_LINK]
                parsed_name = null_target.GetName().split(' | ')

                # 3 word targets, 2 word targets
                if item.GetName() != parsed_name and len(parsed_name) > 2:
                    doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL, null_target)
                    null_target[c4d.ID_BASELIST_NAME] = "target | " + \
                            item.GetName() + ' | ' + parsed_name[2]
                else:
                    doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL, null_target)
                    null_target[c4d.ID_BASELIST_NAME] = "target | " + item.GetName()

        doc.EndUndo()  # ----End UNDO

    # Check for active object
    if doc.GetActiveObject() and not bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QUALIFIER_SHIFT:
        # Change positioin if op is and instance of c4d.Olight and has a target tag
        if doc.GetActiveObject().IsInstanceOf(c4d.Olight) and \
           doc.GetActiveObject().GetTag(c4d.Ttargetexpression):
            change_light_position()
        # Change positioin if op is only an instance of c4d.Olight
        elif doc.GetActiveObject().IsInstanceOf(c4d.Olight):
            doc.GetActiveObject()[c4d.ID_BASEOBJECT_REL_POSITION] = get_view_data()[0]
            doc.GetActiveObject()[c4d.ID_BASEOBJECT_REL_ROTATION] = get_view_data()[1]
        # Create light and target if op is not an instance of c4d.Olight
        elif not doc.GetActiveObject().IsInstanceOf(c4d.Olight):
            create_active_object_target(light_object, tag_target)

    # Check if no object selected, create target null (0,0,0)
    if not doc.GetActiveObject() and not bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QUALIFIER_SHIFT:
        if not bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT:
            # create ligh at current view
            create_light_at_view(light_object)
        else:
            # create light at current view with target null
            create_null_object_target(light_object, tag_target)

    c4d.EventAdd()


# Execute main()
if __name__ == '__main__':
    main()
