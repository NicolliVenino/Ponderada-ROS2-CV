"""
dog_draw.launch.py
==================
Arquivo de launch que inicia o turtlesim_node e o dog_drawer_node
em sequência, com delay para garantir que o simulador esteja pronto.

Uso:
    ros2 launch dog_drawer dog_draw.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction


def generate_launch_description():
    # Nó do simulador Turtlesim
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    # Nó de desenho — aguarda 2s para o turtlesim inicializar
    dog_drawer_node = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='dog_drawer',
                executable='dog_drawer_node',
                name='dog_drawer_node',
                output='screen',
            )
        ]
    )

    return LaunchDescription([
        turtlesim_node,
        dog_drawer_node,
    ])
