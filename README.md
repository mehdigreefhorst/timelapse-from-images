# timelapse-from-images
Make aligned timelapse from images


How to make it work in upcloud

- add ssh keys (first generate and add them to upcloud)
- docker login
- git clone repo
- sudo apt install python3 python3-pip -y
- mkdir -p ~/.docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
- docker compose up -d