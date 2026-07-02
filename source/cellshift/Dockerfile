#
# Build like this from within repo:
#   docker build -t cellshift -f Dockerfile .
# Then run like this:
#   docker run -it cellshift
#

# Use the official Debian Bookworm Slim base image
FROM debian:12-slim
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install basic packages
RUN apt update && apt install -y apt-utils
RUN apt install -y locales
RUN dpkg-reconfigure locales
RUN dpkg-reconfigure tzdata

# Install necessary packages
RUN apt install -y --no-install-recommends \
    clang \
    curl \
    cmake \
    git \
    xz-utils \
    zstd \
    libhdf5-dev \
    hdf5-filter-plugin \
    hdf5-filter-plugin-blosc-serial

# Install Rust
RUN rm -f /etc/ssl/certs/ca-bundle.crt
RUN apt reinstall -y ca-certificates
RUN update-ca-certificates -y
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs --output /opt/rustup-init.sh 
RUN sh /opt/rustup-init.sh -y

# Install CellShift from remote
RUN mkdir -p /opt
ENV PATH "/root/.cargo/bin:/opt/bin:${PATH}"
RUN cargo install --root /opt/ --git https://github.com/robgjansen/cellshift.git

# Install CellShift from local
#RUN mkdir -p /opt
#WORKDIR /opt
#COPY cellshift.tar /opt/cellshift.tar
#RUN tar xf cellshift.tar && rm -rf cellshift.tar
#ENV PATH "/root/.cargo/bin:/opt/bin:${PATH}"
#RUN cargo install --root /opt/ --path cellshift

# Get a bash shell when the container starts
CMD ["/bin/bash"]
