function matDetails(src) {
    let image;
    if (typeof src === "string") {
        image = cv.imread(src);
    } else {
        image = src;
    }

    console.log(
        "image width: " +
        image.cols +
        "\n" +
        "image height: " +
        image.rows +
        "\n" +
        "image size: " +
        image.size().width +
        "*" +
        image.size().height +
        "\n" +
        "image depth: " +
        image.depth() +
        "\n" +
        "image channels: " +
        image.channels() +
        "\n" +
        "image type: " +
        image.type() +
        "\n"
    );

    console.log(image.data);
    console.log(image.data16S);
}

function resizeImage(
    srcElement,
    dst,
    resizeWidth = 32,
    resizeHeight = 32
) {
    let src = cv.imread(srcElement);

    if (src.rows === resizeHeight && src.cols === resizeWidth) {
        src.copyTo(dst);
    }
    else {
        let dsize = new cv.Size(resizeWidth, resizeHeight);
        cv.resize(src, dst, dsize, 0, 0, cv.INTER_AREA);
    }

    src.delete();
}

function calculateLaplacian(srcMat, dstMat, scale = 1.0) {
    cv.Laplacian(
        srcMat,
        dstMat,
        cv.CV_16S,
        (ksize = 1),
        (scale = scale),
        (delta = 0)
    );
}

function displaySharpen(
    srcMat,
    dstElement,
    laplacianMat,
    ratio = 0.5
) {
    let src = srcMat.clone();
    let dst = new cv.Mat(32, 32, cv.CV_8U);
    src.convertTo(src, 27);

    try {
        cv.addWeighted(
            src,
            1,
            laplacianMat,
            -ratio,
            (gamma = 0.0),
            (dst = dst),
            dtype = -1 / laplacianMat.depth()
        );
        cv.imshow(dstElement, dst);
    }
    catch (error) {
        console.log("Laplacian has not been calculated");
        return;
    }
    src.delete();
    dst.delete();
}

function submitPrediction() {
    $("#result").text(" Predicting...");
    let canvas = document.getElementById("sharpenCanvas");
    let contrastSlider = document.getElementById("contrastSlider");
    let sharpenSlider = document.getElementById("sharpenSlider");
    let modelSelect = document.getElementById("modelSelect");

    let fileInput = document.getElementById("fileInput");
    if (fileInput.files[0]) {
        filename = fileInput.files[0].name;
    } else filename = "";

    $.post(
        "https://bevanpoh-cifar-webapp.onrender.com/predict",
        {
            image: canvas.toDataURL("image/png"),
            filename: filename,
            model: modelSelect.value,
            contrast: contrastSlider.value,
            edgeSharpen: sharpenSlider.value,
        },
    ).done(function (status) { $("#result").text("Prediction: " + status.message[0].toUpperCase() + status.message.slice(1)); })
        .fail(function (xhr, status, error) {
            $("#result").text(xhr.responseJSON.message);
        });
}
