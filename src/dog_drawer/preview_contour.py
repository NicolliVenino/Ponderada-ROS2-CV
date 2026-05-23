#!/usr/bin/env python3
"""
preview_contour.py
==================
Script auxiliar (sem ROS) para visualizar os pontos mapeados
no espaço do Turtlesim antes de executar no simulador real.

Uso:
    python3 preview_contour.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

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

pts = np.array(CONTOUR_POINTS)
xs, ys = pts[:, 0], pts[:, 1]

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.patch.set_facecolor('#1a1a2e')

# ---- Painel esquerdo: simulação do Turtlesim ----
ax1 = axes[0]
ax1.set_facecolor('#0a0a1a')
ax1.set_xlim(0, 11.09)
ax1.set_ylim(0, 11.09)
ax1.set_aspect('equal')
ax1.set_title('Simulação Turtlesim', color='white', fontsize=13, pad=10)
ax1.tick_params(colors='gray')
for spine in ax1.spines.values():
    spine.set_edgecolor('#444')

# Grid sutil
ax1.grid(True, color='#222244', linewidth=0.5, alpha=0.7)

# Contorno fechado
closed_xs = np.append(xs, xs[0])
closed_ys = np.append(ys, ys[0])
ax1.plot(closed_xs, closed_ys, color='#00e5ff', linewidth=1.8,
         label=f'Contorno ({len(CONTOUR_POINTS)} pts)', zorder=3)

# Pontos
ax1.scatter(xs, ys, s=25, color='#ff6b35', zorder=4, alpha=0.9)

# Ponto inicial
ax1.scatter(xs[0], ys[0], s=100, color='#00ff88', zorder=5,
            marker='*', label='Início')
ax1.scatter(xs[-1], ys[-1], s=80, color='#ff4466', zorder=5,
            marker='X', label='Fim')

# Numeração a cada 10 pontos
for i in range(0, len(CONTOUR_POINTS), 10):
    ax1.annotate(str(i), (xs[i], ys[i]),
                 fontsize=7, color='#ffdd00',
                 xytext=(4, 4), textcoords='offset points')

ax1.legend(loc='upper right', fontsize=9,
           facecolor='#0a0a1a', labelcolor='white', edgecolor='#444')

# ---- Painel direito: estatísticas ----
ax2 = axes[1]
ax2.set_facecolor('#0a0a1a')
ax2.set_axis_off()
ax2.set_title('Informações do Mapeamento', color='white', fontsize=13, pad=10)

# Calcula comprimento total
total_len = 0.0
for i in range(len(CONTOUR_POINTS)):
    j = (i + 1) % len(CONTOUR_POINTS)
    dx = CONTOUR_POINTS[j][0] - CONTOUR_POINTS[i][0]
    dy = CONTOUR_POINTS[j][1] - CONTOUR_POINTS[i][1]
    total_len += (dx**2 + dy**2) ** 0.5

info_lines = [
    ('📐 Imagem original', '1280 × 720 px'),
    ('🐢 Espaço Turtlesim', '0–11 × 0–11 u'),
    ('📍 Total de pontos', f'{len(CONTOUR_POINTS)}'),
    ('📏 Comprimento total', f'{total_len:.2f} u'),
    ('⬅️  X mínimo', f'{xs.min():.3f}'),
    ('➡️  X máximo', f'{xs.max():.3f}'),
    ('⬇️  Y mínimo', f'{ys.min():.3f}'),
    ('⬆️  Y máximo', f'{ys.max():.3f}'),
    ('🚀 Velocidade linear', '3.0 u/s'),
    ('🔄 Velocidade angular', '4.0 rad/s'),
    ('🎯 Tolerância goal', '0.08 u'),
]

y_pos = 0.93
for label, value in info_lines:
    ax2.text(0.05, y_pos, label, transform=ax2.transAxes,
             color='#aaaacc', fontsize=10, va='top')
    ax2.text(0.65, y_pos, value, transform=ax2.transAxes,
             color='#00e5ff', fontsize=10, va='top', fontweight='bold')
    y_pos -= 0.08

# Nota de uso
ax2.text(0.05, 0.08, '▶  ros2 launch dog_drawer dog_draw.launch.py',
         transform=ax2.transAxes,
         color='#00ff88', fontsize=9, va='bottom',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#001a00',
                   edgecolor='#00ff88', alpha=0.8))

plt.tight_layout(pad=2.0)
plt.savefig('/home/claude/contour_preview.png', dpi=150,
            facecolor=fig.get_facecolor(), bbox_inches='tight')
print('Preview salvo em: contour_preview.png')
