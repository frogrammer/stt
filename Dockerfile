FROM registry.access.redhat.com/ubi8/python-39

USER 0
COPY --chown=1001:1001 . /stt
WORKDIR /stt
RUN wget http://www.itzgeek.com/msttcore-fonts-2.0-3.noarch.rpm && rpm -Uvh msttcore-fonts-2.0-3.noarch.rpm \
    && wget https://www.imagemagick.org/download/ImageMagick.tar.gz \
    && mkdir ImageMagick \
    && tar xvzf ImageMagick.tar.gz -C ./ImageMagick --strip-components=1 \
    && pushd ImageMagick && ./configure && make && make install && popd \
    && python -m venv ~/.venv \
    && echo 'source ~/.venv/bin/activate' >> ~/.bashrc \
    && chmod +x /stt/process.py \
    && chmod +x /stt/init.py \
    && pip install -r requirements.txt \
    && python /stt/init.py
USER 1001