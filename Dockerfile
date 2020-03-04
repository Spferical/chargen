from golang:1-buster

run apt-get update && apt-get install -y --no-install-recommends \
	pipenv\
	locales

run go get github.com/yudai/gotty

run adduser --system chargen

workdir /chargen

volume /chargen/data/

# Set the locale
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8

copy Pipfile Pipfile.lock docker_entrypoint.sh /chargen/

run pipenv install

copy ./chargen /chargen/chargen

cmd [ "./docker_entrypoint.sh" ]
