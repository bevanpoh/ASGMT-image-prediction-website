FROM tensorflow/serving

COPY / /
# RUN apt-get -y update
# && apt-get install -y git && git reset --hard


ENV MODEL_CONFIG_PATH=/models/models.config

EXPOSE 8500
EXPOSE 8501


RUN echo '#!/bin/bash \n\n\
tensorflow_model_server \
--rest_api_port=8501 \
--model_config_file=${MODEL_CONFIG_PATH} \
--model_config_file_poll_wait_seconds=60 \
"$@"' > /usr/bin/tf_serving_entrypoint.sh \
&& chmod +x /usr/bin/tf_serving_entrypoint.sh
