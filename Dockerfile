FROM nlknguyen/alpine-mpich:onbuild

# # ------------------------------------------------------------
# # Build MPI project
# # ------------------------------------------------------------

COPY project/ .

# # ------------------------------------------------------------
# Install Linux deps
# # ------------------------------------------------------------

RUN sudo apk update
RUN sudo apk add ca-certificates
RUN sudo update-ca-certificates
RUN sudo apk add openssl
RUN sudo apk add openssl-dev
RUN sudo apk add zlib-dev
RUN sudo apk add curl
RUN sudo apk add libffi-dev
RUN sudo apk add postgresql-dev
RUN sudo apk add protobuf-dev
RUN sudo apk add bzip2-dev
RUN sudo apk add jpeg-dev

ARG TCB=tokyocabinet-1.4.48
RUN wget http://fallabs.com/tokyocabinet/$TCB.tar.gz && tar -xzf $TCB.tar.gz && cd $TCB && \
 sudo ./configure --prefix=/usr --enable-off64 --enable-fastest && sudo make && sudo make install

RUN sudo apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/testing \
  geos-dev
ENV LIBRARY_PATH=/lib:/usr/lib

# # ------------------------------------------------------------
# Install Python2 deps
# # ------------------------------------------------------------

RUN sudo wget http://www.python.org/ftp/python/2.7.16/Python-2.7.16.tgz
RUN sudo tar xzf Python-2.7.16.tgz
RUN cd Python-2.7.16 && sudo ./configure --enable-optimizations --with-ssl && sudo make install

RUN sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN sudo python get-pip.py

# Install pygraph
RUN cd python-graph/core/ && sudo python2 setup.py install

# Install python requirments
RUN sudo pip2.7 install -r requirements.txt

# # ------------------------------------------------------------
