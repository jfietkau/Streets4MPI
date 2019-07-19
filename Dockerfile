# # ------------------------------------------------------------
# # Build MPI project
# # ------------------------------------------------------------

# Base MPI docker image
FROM nlknguyen/alpine-mpich:onbuild

# # ------------------------------------------------------------
# Install Linux deps
# # ------------------------------------------------------------

RUN sudo apk update
RUN sudo apk add vim \
                 bzip2-dev \
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

# Need for OSM (open street maps)
RUN sudo apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/testing \
  geos-dev
ENV LIBRARY_PATH=/lib:/usr/lib

# # ------------------------------------------------------------
# Install Python2 deps
# # ------------------------------------------------------------

# Get resource
RUN wget http://www.python.org/ftp/python/2.7.15/Python-2.7.15.tgz
RUN wget https://pypi.org/packages/source/p/pytracemalloc/pytracemalloc-1.4.tar.gz
# Extract
RUN tar -xf pytracemalloc-1.4.tar.gz
RUN tar -xzf Python-2.7.15.tgz
# Install Python
RUN cd Python-2.7.15 && sudo patch -p1 < ../pytracemalloc-1.4/patches/2.7.15/pep445.patch && sudo ./configure --with-ensurepip=install --enable-unicode=ucs4 --enable-optimizations --with-ssl && sudo make && sudo make install
RUN cd pytracemalloc-1.4 && sudo python2.7 setup.py install
# Install python requirments
COPY project/requirements.txt .
RUN sudo pip2.7 install -r requirements.txt

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
