# # ------------------------------------------------------------
# # Build MPI project
# # ------------------------------------------------------------

# Base MPI docker image
FROM nlknguyen/alpine-mpich:onbuild

# # ------------------------------------------------------------
# Install Linux deps
# # ------------------------------------------------------------

RUN sudo apk update
RUN sudo apk add bzip2-dev \
                 ca-certificates \
                 curl \
                 libffi-dev \
                 jpeg-dev \
                 openssl \
                 openssl-dev \
                 postgresql-dev \
                 protobuf-dev \
                 zlib-dev
RUN sudo update-ca-certificates

# Tokyo cabinent is needed for its TCutil.h
ARG TCB=tokyocabinet-1.4.48
RUN wget http://fallabs.com/tokyocabinet/$TCB.tar.gz && tar -xzf $TCB.tar.gz && cd $TCB && \
 sudo ./configure --prefix=/usr --enable-off64 --enable-fastest && sudo make && sudo make install

# Need for OSM
RUN sudo apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/testing \
  geos-dev
ENV LIBRARY_PATH=/lib:/usr/lib

# # ------------------------------------------------------------
# Install Python2 deps
# # ------------------------------------------------------------

# Install python2
RUN wget http://www.python.org/ftp/python/2.7.16/Python-2.7.16.tgz
RUN tar xzf Python-2.7.16.tgz
RUN cd Python-2.7.16 && sudo ./configure --enable-optimizations --with-ssl && sudo make install

# Get & Install pip
RUN sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN sudo python get-pip.py

# Install pygraph
#COPY project/python-graph/ ./python-graph
#RUN cd python-graph/core/ && sudo python2 setup.py install

# Install python requirments
COPY project/requirements.txt .
RUN sudo pip2.7 install -r requirements.txt

# Clean up downloaded files
#RUN rm

# # ------------------------------------------------------------
# Copy over project code
#
# Do this last to keep the cached deps valid
# If this was at the top, each time you change code it would have
# to recompile all deps again which takes too much time for small
# code changes
# # ------------------------------------------------------------

COPY project/ .

# # ------------------------------------------------------------
# # End building MPI project
# # ------------------------------------------------------------