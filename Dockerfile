FROM frrouting/frr:latest

# Add an SSH server to the FRR image
RUN apk add --no-cache openssh \
    && ssh-keygen -A \
    && echo "root:labpass123" | chpasswd \
    && sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
