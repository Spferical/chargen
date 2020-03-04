from golang:1-buster

run apt-get update && apt-get install -y --no-install-recommends \
	pipenv \
	locales

run adduser --system --shell /bin/bash chargen

run go get github.com/yudai/gotty

run ln -s /go/bin/gotty /usr/local/bin/gotty

workdir /chargen

volume /chargen/data/

# Set the locale
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN locale-gen en_US.UTF-8

RUN echo 'export LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8' > /etc/profile.d/locale.sh

copy --chown=chargen:root Pipfile Pipfile.lock /chargen/

run su - chargen -c 'cd /chargen && pipenv install'

copy .gotty /home/chargen
copy ./chargen /chargen/chargen
copy docker_entrypoint.sh /chargen/

cmd [ "./docker_entrypoint.sh" ]
