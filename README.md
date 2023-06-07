# Repository Info

This repository contains work done for my Data Structures & Algorithms Module Assignment 1 at SP
The scope of the assignment consisted of developing a full-stack website for an image classification service using trained CNNs.

The website is hosted on https://bevanpoh-cifar-webapp.onrender.com for access on Render

The website has features for uploading an image, editing the image and sending it to a CNN for a classification. Additionally, a history of previous model predictions is stored and can be viewed through a dashboard interface as well.

The repo consists of two servers, one hosting the CNN models and another providing both the frontend and the database functionalities.

- `dl_model_app_server` contains all the code for containerizing the CNN model server using Docker
- `dl_web_app_server` contains the python code for the image classification web service and containerized using Docker
    - `application` contains the Flask APIs for the website
    - `instance` contains the SQLite database for the website
    - `unit_test` contains pytests for each of the API responses
