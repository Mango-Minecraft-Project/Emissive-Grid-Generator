# Emissive Grid Generator

Given the RGB value of the grid and the original texture, generate an Optifine-based emissive grid.

## How to use

Note: [`python 3.11`][py311] and [`pdm`][pdm] must be installed first.
If this is your first time using it, run the `pdm sync` command first.

1. Run `run.bat`
2. Modify `data/color_map.json`, the key is the path of the map, and the value is the RGB of the grid (no need to modify it if the texture entered is already with a grid)
3. Run `run.bat` again

[py311]: https://www.python.org/downloads/release/python-3114/
[pdm]: https://pdm.fming.dev/