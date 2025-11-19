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

onUiLoaded(function() {
    movePromptLineBuilder('txt2img');
    movePromptLineBuilder('img2img');
});
