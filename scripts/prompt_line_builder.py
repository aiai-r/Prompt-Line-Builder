import os
from typing import List, Optional

import gradio as gr

from modules import script_callbacks


EXTENSION_ROOT = os.path.dirname(os.path.dirname(__file__))
LISTS_DIR = os.path.join(EXTENSION_ROOT, "prompt_lists")


def ensure_lists_dir() -> str:
    os.makedirs(LISTS_DIR, exist_ok=True)
    return LISTS_DIR


def _build_prompt_line(
    prompt: str,
    negative_prompt: str,
    sd_model: str,
    outpath_grids: str,
    prompt_for_display: str,
    styles: str,
    seed: Optional[float],
    subseed_strength: Optional[float],
    subseed: Optional[float],
    seed_resize_from_h: Optional[float],
    seed_resize_from_w: Optional[float],
    sampler_index: Optional[float],
    sampler_name: str,
    batch_size: Optional[float],
    n_iter: Optional[float],
    steps: Optional[float],
    cfg_scale: Optional[float],
    width: Optional[float],
    height: Optional[float],
    restore_faces: bool,
    tiling: bool,
    do_not_save_samples: bool,
    do_not_save_grid: bool,
) -> str:
    parts: List[str] = []

    def add_str(tag: str, value: str):
        if value is None:
            return
        value = value.strip()
        if not value:
            return
        parts.append(f"--{tag} {value}")

    def add_num(tag: str, value: Optional[float]):
        if value is None:
            return
        v = float(value)
        parts.append(f"--{tag} {int(v) if v.is_integer() else v}")

    def add_bool(tag: str, value: bool):
        parts.append(f"--{tag} {'true' if value else 'false'}")

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

    if restore_faces:
        add_bool("restore_faces", True)
    if tiling:
        add_bool("tiling", True)
    if do_not_save_samples:
        add_bool("do_not_save_samples", True)
    if do_not_save_grid:
        add_bool("do_not_save_grid", True)

    return " ".join(parts)


def add_line(
    current_text: str,
    line_prompt: str,
    line_negative_prompt: str,
    sd_model: str,
    outpath_grids: str,
    prompt_for_display: str,
    styles: str,
    seed: Optional[float],
    subseed_strength: Optional[float],
    subseed: Optional[float],
    seed_resize_from_h: Optional[float],
    seed_resize_from_w: Optional[float],
    sampler_index: Optional[float],
    sampler_name: str,
    batch_size: Optional[float],
    n_iter: Optional[float],
    steps: Optional[float],
    cfg_scale: Optional[float],
    width: Optional[float],
    height: Optional[float],
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


def list_saved_files() -> List[str]:
    ensure_lists_dir()
    files = []
    for name in os.listdir(LISTS_DIR):
        if name.lower().endswith(".txt"):
            files.append(name)
    files.sort()
    return files


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
    return message, gr.update(choices=list_saved_files(), value=file_name)


def load_lines(file_name: str):
    ensure_lists_dir()
    file_name = (file_name or "").strip()
    if not file_name:
        return "", gr.update()

    path = os.path.join(LISTS_DIR, file_name)
    if not os.path.isfile(path):
        return "", gr.update()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    return text, gr.update(value=file_name, choices=list_saved_files())


def load_from_upload(file):
    if file is None:
        return "", gr.update()

    try:
        content = file.decode("utf-8", errors="ignore")
    except Exception:
        content = ""

    return content, gr.update()


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
        gr.Markdown("### Line 設定")

        line_prompt = gr.Textbox(
            label="ライン用プロンプト (prompt)",
            lines=2,
            placeholder="この行で使うポジティブプロンプト",
        )
        line_negative_prompt = gr.Textbox(
            label="ライン用ネガティブプロンプト (negative_prompt)",
            lines=2,
            placeholder="この行で使うネガティブプロンプト (必要な場合)",
        )

        with gr.Row():
            sd_model = gr.Textbox(
                label="sd_model (チェックポイント名)",
                placeholder="例: AnythingV3, chilloutmix など。空欄で現在のモデルを使用",
            )

        with gr.Row():
            sampler_name = gr.Textbox(
                label="sampler_name",
                placeholder="例: Euler a, DPM++ 2M Karras など。空欄で現在の設定を使用",
            )

        with gr.Row():
            seed = gr.Number(label="seed", value=None, precision=0)
            batch_size = gr.Number(label="batch_size", value=None, precision=0)
            n_iter = gr.Number(label="n_iter", value=None, precision=0)

        with gr.Row():
            steps = gr.Number(label="steps", value=None, precision=0)
            cfg_scale = gr.Number(label="cfg_scale", value=None)

        with gr.Row():
            width = gr.Number(label="width", value=None, precision=0)
            height = gr.Number(label="height", value=None, precision=0)

        with gr.Row():
            restore_faces = gr.Checkbox(label="restore_faces", value=False)
            tiling = gr.Checkbox(label="tiling", value=False)

        styles = gr.Textbox(
            label="styles",
            placeholder="Style 名 (カンマ区切り / 任意)",
        )

        with gr.Accordion("Advanced / 詳細設定", open=False):
            with gr.Row():
                sampler_index = gr.Number(
                    label="sampler_index",
                    value=None,
                    precision=0,
                )

            with gr.Row():
                subseed = gr.Number(label="subseed", value=None, precision=0)
                subseed_strength = gr.Number(
                    label="subseed_strength", value=None
                )

            with gr.Row():
                seed_resize_from_w = gr.Number(
                    label="seed_resize_from_w", value=None, precision=0
                )
                seed_resize_from_h = gr.Number(
                    label="seed_resize_from_h", value=None, precision=0
                )

            prompt_for_display = gr.Textbox(
                label="prompt_for_display",
                placeholder="表示用に整形したプロンプト (任意)",
            )

            outpath_grids = gr.Textbox(
                label="outpath_grids",
                placeholder="グリッド画像の保存先フォルダ (任意)",
            )

            with gr.Row():
                do_not_save_samples = gr.Checkbox(
                    label="do_not_save_samples", value=False
                )
                do_not_save_grid = gr.Checkbox(
                    label="do_not_save_grid", value=False
                )

        gr.Markdown("### 出力・ファイル設定")

        lines_text = gr.Textbox(
            label="現在のライン一覧 (Prompts from file or textbox 用)",
            lines=8,
            placeholder="ここに 1 行ずつコマンド形式で保存されます",
        )

        with gr.Row():
            add_button = gr.Button("行を追加")
            clear_button = gr.Button("全行をクリア")

        with gr.Row():
            file_name = gr.Textbox(
                label="ファイル名 (.txt)",
                placeholder="prompt_list.txt",
                value="prompt_list.txt",
            )
            saved_files = gr.Dropdown(
                label="保存済みファイル",
                choices=list_saved_files(),
                value=None,
            )

        upload_file = gr.File(
            label="外部の txt を読み込む",
            type="binary",
        )

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

        save_btn = gr.Button("txt に保存")
        save_btn.click(
            fn=save_lines,
            inputs=[lines_text, file_name],
            outputs=[status, saved_files],
        )

        load_btn = gr.Button("選択したファイルを読み込み")
        load_btn.click(
            fn=load_lines,
            inputs=[saved_files],
            outputs=[lines_text, saved_files],
        )

        upload_file.upload(
            fn=load_from_upload,
            inputs=[upload_file],
            outputs=[lines_text, file_name],
            show_progress=False,
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
