function updateSlider(target, value) {
    $('#' + target).val(value).trigger("input");
}

function updateText(target, value) {
    text = document.getElementById(target);
    text.value = value;
}
