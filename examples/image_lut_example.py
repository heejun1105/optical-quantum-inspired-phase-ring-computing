"""Repository-added illustrative gamma lookup; not a PLP ISP reproduction.

The attached PDF discusses image LUTs in its Paper IX appendix (Appendix D),
which is background only. The encoder and gamma=2.2 are demo choices, not
Paper VIII implementation parameters or claims about image quality.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from phase_ring import phase_add


def pixel_to_phase(pixel: int) -> int:
    if isinstance(pixel, bool) or not isinstance(pixel, int):
        raise TypeError("pixel must be an integer")
    if not 0 <= pixel <= 255:
        raise ValueError("pixel must be in [0, 255]")
    return pixel * 1023 // 255


def gamma_lut(gamma: float = 2.2) -> tuple[int, ...]:
    if gamma <= 0:
        raise ValueError("gamma must be positive")
    return tuple(round(255 * (address / 1023) ** (1 / gamma)) for address in range(1024))


def process_rgb(rgb: tuple[int, int, int], phase_offset: int = 0) -> tuple[int, int, int]:
    lut = gamma_lut()
    return tuple(lut[phase_add(pixel_to_phase(pixel), phase_offset, 1024)] for pixel in rgb)


if __name__ == "__main__":
    for rgb in ((0, 0, 0), (32, 64, 128), (128, 192, 255), (255, 255, 255)):
        phases = tuple(pixel_to_phase(pixel) for pixel in rgb)
        output = process_rgb(rgb)
        print(f"RGB {rgb} -> illustrative phase addresses {phases} -> gamma LUT RGB {output}")
    print("Demo only: no PLP denoising, image-quality benchmark or general color conversion.")
