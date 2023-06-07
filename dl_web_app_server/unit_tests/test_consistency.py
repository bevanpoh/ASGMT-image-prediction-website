import pytest

from flask import json
import keras
import requests
import numpy as np


def make_prediction(instances, target_url):
    data = json.dumps(
        {"signature_name": "serving_default", "instances": instances.tolist()}
    )
    headers = {"content-type": "application/json"}
    json_response = requests.post(target_url, data=data, headers=headers)
    predictions = json.loads(json_response.text)["predictions"]
    return predictions


base_url = "https://bevanpoh-cifar-model.onrender.com"


@pytest.fixture(scope="module")
def test_vgg_model():
    return base_url + "/v1/models/vgg_net/versions/1:predict"


@pytest.fixture(scope="module")
def test_all_conv_model():
    return base_url + "/v1/models/all_conv_net/versions/1:predict"


image1 = "test_images/elephant.jpg"
image2 = "test_images/possum.jpg"
image3 = "test_images/pexels-adriaan-greyling-769433.jpg"


@pytest.mark.parametrize(
    "file,target_model",
    [
        (image1, "test_vgg_model"),
        (image2, "test_vgg_model"),
        (image3, "test_vgg_model"),
        (image1, "test_all_conv_model"),
        (image2, "test_all_conv_model"),
        (image3, "test_all_conv_model"),
    ],
)
def test_model_consistency(file, target_model, request, capsys):
    with capsys.disabled():

        target_url = request.getfixturevalue(target_model)
        image = keras.utils.img_to_array(
            keras.utils.load_img(file, target_size=(32, 32, 3))
        )
        image = image.reshape(1, 32, 32, 3)

        pred1 = make_prediction(image, target_url)
        pred2 = make_prediction(image, target_url)
        pred3 = make_prediction(image, target_url)

        assert np.array_equal(pred1, pred2)
        assert np.array_equal(pred1, pred3)
        assert np.array_equal(pred2, pred3)
