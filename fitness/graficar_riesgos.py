"""E7: Genera la matriz de probabilidad e impacto de riesgos ATAM-lite."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

DESTINO = (
    Path(__file__).resolve().parents[1]
    / "docs/architecture/add/evidencias/matriz-riesgos.png"
)

RIESGOS = [
    ("R1", 4, 5, "R1: Brecha almacén simulado\nvs. PostgreSQL real (S1, S2)", (2.75, 4.55)),
    ("R2", 3, 5, "R2: VPS único como punto\núnico de falla (S3)", (1.55, 4.55)),
    ("R3", 3, 4, "R3: Huella SHA-256 sin canal\nexterno activo aún (S4)", (1.55, 3.65)),
    ("R4", 3, 3, "R4: Eventos en memoria y\ncorreo SMTP síncrono (S6, S8)", (3.15, 2.75)),
    ("R5", 2, 2, "R5: Cambios en API académica\no proveedor IA (S7)", (1.15, 1.45)),
]


def main():
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 5.2), layout="constrained")

    ax.add_patch(Rectangle((0.5, 0.5), 2.5, 2.5, facecolor="#e8f5e9", alpha=0.65, label="Zona aceptable"))
    ax.add_patch(Rectangle((3.0, 3.0), 2.5, 2.5, facecolor="#ffebee", alpha=0.75, label="Zona crítica (mitigar / justificar)"))

    for codigo, prob, imp, etiqueta, (tx, ty) in RIESGOS:
        color = "#c62828" if (prob >= 3 and imp >= 4) else ("#ef6c00" if prob * imp >= 9 else "#2e7d32")
        ax.scatter(prob, imp, s=180, color=color, zorder=4, edgecolors="black")
        ax.annotate(
            etiqueta,
            xy=(prob, imp),
            xytext=(tx, ty),
            fontsize=9.5,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.9),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.2),
            zorder=5,
        )

    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Probabilidad (1 = muy baja ... 5 = muy alta)", fontsize=11)
    ax.set_ylabel("Impacto en los escenarios de calidad (1 .. 5)", fontsize=11)
    ax.set_title("VotoEPIS · Matriz de Probabilidad e Impacto de Riesgos (ATAM-lite)", fontsize=13, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="lower right")

    fig.savefig(DESTINO, dpi=150)
    plt.close(fig)
    print(f"Matriz generada en: {DESTINO}")


if __name__ == "__main__":
    main()