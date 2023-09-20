import bpy
import bmesh
from bpy.props import StringProperty, IntProperty, CollectionProperty, FloatProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel

##################################################
# List of properties to be added to the material #
##################################################

class SelectedNode(PropertyGroup):
    node: bpy.props.IntProperty()

class ListItem(PropertyGroup):
    """Group of properties representing an item in the list."""

    name: StringProperty(
        name="Name",
        description="A name for this item",
        default="Untitled",
    )

    index: IntProperty(
        name="Index",
        description="Unique index",
    )

    emissivity: FloatProperty(
        name="Emissivity",
        description="Emissivity of the material",
        default=0.5,
        min=0,
        max=1,
    )

    absorptivity: FloatProperty(
        name="Absorptivity",
        description="Absorptivity of the material",
        default=0.5,
        min=0,
        max=1,
    )

    selected_nodes: CollectionProperty(
        type = SelectedNode,
        name="selected_nodes",
        description="Selected nodes",
    )

class PT_UL_CustomMaterials(UIList):
    """Custom Materials UIList. This is the component which renders the box."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.4)
            split.label(text="Index: %d" % (item.index))
            layout.label(text=item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='', icon = custom_icon)

###############################################
# Operators to add, remove and move materials #
###############################################

class LIST_OT_NewMaterial(Operator):
    """Add a new material to the list."""

    bl_idname = "mat_prop_list.new_material"
    bl_label = "Add a new material"

    def execute(self, context):
        context.scene.mat_prop_list.add()
        context.scene.mat_prop_list[-1].index = context.scene.unique_index
        context.scene.unique_index += 1

        return{'FINISHED'}


class LIST_OT_DeleteMaterial(Operator):
    """Delete the selected material from the list."""

    bl_idname = "mat_prop_list.delete_material"
    bl_label = "Deletes an material"

    @classmethod
    def poll(cls, context):
        return context.scene.mat_prop_list

    def execute(self, context):
        mat_prop_list = context.scene.mat_prop_list
        index = context.scene.list_index

        mat_prop_list.remove(index)
        context.scene.list_index = min(max(0, index - 1), len(mat_prop_list) - 1)

        return{'FINISHED'}


class LIST_OT_MoveMaterial(Operator):
    """Move an material in the list."""

    bl_idname = "mat_prop_list.move_material"
    bl_label = "Move an material in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.scene.mat_prop_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.list_index
        list_length = len(bpy.context.scene.mat_prop_list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        mat_prop_list = context.scene.mat_prop_list
        index = context.scene.list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        mat_prop_list.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}

class LIST_OT_AddNodes(Operator):
    """Add selected nodes to the material list."""
    
    bl_idname = "mat_prop_list.add_nodes"
    bl_label = "Add nodes"

    @classmethod
    def poll(cls, context):
        return context.scene.mat_prop_list

    def execute(self, context):
        mat_prop_list = context.scene.mat_prop_list
        selected_nodes = mat_prop_list[context.scene.list_index].selected_nodes

        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode = 'EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        for node in bm.verts:
            # if node is selected and not already in the list
            if node.select and not any(node.index == x.node for x in selected_nodes):
                selected_nodes.add()
                selected_nodes[-1].node = node.index
                # if node was already in other material, remove it from that material
                for material in mat_prop_list:
                    if material.index == mat_prop_list[context.scene.list_index].index:
                        continue
                    for selected_node in material.selected_nodes:
                        if selected_node.node.index == node.index:
                            material.selected_nodes.remove(selected_node)

        return{'FINISHED'}

#################################################
# Panel to display the list of custom materials #
#################################################

class PT_CustomMaterial(Panel):
    """Custom Material Panel"""

    bl_label = "UI_Custom_Material"
    bl_idname = "SCENE_PT_CUSTOM_MATERIAL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.template_list("PT_UL_CustomMaterials", "The_List", scene,
                          "mat_prop_list", scene, "list_index")

        col = row.column(align=True)
        col.operator('mat_prop_list.new_material', text='', icon="ADD")
        col.operator('mat_prop_list.delete_material', text='', icon="REMOVE")
        col.separator()
        col.operator('mat_prop_list.move_material', text='', icon="TRIA_UP").direction = 'UP'
        col.operator('mat_prop_list.move_material', text='', icon="TRIA_DOWN").direction = 'DOWN'

        col = layout.column(align=True)
        col.operator('mat_prop_list.add_nodes', text='Add selected nodes', icon="ADD")

        if scene.list_index >= 0 and scene.mat_prop_list:
            material = scene.mat_prop_list[scene.list_index]

            layout.row().prop(material, 'name')
            layout.row().prop(material, 'emissivity')
            layout.row().prop(material, 'absorptivity')
            layout.row().prop(material, 'selected_nodes')
            print(material.selected_nodes)

##############################################
# Registration and unregistration of classes #
##############################################

def custom_materials_register():
    bpy.utils.register_class(SelectedNode)
    bpy.utils.register_class(ListItem)
    bpy.utils.register_class(PT_UL_CustomMaterials)
    bpy.utils.register_class(LIST_OT_NewMaterial)
    bpy.utils.register_class(LIST_OT_DeleteMaterial)
    bpy.utils.register_class(LIST_OT_MoveMaterial)
    bpy.utils.register_class(LIST_OT_AddNodes)
    bpy.utils.register_class(PT_CustomMaterial)

    bpy.types.Scene.mat_prop_list = CollectionProperty(type = ListItem)
    bpy.types.Scene.list_index = IntProperty(name = "Index for mat_prop_list",
                                             default = 0)
    bpy.types.Scene.unique_index = IntProperty(name = "Unique index for mat_prop_list",
                                             default = 0)

def custom_materials_unregister():
    del bpy.types.Scene.mat_prop_list
    del bpy.types.Scene.list_index
    del bpy.types.Scene.unique_index

    bpy.utils.unregister_class(SelectedNode)
    bpy.utils.unregister_class(ListItem)
    bpy.utils.unregister_class(PT_UL_CustomMaterials)
    bpy.utils.unregister_class(LIST_OT_NewMaterial)
    bpy.utils.unregister_class(LIST_OT_DeleteMaterial)
    bpy.utils.unregister_class(LIST_OT_MoveMaterial)
    bpy.utils.unregister_class(LIST_OT_AddNodes)
    bpy.utils.unregister_class(PT_CustomMaterial)
