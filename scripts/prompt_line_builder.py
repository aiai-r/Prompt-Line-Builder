import os
from typing import List

import gradio as gr

from modules import script_callbacks, sd_models, sd_samplers, shared


EXTENSION_ROOT = os.path.dirname(os.path.dirname(__file__))
LISTS_DIR = os.path.join(EXTENSION_ROOT, "prompt_lists")


def ensure_lists_dir() -> str:
    os.makedirs(LISTS_DIR, exist_ok=True)
    return LISTS_DIR


def get_sd_model_choices() -> List[str]:
    titles = [x.title for x in sd_models.checkpoints_list.values()]
    return ["未選択"] + titles


def get_sampler_choices() -> List[str]:
    return ["未選択"] + sd_samplers.visible_sampler_names()


def get_style_choices() -> List[str]:
    if shared.prompt_styles is None:
        return ["未選択"]

    choices: List[str] = ["未選択"]

    # styles.csv -> styles_integrated.csv の順を維持
    for name, style in shared.prompt_styles.styles.items():
        if not name or name == "None":
            continue
        if getattr(style, "path", None) == "do_not_save":
            continue
        choices.append(name)

    return choices


def _quote_value(value: str) -> str:
    """Wrap value in double quotes and escape inner quotes."""
    escaped = value.replace("\"", "\\\"")
    return f'"{escaped}"'


def _build_prompt_line(
    prompt: str,
    negative_prompt: str,
    sd_model: str,
    outpath_grids: str,
    prompt_for_display: str,
    styles: str,
    seed,
    subseed_strength,
    subseed,
    seed_resize_from_h,
    seed_resize_from_w,
    sampler_index,
    sampler_name: str,
    batch_size,
    n_iter,
    steps,
    cfg_scale,
    width,
    height,
    restore_faces: bool,
    tiling: bool,
    do_not_save_samples: bool,
    do_not_save_grid: bool,
) -> str:
    parts: List[str] = []

    def add_str(tag: str, value: str):
        if value is None:
            return
        value = str(value).strip()
        if not value or value == "未選択":
            return
        parts.append(f"--{tag} {_quote_value(value)}")

    def add_num(tag: str, value):
        if value is None:
            return
        # Gradio Number may supply 0 as an initial placeholder; treat 0/"" as未入力
        if isinstance(value, (int, float)) and value == 0:
            return
        v = str(value).strip()
        if not v or v == "0":
            return
        parts.append(f"--{tag} {v}")

    def add_bool(tag: str, value: bool):
        if value:
            parts.append(f"--{tag} true")

    add_str("prompt", prompt)
    add_str("negative_prompt", negative_prompt)
    add_str("sd_model", sd_model)
    add_str("outpath_grids", outpath_grids)
    add_str("prompt_for_display", prompt_for_display)
    add_str("styles", styles)

    add_num("seed", seed)
    add_num("subseed_strength", subseed_strength)
    add_num("subseed", subseed)
    add_num("seed_resize_from_h", seed_resize_from_h)
    add_num("seed_resize_from_w", seed_resize_from_w)
    add_num("sampler_index", sampler_index)
    add_str("sampler_name", sampler_name)
    add_num("batch_size", batch_size)
    add_num("n_iter", n_iter)
    add_num("steps", steps)
    add_num("cfg_scale", cfg_scale)
    add_num("width", width)
    add_num("height", height)

    add_bool("restore_faces", restore_faces)
    add_bool("tiling", tiling)
    add_bool("do_not_save_samples", do_not_save_samples)
    add_bool("do_not_save_grid", do_not_save_grid)

    return " ".join(parts)


def add_line(
    current_text: str,
    line_prompt: str,
    line_negative_prompt: str,
    sd_model: str,
    outpath_grids: str,
    prompt_for_display: str,
    styles: str,
    seed,
    subseed_strength,
    subseed,
    seed_resize_from_h,
    seed_resize_from_w,
    sampler_index,
    sampler_name: str,
    batch_size,
    n_iter,
    steps,
    cfg_scale,
    width,
    height,
    restore_faces: bool,
    tiling: bool,
    do_not_save_samples: bool,
    do_not_save_grid: bool,
) -> str:
    line = _build_prompt_line(
        line_prompt,
        line_negative_prompt,
        sd_model,
        outpath_grids,
        prompt_for_display,
        styles,
        seed,
        subseed_strength,
        subseed,
        seed_resize_from_h,
        seed_resize_from_w,
        sampler_index,
        sampler_name,
        batch_size,
        n_iter,
        steps,
        cfg_scale,
        width,
        height,
        restore_faces,
        tiling,
        do_not_save_samples,
        do_not_save_grid,
    )

    line = line.strip()
    if not line:
        return current_text or ""

    if current_text:
        return (current_text.rstrip("\n") + "\n" + line).rstrip("\n")

    return line


def clear_lines() -> str:
    return ""


def save_lines(text: str, file_name: str):
    ensure_lists_dir()

    file_name = (file_name or "").strip()
    if not file_name:
        file_name = "prompt_list.txt"

    if not file_name.lower().endswith(".txt"):
        file_name += ".txt"

    path = os.path.join(LISTS_DIR, file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text or "")

    message = f"保存しました: {path}"
    return message


_initialized_txt2img = False
_initialized_img2img = False


def _create_ui(is_img2img: bool):
    id_part = "img2img" if is_img2img else "txt2img"

    with gr.Accordion(
        "Prompt Line Builder",
        open=False,
        elem_id=f"{id_part}_prompt_line_builder",
        elem_classes=["prompt-line-builder-container"],
    ):
        with gr.Row():
            # left: prompts and line controls
            with gr.Column(scale=7):
                line_prompt = gr.Textbox(
                    label="Line prompt (prompt)",
                    lines=3,
                )
                line_negative_prompt = gr.Textbox(
                    label="Line negative prompt (negative_prompt)",
                    lines=3,
                )

                with gr.Row():
                    add_button = gr.Button("行を追加")
                    clear_button = gr.Button("全行をクリア")

            # right: parameter controls
            with gr.Column(scale=3):
                # row 1: sd_model, sampler_name, styles (dropdowns)
                with gr.Row():
                    sd_model = gr.Dropdown(
                        label="sd_model",
                        choices=get_sd_model_choices(),
                        value="未選択",
                        elem_classes=["plb-dropdown"],
                    )
                    sampler_name = gr.Dropdown(
                        label="sampler_name",
                        choices=get_sampler_choices(),
                        value="未選択",
                        elem_classes=["plb-dropdown"],
                    )
                    styles = gr.Dropdown(
                        label="styles",
                        choices=get_style_choices(),
                        value="未選択",
                        elem_classes=["plb-dropdown"],
                    )

                # row 2: seed, batch_size, n_iter, steps
                with gr.Row():
                    seed = gr.Number(
                        label="seed",
                        value=None,
                        elem_classes=["plb-row2-number"],
                    )
                    batch_size = gr.Number(
                        label="batch_size",
                        value=None,
                        elem_classes=["plb-row2-number"],
                    )
                    n_iter = gr.Number(
                        label="n_iter",
                        value=None,
                        elem_classes=["plb-row2-number"],
                    )
                    steps = gr.Number(
                        label="steps",
                        value=None,
                        elem_classes=["plb-row3-number"],
                    )

                # row 3: cfg_scale, width, height, restore_faces, tiling
                with gr.Row():
                    cfg_scale = gr.Number(
                        label="cfg_scale",
                        value=None,
                        elem_classes=["plb-row3-number"],
                    )
                    width = gr.Number(
                        label="width",
                        value=None,
                        elem_classes=["plb-row3-number"],
                    )
                    height = gr.Number(
                        label="height",
                        value=None,
                        elem_classes=["plb-row3-number"],
                    )
                    restore_faces = gr.Checkbox(label="restore_faces", value=False)
                    tiling = gr.Checkbox(label="tiling", value=False)

                # row 4: Advanced
                with gr.Accordion("Advanced / 詳細設定", open=False):
                    sampler_index = gr.Number(
                        label="sampler_index",
                        value=None,
                        elem_classes=["plb-row3-number"],
                    )

                    with gr.Row():
                        subseed = gr.Number(
                            label="subseed",
                            value=None,
                            elem_classes=["plb-row3-number"],
                        )
                        subseed_strength = gr.Number(
                            label="subseed_strength",
                            value=None,
                            elem_classes=["plb-row3-number"],
                        )

                    with gr.Row():
                        seed_resize_from_w = gr.Number(
                            label="seed_resize_from_w",
                            value=None,
                            elem_classes=["plb-row3-number"],
                        )
                        seed_resize_from_h = gr.Number(
                            label="seed_resize_from_h",
                            value=None,
                            elem_classes=["plb-row3-number"],
                        )

                    prompt_for_display = gr.Textbox(label="prompt_for_display")
                    outpath_grids = gr.Textbox(label="outpath_grids")

                    with gr.Row():
                        do_not_save_samples = gr.Checkbox(
                            label="do_not_save_samples", value=False
                        )
                        do_not_save_grid = gr.Checkbox(
                            label="do_not_save_grid", value=False
                        )

        # lines + file/save area: 7:3 layout
        with gr.Row():
            with gr.Column(scale=7):
                lines_text = gr.Textbox(
                    label="Current lines (Prompts from file or textbox)",
                    lines=8,
                    elem_id=f"{id_part}_prompt_line_builder_lines",
                )

            with gr.Column(scale=3):
                file_name = gr.Textbox(
                    label="File name (.txt)",
                    value="prompt_list.txt",
                )
                save_btn = gr.Button("txt に保存")

        status = gr.HTML(value="")

        add_button.click(
            fn=add_line,
            inputs=[
                lines_text,
                line_prompt,
                line_negative_prompt,
                sd_model,
                outpath_grids,
                prompt_for_display,
                styles,
                seed,
                subseed_strength,
                subseed,
                seed_resize_from_h,
                seed_resize_from_w,
                sampler_index,
                sampler_name,
                batch_size,
                n_iter,
                steps,
                cfg_scale,
                width,
                height,
                restore_faces,
                tiling,
                do_not_save_samples,
                do_not_save_grid,
            ],
            outputs=[lines_text],
        )

        clear_button.click(fn=clear_lines, inputs=[], outputs=[lines_text])

        save_btn.click(
            fn=save_lines,
            inputs=[lines_text, file_name],
            outputs=[status],
        )


def on_after_component(component, **_kwargs):
    global _initialized_txt2img, _initialized_img2img

    elem_id = getattr(component, "elem_id", None)

    if elem_id == "txt2img_neg_prompt" and not _initialized_txt2img:
        _initialized_txt2img = True
        _create_ui(is_img2img=False)
    elif elem_id == "img2img_neg_prompt" and not _initialized_img2img:
        _initialized_img2img = True
        _create_ui(is_img2img=True)


script_callbacks.on_after_component(on_after_component, name="prompt_line_builder_after_component")
