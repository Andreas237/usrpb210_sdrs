FROM python:3.14.0a2-slim-bookworm

RUN cat /etc/os-release
# Install base UHD packages
RUN apt install -y git cmake libboost-all-dev libusb-1.0-0-dev python3-docutils python3-mako python3-numpy python3-requests python3-ruamel.yaml python3-setuptools build-essential

# Install the UHD Python API
RUN git clone https://github.com/EttusResearch/uhd.git && \
    cd uhd/host && \
    git checkout v4.7.0.0 && \
    mkdir build && \
    cd build && \
    cmake -DENABLE_TESTS=OFF -DENABLE_C_API=OFF -DENABLE_PYTHON_API=ON -DENABLE_MANUAL=OFF ..  && \
    make -j8 && \
    sudo make install && \
    sudo ldconfig

# Test that the build works
RUN python3 -c "import uhd; usrp = uhd.usrp.MultiUSRP(); samples = usrp.recv_num_samps(100, 100e6, 1e6, [0], 50)"