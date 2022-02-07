FROM registry.access.redhat.com/ubi8/python-39

USER 0
RUN wget http://www.itzgeek.com/msttcore-fonts-2.0-3.noarch.rpm && rpm -Uvh msttcore-fonts-2.0-3.noarch.rpm
RUN wget https://www.imagemagick.org/download/ImageMagick.tar.gz \
    && mkdir ImageMagick \
    && tar xvzf ImageMagick.tar.gz -C ./ImageMagick --strip-components=1 \
    && pushd ImageMagick && ./configure && make && make install && popd
USER 1001
RUN python -m venv ~/.venv \
    && echo 'source ~/.venv/bin/activate' >> ~/.bashrc \
    && echo 'alias python="~/.venv/bin/python3.9' >> ~/.bashrc \
    && echo 'alias pip="~/.venv/bin/pip3.9' >> ~/.bashrc
COPY . /stt

