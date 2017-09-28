FROM centos:latest
RUN yum update
RUN yum install -y which man
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.13.1/install.sh | bash
RUN source /root/.bash_profile && nvm install v6.11.3
COPY front_end.sh /front_end.sh
CMD /front_end.sh
