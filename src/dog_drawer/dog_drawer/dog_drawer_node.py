#!/usr/bin/env python3
"""
dog_drawer_node.py
==================
Nó ROS2 que desenha o contorno de um cachorro (French Bulldog)
no simulador Turtlesim usando navegação point-to-point com
controle proporcional de velocidade.

Uso:
    ros2 run dog_drawer dog_drawer_node
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, TeleportAbsolute, Kill, Spawn
from std_srvs.srv import Empty
from rclpy.callback_groups import ReentrantCallbackGroup


# ---------------------------------------------------------------------------
# Pontos do contorno mapeados para o espaço do Turtlesim (0-11 x 0-11)
# Extraídos da imagem contorno_grosso__2_.png
# ---------------------------------------------------------------------------
CONTOUR_POINTS = [
    [8.0571, 10.0], [7.5857, 9.5714], [7.3857, 9.1571], [7.2571, 8.5286],
    [7.1, 8.4143], [6.1286, 8.5], [5.7143, 9.4714], [5.2571, 9.9],
    [4.9, 9.9429], [4.6286, 9.7429], [4.4857, 9.1714], [4.5571, 7.7857],
    [5.0286, 6.9286], [4.9857, 5.6571], [4.8429, 5.1286], [4.9286, 3.7571],
    [4.6857, 2.6429], [4.4143, 2.7143], [4.3286, 2.8857], [3.4857, 2.8143],
    [2.7857, 2.4143], [2.0714, 2.2143], [1.0857, 1.7857], [1.0, 1.5857],
    [1.1286, 1.4429], [1.8571, 1.4], [1.8714, 1.2429], [4.4857, 1.3286],
    [5.2429, 1.1714], [4.5429, 1.3857], [2.1143, 1.3143], [1.9143, 1.4571],
    [1.5286, 1.5429], [1.1857, 1.5], [1.0857, 1.6571], [2.1429, 2.1571],
    [2.8429, 2.3571], [3.5429, 2.7571], [4.1857, 2.8429], [4.4286, 2.6],
    [4.7429, 2.5429], [5.0, 3.7429], [4.9, 5.0714], [5.0429, 5.6],
    [5.0857, 6.9857], [4.6143, 7.8429], [4.5429, 9.1143], [4.6857, 9.6857],
    [4.8571, 9.8429], [5.0857, 9.8857], [5.4714, 9.6429], [5.8, 9.1714],
    [6.0714, 8.4429], [7.2429, 8.3429], [7.3571, 8.4714], [7.4143, 9.0],
    [7.6429, 9.5143], [7.9571, 9.8714], [8.2143, 9.9429], [8.5, 9.7571],
    [8.6286, 9.5], [8.7286, 7.8429], [8.4571, 7.3], [8.3286, 7.2429],
    [8.4429, 6.7143], [8.4, 6.0571], [8.1286, 5.4143], [8.1429, 5.2714],
    [7.8714, 5.0143], [7.8714, 4.5714], [7.9714, 4.5429], [8.0714, 4.6429],
    [7.9857, 4.9429], [8.3143, 5.0571], [8.2857, 5.2286], [8.4571, 5.4429],
    [8.6571, 4.9286], [9.0857, 4.7143], [9.2571, 4.4714], [9.4429, 3.6143],
    [9.9429, 2.8143], [9.7857, 2.5143], [9.3714, 2.4286], [9.3143, 1.7],
    [9.6571, 1.3714], [9.7143, 1.1714], [9.7857, 1.1857], [9.7143, 1.4286],
    [9.3714, 1.7571], [9.4286, 2.3714], [9.8429, 2.4571], [10.0, 2.6571],
    [10.0, 2.8714], [9.5, 3.6714], [9.4429, 4.1857], [9.2571, 4.6286],
    [8.7143, 4.9857], [8.5714, 5.4286], [8.3143, 5.5857], [8.5143, 6.4],
    [8.3857, 7.1857], [8.5, 7.2143], [8.7857, 7.7857], [8.7, 8.5],
    [8.7571, 9.1857], [8.5571, 9.8143], [8.3714, 9.9714], [8.0714, 10.0],
]


class DogDrawerNode(Node):
    """Nó que teleporta a tartaruga para o ponto inicial e depois
    navega point-to-point desenhando o contorno do cachorro."""

    # Parâmetros de controle
    LINEAR_SPEED   = 3.0   # velocidade linear máxima (m/s simulado)
    ANGULAR_SPEED  = 4.0   # velocidade angular máxima (rad/s)
    KP_LINEAR      = 1.5   # ganho proporcional linear
    KP_ANGULAR     = 6.0   # ganho proporcional angular
    GOAL_TOLERANCE = 0.08  # distância para considerar ponto atingido (m)
    RATE_HZ        = 50.0  # frequência do loop de controle

    def __init__(self):
        super().__init__('dog_drawer_node')

        self.cb_group = ReentrantCallbackGroup()

        # Publisher de velocidade
        self.cmd_vel_pub = self.create_publisher(
            Twist, '/turtle1/cmd_vel', 10)

        # Subscriber de pose
        self.pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose',
            self._pose_callback, 10,
            callback_group=self.cb_group)

        # Clientes de serviço
        self.set_pen_cli      = self.create_client(SetPen,          '/turtle1/set_pen')
        self.teleport_cli     = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.clear_cli        = self.create_client(Empty,            '/clear')

        self.get_logger().info('DogDrawerNode iniciado. Aguardando turtlesim...')

        # Timer principal (inicia após serviços disponíveis)
        self._drawing_started = False
        self._init_timer = self.create_timer(
            1.0, self._check_services,
            callback_group=self.cb_group)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _pose_callback(self, msg: Pose):
        self.pose = msg

    def _check_services(self):
        """Aguarda todos os serviços ficarem disponíveis antes de começar."""
        services = [self.set_pen_cli, self.teleport_cli, self.clear_cli]
        if all(s.service_is_ready() for s in services) and not self._drawing_started:
            self._drawing_started = True
            self._init_timer.cancel()
            self.get_logger().info('Todos os serviços prontos! Iniciando desenho...')
            # Cria timer de controle
            self._point_index = 0
            self._phase = 'clear'          # estados: clear → teleport → draw → done
            self._control_timer = self.create_timer(
                1.0 / self.RATE_HZ,
                self._control_loop,
                callback_group=self.cb_group)

    def _control_loop(self):
        """Loop principal de controle de estados."""
        if self._phase == 'clear':
            self._do_clear()

        elif self._phase == 'teleport':
            self._do_teleport()

        elif self._phase == 'draw':
            if self.pose is None:
                return
            self._navigate_to_next_point()

        elif self._phase == 'done':
            self._stop_turtle()
            self.get_logger().info('✅  Contorno do cachorro concluído!')
            self._control_timer.cancel()

    # ------------------------------------------------------------------
    # Fases
    # ------------------------------------------------------------------

    def _do_clear(self):
        """Limpa a tela e desliga a caneta."""
        self._phase = 'waiting_clear'
        self.get_logger().info('Limpando tela...')
        future = self.clear_cli.call_async(Empty.Request())
        future.add_done_callback(lambda _: self._pen_off_then_teleport())

    def _pen_off_then_teleport(self):
        req = SetPen.Request()
        req.r, req.g, req.b = 0, 0, 0
        req.width = 0
        req.off = True
        future = self.set_pen_cli.call_async(req)
        future.add_done_callback(lambda _: self._set_phase('teleport'))

    def _set_phase(self, phase: str):
        self._phase = phase

    def _do_teleport(self):
        """Teleporta para o primeiro ponto do contorno (sem desenhar)."""
        self._phase = 'waiting_teleport'
        x0, y0 = CONTOUR_POINTS[0]
        self.get_logger().info(f'Teleportando para ponto inicial ({x0:.2f}, {y0:.2f})...')
        req = TeleportAbsolute.Request()
        req.x, req.y = float(x0), float(y0)
        req.theta = 0.0
        future = self.teleport_cli.call_async(req)
        future.add_done_callback(lambda _: self._pen_on())

    def _pen_on(self):
        """Liga a caneta branca e inicia o desenho."""
        req = SetPen.Request()
        req.r, req.g, req.b = 255, 255, 255
        req.width = 2
        req.off = False
        future = self.set_pen_cli.call_async(req)
        future.add_done_callback(lambda _: self._start_drawing())

    def _start_drawing(self):
        self._point_index = 1   # começa do segundo ponto
        self._phase = 'draw'
        self.get_logger().info(
            f'Caneta ligada. Desenhando {len(CONTOUR_POINTS)} pontos...')

    # ------------------------------------------------------------------
    # Navegação point-to-point com controle proporcional
    # ------------------------------------------------------------------

    def _navigate_to_next_point(self):
        if self._point_index >= len(CONTOUR_POINTS):
            # Fecha o contorno voltando ao ponto inicial
            self._point_index = len(CONTOUR_POINTS)  # sentinela
            self._phase = 'done'
            return

        gx, gy = CONTOUR_POINTS[self._point_index]
        gx, gy = float(gx), float(gy)

        dx = gx - self.pose.x
        dy = gy - self.pose.y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < self.GOAL_TOLERANCE:
            pct = int(100 * self._point_index / len(CONTOUR_POINTS))
            self.get_logger().info(
                f'[{pct:3d}%] Ponto {self._point_index}/{len(CONTOUR_POINTS)-1} '
                f'atingido ({gx:.2f}, {gy:.2f})')
            self._point_index += 1
            return

        # Ângulo desejado
        desired_angle = math.atan2(dy, dx)
        angle_error   = self._normalize_angle(desired_angle - self.pose.theta)

        # Controle proporcional
        linear  = min(self.KP_LINEAR  * dist,       self.LINEAR_SPEED)
        angular = max(min(self.KP_ANGULAR * angle_error, self.ANGULAR_SPEED),
                      -self.ANGULAR_SPEED)

        # Reduz linear se ângulo muito grande
        if abs(angle_error) > math.pi / 4:
            linear *= 0.3

        twist = Twist()
        twist.linear.x  = linear
        twist.angular.z = angular
        self.cmd_vel_pub.publish(twist)

    def _stop_turtle(self):
        self.cmd_vel_pub.publish(Twist())

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        while angle >  math.pi: angle -= 2 * math.pi
        while angle < -math.pi: angle += 2 * math.pi
        return angle


# ---------------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)
    node = DogDrawerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
