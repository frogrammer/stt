FROM registry.access.redhat.com/ubi8/python-39

USER 0
RUN wget http://www.itzgeek.com/msttcore-fonts-2.0-3.noarch.rpm \
    && rpm -Uvh msttcore-fonts-2.0-3.noarch.rpm \
    && wget https://www.imagemagick.org/download/ImageMagick.tar.gz \
    && mkdir ImageMagick \
    && tar xvzf ImageMagick.tar.gz -C ./ImageMagick --strip-components=1 \
    && pushd ImageMagick && ./configure && make && make install && popd
RUN groupadd --gid 1002 vscode \
    && useradd --uid 1002 --gid 1002 -m vscode
USER 1002
ENV HOME /home/vscode
RUN python -m venv /home/vscode/.venv \
    && echo 'source /home/vscode/.venv/bin/activate' >> /home/vscode/.bashrc