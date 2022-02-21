FROM registry.access.redhat.com/ubi8/python-39

USER 0
COPY ./src /stt
WORKDIR /stt
ADD sslproxy.crt /etc/pki/ca-trust/source/anchors/local.pem
RUN update-ca-trust \
    && wget http://www.itzgeek.com/msttcore-fonts-2.0-3.noarch.rpm && rpm -Uvh msttcore-fonts-2.0-3.noarch.rpm \
    && wget https://www.imagemagick.org/download/ImageMagick.tar.gz \
    && mkdir ImageMagick \
    && tar xvzf ImageMagick.tar.gz -C ./ImageMagick --strip-components=1 \
    && pushd ImageMagick && ./configure && make && make install && popd \
    && python -m venv ~/.venv \
    && echo 'source ~/.venv/bin/activate' >> ~/.bashrc \
    && chmod +x /stt/process.py \
    && chmod +x /stt/init.py \
    && pip install -r requirements.txt \
    && python /stt/init.py \
    && chown -R 1001:1001 /stt/in \
    && chown -R 1001:1001 /stt/proc \
    && chown -R 1001:1001 /stt/out \
    && rm -f /etc/pki/ca-trust/source/anchors/local.pem && \
    update-ca-trust
USER 1001
