"""
It's Lit: It's Lit v1 (02/19)
Copyright Algernon Quashie 2019

Name-US: It's Lit
Description-US: Create Area light and target null (Shift + Click for Spotlight)
and moves light to current view position
"""

import c4d
from c4d import gui


# camera view or editor view
def get_cam_pos():
    bd = doc.GetRenderBaseDraw()  # editor camera
    scene_cam = bd.GetSceneCamera(doc)  # scene camera
    if scene_cam is None:
        scene_cam = bd.GetEditorCamera()
    return scene_cam.GetOffset()


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

    # Default Area Light, Press Shift for Spotlight
    light_type = 8  # Area Light
    bc = c4d.BaseContainer()
    c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, c4d.BFM_INPUT_VALUE, bc)
    if bc[c4d.BFM_INPUT_QUALIFIER] == c4d.QUALIFIER_CTRL:
        light_type = 1

    light = c4d.BaseObject(c4d.Olight).GetClone()
    light[c4d.ID_BASEOBJECT_REL_POSITION] = get_cam_pos()
    light[c4d.LIGHT_TYPE] = light_type
    light[c4d.LIGHT_SHADOWTYPE] = 1

    if light_type == 1 and doc.GetActiveObject():
        light[c4d.LIGHT_DETAILS_FALLOFF] = c4d.LIGHT_DETAILS_FALLOFF_INVERSESQUARE
        p1 = light.GetMg().off
        p2 = doc.GetActiveObject().GetMg().off
        dist = (p2-p1).GetLength()
        light[c4d.LIGHT_DETAILS_OUTERDISTANCE] = dist

    return light


# Create Light and target tag to active object
def create_active_object_target(light_object, tag_target):
    # add target tag link to active object
    #tag_target[c4d.TARGETEXPRESSIONTAG_LINK] = doc.GetActiveObject()

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

    #target_null[c4d.ID_BASELIST_NAME] += light_object[c4d.ID_BASELIST_NAME].strip('Light')
    target_null[c4d.ID_BASELIST_NAME] = "target | " + \
        light_object[c4d.ID_BASELIST_NAME] + " | " + \
        doc.GetActiveObject()[c4d.ID_BASELIST_NAME]

    target_null[c4d.ID_BASEOBJECT_REL_POSITION] = doc.GetActiveObject().GetAbsPos()
    tag_target[c4d.TARGETEXPRESSIONTAG_LINK] = target_null


# Create Light and target tag to new null object
def create_null_object_target(light_object, tag_target):
    doc.StartUndo()  # ----Start UNDO

    doc.InsertObject(light_object, checknames=True)  # Insert Light Object
    doc.AddUndo(c4d.UNDOTYPE_NEW, light_object)

    target_null = target_null_setup()  # Create target null
    doc.AddUndo(c4d.UNDOTYPE_NEW, target_null)

    # target_null[c4d.ID_BASELIST_NAME] += light_object[c4d.ID_BASELIST_NAME].strip('Light')
    target_null[c4d.ID_BASELIST_NAME] += ' | ' + light_object[c4d.ID_BASELIST_NAME]

    light_object.InsertTag(tag_target)  # Insert target tag to light
    doc.AddUndo(c4d.UNDOTYPE_NEW, tag_target)

    doc.InsertObject(target_null, pred=light_object, checknames=True)  # Insert null
    doc.AddUndo(c4d.UNDOTYPE_NEW, target_null)

    doc.EndUndo()  # ----End UNDO
    tag_target[c4d.TARGETEXPRESSIONTAG_LINK] = target_null  # add target tag link to new null


# Assign current light object to current camera position
def change_light_position():
    doc.StartUndo()  # ----Start UNDO
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, doc.GetActiveObject())
    doc.GetActiveObject()[c4d.ID_BASEOBJECT_REL_POSITION] = get_cam_pos()
    doc.EndUndo()  # ----End UNDO
    return


# Get Nodes
def GetNodes(obj, nodelist=[]):

    while(obj):
        if obj.IsInstanceOf(c4d.Olight):
            nodelist.append(obj)
        if obj.GetDown():
            GetNodes(obj.GetDown(), nodelist)

        obj = obj.GetNext()

    return nodelist

# Main function
def main():
    light_object = light_setup()
    tag_target = c4d.BaseTag(c4d.Ttargetexpression)

    # Check if wanting to rename targets
    bc = c4d.BaseContainer()
    c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, c4d.BFM_INPUT_VALUE, bc)
    if bc[c4d.BFM_INPUT_QUALIFIER] == c4d.QUALIFIER_SHIFT:
        print "Shift Clicked"
        first_object = doc.GetFirstObject()
        print doc.GetFirstObject()
        print type(first_object)

        nodelist = GetNodes(first_object)
        print len(nodelist)

        if nodelist:
            for item in nodelist:
                # print type(item.GetTag(c4d.Ttargetexpression)[c4d.TARGETEXPRESSIONTAG_LINK])
                print item.GetName()
                # null_target = doc.SearchObject(item.GetTag(c4d.Ttargetexpression)[c4d.TARGETEXPRESSIONTAG_LINK])
                null_target = item.GetTag(c4d.Ttargetexpression)[c4d.TARGETEXPRESSIONTAG_LINK]
                print null_target.GetName()
                actual_name = null_target.GetName().split(' | ')
                print actual_name[1]

                if item.GetName() != actual_name and len(actual_name) > 2:
                    null_target[c4d.ID_BASELIST_NAME] = "target | " + \
                            item.GetName() + ' | ' + actual_name[2]
                else:
                    null_target[c4d.ID_BASELIST_NAME] = "target | " + item.GetName()


    # Check for active object
    if doc.GetActiveObject() and not bc[c4d.BFM_INPUT_QUALIFIER] == c4d.QUALIFIER_SHIFT:
        # Change positioin if op is and instance of c4d.Olight and has a target tag
        if doc.GetActiveObject().IsInstanceOf(c4d.Olight) and \
           doc.GetActiveObject().GetTag(c4d.Ttargetexpression):
            change_light_position()
        # Change positioin if op is only an instance of c4d.Olight
        elif doc.GetActiveObject().IsInstanceOf(c4d.Olight):
            doc.GetActiveObject()[c4d.ID_BASEOBJECT_REL_POSITION] = get_cam_pos()
        # Create light and target if op is not an instance of c4d.Olight
        elif not doc.GetActiveObject().IsInstanceOf(c4d.Olight):
            create_active_object_target(light_object, tag_target)

    # Check if no object selected, create target null (0,0,0)
    if not doc.GetActiveObject() and not bc[c4d.BFM_INPUT_QUALIFIER] == c4d.QUALIFIER_SHIFT:
        create_null_object_target(light_object, tag_target)

    c4d.EventAdd()


# Execute main()
if __name__ == '__main__':
    main()
