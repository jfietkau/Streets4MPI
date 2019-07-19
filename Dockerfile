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

# Get and install python2
#RUN wget http://www.python.org/ftp/python/2.7.16/Python-2.7.16.tgz
#RUN tar xzf Python-2.7.16.tgz
#RUN cd Python-2.7.16 && sudo ./configure --enable-optimizations --with-ensurepip=install --with-ssl && sudo make install

# Get, patch tracemalloc, and install patched python2
# TODO: Clean this dumpster fire up
RUN wget http://www.python.org/ftp/python/2.7.15/Python-2.7.15.tgz
RUN wget https://pypi.org/packages/source/p/pytracemalloc/pytracemalloc-1.4.tar.gz
RUN tar -xf pytracemalloc-1.4.tar.gz
RUN tar -xzf Python-2.7.15.tgz
#RUN cd Python-2.7.15 && sudo patch -p1 < ../pytracemalloc-1.4/patches/2.7.15/pep445.patch && sudo ./configure --with-ensurepip=install --enable-unicode=ucs4 --enable-optimizations --with-ssl --prefix=/opt/tracemalloc/py27 && sudo make && sudo make install
RUN cd Python-2.7.15 && sudo patch -p1 < ../pytracemalloc-1.4/patches/2.7.15/pep445.patch && sudo ./configure --with-ensurepip=install --enable-unicode=ucs4 --enable-optimizations --with-ssl && sudo make && sudo make install
#RUN cd pytracemalloc-1.4 && sudo /opt/tracemalloc/py27/bin/python2.7 setup.py install
RUN cd pytracemalloc-1.4 && sudo python2.7 setup.py install

# Install python requirments for system and patched versions of python
COPY project/requirements.txt .
RUN sudo pip2.7 install -r requirements.txt
#RUN sudo /opt/tracemalloc/py27/bin/pip2.7 install -r requirements.txt

# Patched python needs extra dep
#RUN sudo pip2.7 install pytracemalloc
#RUN sudo /opt/tracemalloc/py27/bin/pip2.7 install pytracemalloc


# TODO: add RM to clean up downloaded files
#RM foobar

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
