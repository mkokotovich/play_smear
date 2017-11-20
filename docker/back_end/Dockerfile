FROM centos:latest
RUN yum update -y
RUN yum install -y which man gcc python-devel
RUN curl https://bootstrap.pypa.io/get-pip.py | python
COPY back_end.sh /back_end.sh
CMD /back_end.sh
