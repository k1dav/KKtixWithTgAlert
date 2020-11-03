FROM python:3.9-buster

ENV PYTHONUNBUFFERED=1

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Or your actual UID, GID on Linux if not the default 1000
ARG USERNAME=vscode
ARG USER_UID=YOUR_UID_HERE
ARG USER_GID=YOUR_GID_HERE

# System
RUN apt-get update \
    && apt-get install --yes --no-install-recommends locales git sudo openssh-client iproute2 \
    && rm -rf /var/lib/apt/lists/* /var/cache/debconf \
    && apt-get clean \
    && mkdir -p /etc/sudoers.d/ \
    && getent group ${USER_GID} | if [ $(wc -l) -eq 0 ]; then groupadd --gid ${USER_GID} ${USERNAME}; fi \
    && useradd -s /bin/bash --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
    && echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME}\
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# Files
COPY images/my-api/requirements.txt /tmp/pip-tmp/

# Update Python environment based on requirements.txt
RUN pip --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# set default language environment
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    update-locale LANG="en_US.UTF-8"
ENV LC_ALL="en_US.UTF-8"
ENV LANGUAGE="en_US.UTF-8"

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=

CMD ["/bin/bash"]