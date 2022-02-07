FROM registry.access.redhat.com/ubi8/python-39

USER 0
RUN wget http://www.itzgeek.com/msttcore-fonts-2.0-3.noarch.rpm && rpm -Uvh msttcore-fonts-2.0-3.noarch.rpm
RUN wget https://www.imagemagick.org/download/ImageMagick.tar.gz \
    && mkdir ImageMagick \
    && tar xvzf ImageMagick.tar.gz -C ./ImageMagick --strip-components=1 \
    && pushd ImageMagick && ./configure && make && make install && popd
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz 
RUN groupadd --gid 1002 vscode \
    && useradd --uid 1002 --gid 1002 -m vscode
RUN mkdir ffmpeg \
    && tar xf ffmpeg-release-amd64-static.tar.xz -C ./ffmpeg --strip-components=1 \
    && pushd ffmpeg \
    && echo "export PATH=$PWD:\$PATH" >> /home/vscode/.bashrc \
    && popd
USER 1002
ENV HOME /home/vscode
RUN python -m venv /home/vscode/.venv \
    && echo 'source /home/vscode/.venv/bin/activate' >> /home/vscode/.bashrc \
    && echo 'alias python="/home/vscode/.venv/bin/python3.9' >> /home/vscode/.bashrc \
    && echo 'alias pip="/home/vscode/.venv/bin/pip3.9' >> /home/vscode/.bashrc