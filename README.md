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



---

### Why I Didn't use heif-convert

I had so much issue with trying to use subprocesses and heif-converting software. All linux packages were problematic and I just couldn't make it work. Almost it worked but then something went wrong. So I choose for a less efficient python implemenation in the end. But if I ever want to optimize because of the huge user amount. Then look on the links below:

https://github.com/strukturag/libheif/issues/1190
https://idroot.us/convert-heif-images-to-jpg-or-png-linux/ (this worked great from terminal but in dockerfile it went wrong. Work from here & look how you can download the required packages. As it wasn't in the release file for debian at the time and gave a lot of errors)