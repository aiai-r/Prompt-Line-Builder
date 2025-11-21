// Prompt Line Builder UI adjustments

function movePromptLineBuilder(idPart) {
    const app = gradioApp ? gradioApp() : document;
    if (!app) return;

    const builder = app.querySelector(`#${idPart}_prompt_line_builder`);
    const toprow = app.querySelector(`#${idPart}_toprow`);
    if (!builder || !toprow) return;

    // Already moved?
    if (builder.dataset.plbMoved === '1') return;

    const parent = toprow.parentElement;
    if (!parent) return;

    // Insert builder right after the whole toprow (under negative + generate)
    parent.insertBefore(builder, toprow.nextSibling);
    builder.dataset.plbMoved = '1';
}

function setupPromptLineDrop(idPart) {
    const app = gradioApp ? gradioApp() : document;
    if (!app) return;

    const container = app.querySelector(`#${idPart}_prompt_line_builder_lines`);
    if (!container) return;

    const textarea = container.querySelector('textarea');
    if (!textarea) return;

    function prevent(e) {
        e.preventDefault();
    }

    function handleDrop(e) {
        e.preventDefault();
        const files = e.dataTransfer && e.dataTransfer.files;
        if (!files || !files.length) return;

        const file = files[0];
        const reader = new FileReader();
        reader.onload = (ev) => {
            const text = ev.target && ev.target.result ? String(ev.target.result) : '';
            textarea.value = text;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            textarea.dispatchEvent(new Event('change', { bubbles: true }));
        };
        reader.readAsText(file, 'utf-8');
    }

    ['dragover', 'dragenter'].forEach((evt) => {
        textarea.addEventListener(evt, prevent);
    });
    textarea.addEventListener('drop', handleDrop);
}

function clearPromptLineNumberDefaults(idPart) {
    const app = gradioApp ? gradioApp() : document;
    if (!app) return;

    const builder = app.querySelector(`#${idPart}_prompt_line_builder`);
    if (!builder) return;

    const inputs = builder.querySelectorAll('.plb-row2-number input[type="number"], .plb-row3-number input[type="number"]');
    inputs.forEach((inp) => {
        if (inp.value === '0' || inp.value === 0) {
            inp.value = '';
        }
    });
}

onUiLoaded(function() {
    movePromptLineBuilder('txt2img');
    movePromptLineBuilder('img2img');
    setupPromptLineDrop('txt2img');
    setupPromptLineDrop('img2img');
    clearPromptLineNumberDefaults('txt2img');
    clearPromptLineNumberDefaults('img2img');
});
