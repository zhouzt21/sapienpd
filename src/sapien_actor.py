"""Create actors (rigid bodies).

The actor (or rigid body) in Sapien is created through a sapien.ActorBuilder. An
actor is an SAPIEN entity that typically consists of a rigid body component (for
physical simulation) and a visual component (for rendering). Note that can have
multiple collision and visual shapes, and they do not need to correspond.

Concepts:
    - Create an actor by primitives (box, sphere, capsule)
    - Create an actor by mesh files
    - sapien.Pose

"""

import sapien as sapien
from sapien.utils import Viewer
import numpy as np

import sapienpd
from sapienpd.pd_config import PDConfig
from sapienpd.pd_system import PDSystem
from sapienpd.pd_component import PDClothComponent, PDBodyComponent

import igl


def create_box(
    scene: sapien.Scene,
    pose: sapien.Pose,
    half_size,
    color=None,
    name="",
) -> sapien.Entity:
    """Create a box.

    Args:
        scene: sapien.Scene to create a box.
        pose: 6D pose of the box.
        half_size: [3], half size along x, y, z axes.
        color: [4], rgba
        name: name of the actor.

    Returns:
        sapien.Entity
    """
    entity = sapien.Entity()
    entity.set_name(name)
    entity.set_pose(pose)

    # create PhysX dynamic rigid body
    rigid_component = sapien.physx.PhysxRigidDynamicComponent()
    rigid_component.attach(
        sapien.physx.PhysxCollisionShapeBox(
            half_size=half_size, material=sapien.physx.get_default_material()
        )
    )

    # create render body for visualization
    render_component = sapien.render.RenderBodyComponent()
    render_component.attach(
        # add a box visual shape with given size and rendering material
        sapien.render.RenderShapeBox(
            half_size, sapien.render.RenderMaterial(base_color=[*color[:3], 1])
        )
    )

    entity.add_component(rigid_component)
    entity.add_component(render_component)
    entity.set_pose(pose)

    # in general, entity should only be added to scene after it is fully built
    scene.add_entity(entity)

    # name and pose may be changed after added to scene
    # entity.set_name(name)
    # entity.set_pose(pose)

    return entity


def create_box_v2(
    scene: sapien.Scene,
    pose: sapien.Pose,
    half_size,
    color=None,
    name="",
) -> sapien.Entity:
    """Create a box.

    Args:
        scene: sapien.Scene to create a box.
        pose: 6D pose of the box.
        half_size: [3], half size along x, y, z axes.
        color: [3] or [4], rgb or rgba
        name: name of the actor.

    Returns:
        sapien.Entity
    """
    half_size = np.array(half_size)
    builder: sapien.ActorBuilder = scene.create_actor_builder()
    builder.add_box_collision(half_size=half_size)  # Add collision shape
    builder.add_box_visual(half_size=half_size, material=color)  # Add visual shape
    box: sapien.Entity = builder.build(name=name)
    box.set_pose(pose)
    return box


def create_sphere(
    scene: sapien.Scene,
    pose: sapien.Pose,
    radius,
    color=None,
    name="",
) -> sapien.Entity:
    """Create a sphere. See create_box."""
    builder = scene.create_actor_builder()
    builder.add_sphere_collision(radius=radius)
    builder.add_sphere_visual(radius=radius, material=color)
    sphere = builder.build(name=name)
    sphere.set_pose(pose)
    return sphere


def create_capsule(
    scene: sapien.Scene,
    pose: sapien.Pose,
    radius,
    half_length,
    color=None,
    name="",
) -> sapien.Entity:
    """Create a capsule (x-axis <-> half_length). See create_box."""
    builder = scene.create_actor_builder()
    builder.add_capsule_collision(radius=radius, half_length=half_length)
    builder.add_capsule_visual(radius=radius, half_length=half_length, material=color)
    capsule = builder.build(name=name)
    capsule.set_pose(pose)
    return capsule


def create_table(
    scene: sapien.Scene,
    pose: sapien.Pose,
    size,
    height,
    thickness=0.1,
    color=(0.8, 0.6, 0.4),
    name="table",
) -> sapien.Entity:
    """Create a table (a collection of collision and visual shapes)."""
    builder = scene.create_actor_builder()

    # Tabletop
    tabletop_pose = sapien.Pose(
        [0.0, 0.0, -thickness / 2]
    )  # Make the top surface's z equal to 0
    tabletop_half_size = [size / 2, size / 2, thickness / 2]
    builder.add_box_collision(pose=tabletop_pose, half_size=tabletop_half_size)
    builder.add_box_visual(
        pose=tabletop_pose, half_size=tabletop_half_size, material=color
    )

    # Table legs (x4)
    for i in [-1, 1]:
        for j in [-1, 1]:
            x = i * (size - thickness) / 2
            y = j * (size - thickness) / 2
            table_leg_pose = sapien.Pose([x, y, -height / 2])
            table_leg_half_size = [thickness / 2, thickness / 2, height / 2]
            builder.add_box_collision(
                pose=table_leg_pose, half_size=table_leg_half_size
            )
            builder.add_box_visual(
                pose=table_leg_pose, half_size=table_leg_half_size, material=color
            )

    table = builder.build(name=name)
    table.set_pose(pose)
    return table


def main():
    default_material = sapien.physx.get_default_material()
    sapien.physx.set_default_material(0.0, 0.0, default_material.restitution)
    default_material = sapien.physx.get_default_material()
    print(default_material.static_friction)
    print(default_material.dynamic_friction)

    engine = sapien.Engine()
    renderer = sapien.SapienRenderer()
    engine.set_renderer(renderer)

    scene = engine.create_scene()
    scene.set_timestep(1 / 100.0)

    pd_config = PDConfig()
    pd_config.time_step = 0.2 / 100.0
    pd_config.collision_margin = 0.2e-3
    pd_config.collision_sphere_radius = 1.6e-3
    pd_config.collision_weight = 5e3
    pd_config.chebyshev_flag = True
    pd_system = PDSystem(pd_config)
    scene.add_system(pd_system)

    # ---------------------------------------------------------------------------- #
    # Add actors
    # ---------------------------------------------------------------------------- #
    scene.add_ground(altitude=0)  # The ground is in fact a special actor.
    box = create_box(
        scene,
        sapien.Pose(p=[0, 0, 1.0 + 0.05]),
        half_size=[0.05, 0.05, 0.05],
        color=[1.0, 0.0, 0.0],
        name="box",
    )
    sphere = create_sphere(
        scene,
        sapien.Pose(p=[0, -0.2, 1.0 + 0.05]),
        radius=0.05,
        color=[0.0, 1.0, 0.0],
        name="sphere",
    )
    capsule = create_capsule(
        scene,
        sapien.Pose(p=[0, 0.2, 1.0 + 0.05]),
        radius=0.05,
        half_length=0.05,
        color=[0.0, 0.0, 1.0],
        name="capsule",
    )
    table = create_table(
        scene,
        sapien.Pose(p=[0, 0, 1.0]),
        size=1.0,
        height=1.0,
    )

    # add a mesh
    builder = scene.create_actor_builder()
    # builder.add_convex_collision_from_file(
    #     filename="assets/banana/collision_meshes/collision.obj"
    # )
    builder.add_multiple_convex_collisions_from_file(
        filename="../assets/banana/collision_meshes/collision.obj"
    )
    builder.add_visual_from_file(filename="../assets/banana/visual_meshes/visual.glb")
    # builder.add_visual_from_file(filename="../assets/banana/collision_meshes/collision.obj")
    mesh = builder.build(name="mesh")
    mesh.set_pose(sapien.Pose(p=[-0.2, 0, 1.0 + 0.05]))

    for comp in mesh.get_components():
        if isinstance(comp, sapien.pysapien.physx.PhysxRigidDynamicComponent):
            rigid_comp = comp
            pd_comp = PDBodyComponent.from_physx_shape(comp, grid_size=1e-3)
            mesh.add_component(pd_comp)

    print("pd_comp.frictions", pd_comp.frictions)

    # ---------------------------------------------------------------------------- #

    scene.set_ambient_light([0.5, 0.5, 0.5])
    scene.add_directional_light([0, 1, -1], [0.5, 0.5, 0.5])

    viewer = scene.create_viewer()

    viewer.set_camera_xyz(x=-2, y=0, z=2.5)
    viewer.set_camera_rpy(r=0, p=-np.arctan2(2, 2), y=0)
    viewer.window.set_camera_parameters(near=0.05, far=100, fovy=1)

    # ---------------------------------------------------------------------------- #

    # add a cloth
    cloth_path = "../assets/cloth_51.obj"
    vertices, faces = igl.read_triangle_mesh(cloth_path)
    vertices = vertices * 0.2
    cloth_comp = PDClothComponent(
        vertices,
        faces,
        thickness=1e-3,
        density=1e3,
        stretch_stiffness=1e3,
        bend_stiffness=1e-3,
        friction=0.3,
        collider_iterpolation_depth=0,
    )
    cloth_render = sapien.render.RenderCudaMeshComponent(len(vertices), 2 * len(faces))
    cloth_render.set_vertex_count(len(vertices))
    cloth_render.set_triangle_count(2 * len(faces))
    cloth_render.set_triangles(np.concatenate([faces, faces[:, ::-1]], axis=0))
    cloth_render.set_material(
        sapien.render.RenderMaterial(base_color=[0.7, 0.3, 0.4, 1.0])
    )
    cloth_entity = sapien.Entity()
    cloth_entity.add_component(cloth_comp)
    cloth_entity.add_component(cloth_render)
    # cloth_entity.set_pose(sapien.Pose([0, 0, 0.8], [ 0.9486833, 0, 0, 0.3162278 ]))
    cloth_entity.set_pose(sapien.Pose([-0.3, -0.12, 1.0 + 0.2]))
    # cloth_entity.set_pose(sapien.Pose([0, 0, -0.5], [0.7071068, 0, -0.7071068, 0]))

    scene.add_entity(cloth_entity)

    viewer.paused = True
    sapienpd.scene_update_render(scene)
    viewer.render()

    rigid_comp.set_angular_velocity([0.0, 0.0, 0.1])
    # rigid_comp.set_linear_velocity([0.0, 0.0, 10.0])

    mesh_pose_after = mesh.get_pose()
    mesh_twist = np.concatenate([rigid_comp.get_angular_velocity(), rigid_comp.get_linear_velocity()])
    pd_comp.set_pose_twist(mesh_pose_after, mesh_twist)

    while not viewer.closed:
        for i in range(2):
            mesh_pose_before = mesh.get_pose()
            scene.step()
            mesh_pose_after = mesh.get_pose()
            mesh_twist = np.concatenate([rigid_comp.get_angular_velocity(), rigid_comp.get_linear_velocity()])
            pd_comp.set_pose_twist(mesh_pose_before, mesh_twist)
            for j in range(5):
                pd_system.step()
            # print("mesh_twist", mesh_twist)
        sapienpd.scene_update_render(scene, set_body_pose=False)
        viewer.render()


if __name__ == "__main__":
    main()