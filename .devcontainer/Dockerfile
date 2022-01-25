FROM registry.access.redhat.com/ubi8/python-39

USER 0
RUN wget http://www.itzgeek.com/msttcore-fonts-2.0-3.noarch.rpm && rpm -Uvh msttcore-fonts-2.0-3.noarch.rpm
RUN wget https://www.imagemagick.org/download/ImageMagick-7.1.0-20.tar.gz \
    && tar xvzf ImageMagick-7.1.0-20.tar.gz \
    && cd ImageMagick-7.1.0-20 && ./configure && make && make install
RUN groupadd --gid 1002 vscode \
    && useradd --uid 1002 --gid 1002 -m vscode
USER 1002
ENV HOME /home/vscode
RUN python -m venv /home/vscode/.venv \
    && echo 'source /home/vscode/.venv/bin/activate' >> /home/vscode/.bashrc \
    && echo 'alias python="/home/vscode/.venv/bin/python3.9' >> /home/vscode/.bashrc \
    && echo 'alias pip="/home/vscode/.venv/bin/pip3.9' >> /home/vscode/.bashrc