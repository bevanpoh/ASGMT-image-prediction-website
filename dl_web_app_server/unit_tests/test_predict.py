import pytest

from flask import json, jsonify
import base64
from datetime import datetime
import re
import requests
from pathlib import Path

# - xfail on predict errors
#     - bad image input
#     - bad file input
#     - bad num values
#     - bad model


@pytest.fixture(scope="module")
def test_image():
    with open("test_images/elephant.png", "rb") as f:
        im_bytes = f.read()
    base64_str = str(base64.b64encode(im_bytes))
    return base64_str


@pytest.mark.xfail
@pytest.mark.parametrize(
    "image,model,filename,sharpen,contrast,expected_code",
    [
        ("None", "vgg_net", "test.jpg", 0, 100, 200),
        ("test_image", "None", "test.jpg", 0, 100, 200),
        ("test_image", "vgg_net", "None", 0, 100, 200),
        ("test_image", "vgg_net", "None.pdf", 0, 100, 200),
        ("test_image", "vgg_net", "test.jpg", 393939, 100, 200),
        ("test_image", "vgg_net", "test.jpg", 0, 393939, 200),
    ],
)
def test_predict_invalid(
    image, model, filename, sharpen, contrast, expected_code, client, capsys, request
):
    with capsys.disabled():
        try:
            image = request.getfixturevalue(image)
        except:
            image = ""

        data = {
            "image": "base64," + image,
            "model": model,
            "filename": filename,
            "edgeSharpen": sharpen,
            "contrast": contrast,
        }
        response = client.post(
            "/predict",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == expected_code
