import json
import shutil
from pathlib import Path

from PIL import Image


def mkdir(path: Path, **kwargs) -> Path:
    kwargs = {"parents": True, "exist_ok": True} | kwargs
    if path.suffix:
        path.parent.mkdir(**kwargs)
    else:
        path.mkdir(**kwargs)
    return path


def main():
    CURRENT_DIR = Path.cwd()
    RAW_RESOURCEPACK_DIR = CURRENT_DIR / "data" / "raw_resourcepack"
    RESULT_DIR = mkdir(CURRENT_DIR / "data" / "results")
    COLOR_MAP_PATH = CURRENT_DIR / "data" / "color_map.json"
    TRANSPARENT_COLOR = (0, 0, 0, 0)

    def IGNORE_FILES(_, names):
        return filter(lambda x: "." in x, names)

    with open(COLOR_MAP_PATH, "r") as file:
        COLOR_MAP: dict[str, int] = json.load(file)

    shutil.copytree(
        RAW_RESOURCEPACK_DIR, RESULT_DIR, ignore=IGNORE_FILES, dirs_exist_ok=True
    )

    for raw_namespace_dir in RAW_RESOURCEPACK_DIR.iterdir():
        mod_namespace = raw_namespace_dir.name
        result_dir = Path(str(raw_namespace_dir).replace("raw_resourcepack", "results"))

        for raw_texture_path in raw_namespace_dir.rglob("*.png"):
            parts = raw_texture_path.parts
            raw_texture_subpath = Path("/".join(parts[parts.index("blocks") + 1 :]))
            color_key = ":".join(
                (mod_namespace, raw_texture_subpath.with_suffix("").as_posix())
            )
            color = COLOR_MAP.get(color_key, -1)

            optifine_emissive_path = mkdir(
                result_dir / "optifine" / "emissive.properties"
            )
            with open(optifine_emissive_path, "w") as file:
                file.write("suffix.emissive=_e\n")

            image = Image.open(raw_texture_path).convert("RGBA")
            width, height = image.size
            image_count = height // width
            if color == -1:
                color = image.getpixel((0, 0))
                COLOR_MAP[color_key] = int("".join(hex(i)[2:].zfill(2) for i in color[:-1]), 16)
            else:
                color = (
                    (color & 0xFF0000) >> 16,
                    (color & 0x00FF00) >> 8,
                    color & 0x0000FF,
                    255,
                )
            texture_color = [
                [color] * width,
                *([[color, *[TRANSPARENT_COLOR] * (width - 2), color]] * (width - 2)),
                [color] * width,
            ] * image_count

            new_texture_path = (
                result_dir / "textures/blocks" / raw_texture_subpath.parent
            )
            new_texture = Image.new("RGBA", (width, height))
            new_texture.putdata([color for row in texture_color for color in row])
            new_texture.save(new_texture_path / f"{raw_texture_path.stem}_e.png")

            if height > width:
                mcmeta_name = f"{raw_texture_path.name}.mcmeta"
                shutil.copyfile(
                    raw_texture_path.parent / mcmeta_name,
                    new_texture_path / mcmeta_name,
                )

    with open(COLOR_MAP_PATH, "w") as file:
        json.dump(COLOR_MAP, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
