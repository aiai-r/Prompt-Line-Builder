// Prompt Line Builder UI adjustments

const promptLineBuilderReadyObservers = {};

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

function onPromptLineBuilderReady(idPart, callback) {
    const app = gradioApp ? gradioApp() : document;
    if (!app) return;

    const selector = `#${idPart}_prompt_line_builder`;
    const existing = app.querySelector(selector);
    if (existing) {
        callback(existing);
        return;
    }

    if (promptLineBuilderReadyObservers[idPart]) {
        return;
    }

    const target = app === document ? document.documentElement : app;

    const observer = new MutationObserver(() => {
        const builderEl = app.querySelector(selector);
        if (!builderEl) {
            return;
        }
        observer.disconnect();
        delete promptLineBuilderReadyObservers[idPart];
        callback(builderEl);
    });

    observer.observe(target, { childList: true, subtree: true });
    promptLineBuilderReadyObservers[idPart] = observer;
}

function clearPromptLineNumberDefaults(idPart) {
    onPromptLineBuilderReady(idPart, (builder) => {
        if (builder.dataset.plbNumbersCleared === '1') return;

        const clearInputs = () => {
            const inputs = builder.querySelectorAll('.plb-row2-number input[type="number"], .plb-row3-number input[type="number"]');
            if (!inputs.length) {
                return false;
            }

            inputs.forEach((inp) => {
                if (inp.value === '0' || inp.value === 0) {
                    inp.value = '';
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            builder.dataset.plbNumbersCleared = '1';
            return true;
        };

        if (clearInputs()) {
            return;
        }

        const observer = new MutationObserver(() => {
            if (clearInputs()) {
                observer.disconnect();
            }
        });
        observer.observe(builder, { childList: true, subtree: true });
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
