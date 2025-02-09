FROM ubuntu:20.04

# Set timezone non-interactively
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime
RUN apt-get update && apt-get install -y tzdata

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    openssh-server sudo netcat cron \
    && rm -rf /var/lib/apt/lists/*

# Install Flask for the vulnerable web app
RUN pip3 install flask

# Create SSH directories and configure SSH
RUN mkdir /var/run/sshd

# First create the ctf user, then set passwords
RUN useradd -m -s /bin/bash ctf && echo 'ctf:ctfpassword' | chpasswd
RUN echo 'root:rootpassword' | chpasswd

# Grant sudo permission to ctf user
RUN echo "ctf ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/ctf

# Copy necessary files
COPY app.py /var/www/app.py
COPY setup.sh /setup.sh
COPY entrypoint.sh /entrypoint.sh
COPY crontab /etc/cron.d/rotate_flags
COPY sudoers.d/ctf /etc/sudoers.d/ctf

# Ensure all scripts are executable
RUN chmod +x /setup.sh /entrypoint.sh

# Run entrypoint.sh as the main process
CMD ["/entrypoint.sh"]
