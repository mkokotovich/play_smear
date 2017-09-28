FROM centos:latest
RUN yum update
RUN yum install -y which man gcc python-devel
RUN curl https://bootstrap.pypa.io/get-pip.py | python
COPY back_end.sh /back_end.sh
CMD /back_end.sh
