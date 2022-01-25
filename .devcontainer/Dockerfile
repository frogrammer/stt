FROM registry.access.redhat.com/ubi8/python-39

USER 0
# install imagemagick
RUN dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y \
    && dnf install GraphicsMagick -y
# add vscode user
RUN groupadd --gid 1002 vscode \
    && useradd --uid 1002 --gid 1002 -m vscode

USER 1002
ENV HOME /home/vscode
RUN python -m venv /home/vscode/.venv \
    && echo 'source /home/vscode/.venv/bin/activate' >> /home/vscode/.bashrc