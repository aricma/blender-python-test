import dataclasses

import bpy
from typing import Tuple, List


class Utils:

    @classmethod
    def purge_orphans(cls):
        if bpy.app.version >= (3, 0, 0):
            bpy.ops.outliner.orphans_purge(
                do_local_ids=True, do_linked_ids=True, do_recursive=True
            )
        else:
            # call purge_orphans() recursively until there are no more orphan data blocks to purge
            result = bpy.ops.outliner.orphans_purge()
            if result.pop() != "CANCELLED":
                cls.purge_orphans()

    @classmethod
    def clean_scene(cls):
        """
        Removing all of the objects, collection, materials, particles,
        textures, images, curves, meshes, actions, nodes, and worlds from the scene
        """
        if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
            bpy.ops.object.editmode_toggle()

        for obj in bpy.data.objects:
            obj.hide_set(False)
            obj.hide_select = False
            obj.hide_viewport = False

        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

        collection_names = [col.name for col in bpy.data.collections]
        for name in collection_names:
            bpy.data.collections.remove(bpy.data.collections[name])

        # in the case when you modify the world shader
        world_names = [world.name for world in bpy.data.worlds]
        for name in world_names:
            bpy.data.worlds.remove(bpy.data.worlds[name])
        # create a new world data block
        bpy.ops.world.new()
        bpy.context.scene.world = bpy.data.worlds["World"]

        cls.purge_orphans()


@dataclasses.dataclass
class Point:
    x: float
    y: float
    z: float

    @property
    def __tuple__(self) -> Tuple[float, float, float]:
        return self.x, self.y, self.z

    @property
    def __list__(self) -> List[float]:
        return [self.x, self.y, self.z]


ORIGIN = Point(0, 0, 0)


class PlaceableMeshInterface:

    def place(self, at: Point = ORIGIN) -> None:
        raise NotImplementedError


@dataclasses.dataclass
class Cube(PlaceableMeshInterface):
    size: float

    def place(self, at: Point = ORIGIN) -> None:
        bpy.ops.mesh.primitive_cube_add(
            size=self.size,
            location=at.__list__
        )


@dataclasses.dataclass
class WoodenPole(PlaceableMeshInterface):
    width: float = 1
    height: float = 10
    bevel: float = .2

    def place(self, at: Point = ORIGIN) -> None:
        bpy.ops.mesh.primitive_cube_add(
            size=self.width,
            location=at.__list__
        )
        bpy.ops.transform.resize(
            value=[1, 1, self.height],
            orient_type='GLOBAL',
            orient_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            orient_matrix_type='GLOBAL',
            constraint_axis=[False, False, True],
            mirror=False,
            use_proportional_edit=False,
            proportional_edit_falloff='SMOOTH',
            proportional_size=1,
            use_proportional_connected=False,
            use_proportional_projected=False,
            release_confirm=True
        )
        bpy.ops.object.modifier_add(
            type='BEVEL',
        )


class Susanne(PlaceableMeshInterface):

    def place(self, at: Point = ORIGIN) -> None:
        bpy.ops.mesh.primitive_monkey_add(location=at.__list__)


if __name__ == '__main__':
    Utils.clean_scene()
    WoodenPole().place()
