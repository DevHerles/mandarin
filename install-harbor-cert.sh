openssl s_client -showcerts -connect tanzu-harbor.pngd.gob.pe:443 </dev/null 2>/dev/null | openssl x509 -outform PEM > tanzu-harbor.crt
sudo mkdir -p /etc/docker/certs.d/tanzu-harbor.pngd.gob.pe
sudo cp tanzu-harbor.crt /etc/docker/certs.d/tanzu-harbor.pngd.gob.pe/ca.crt
sudo systemctl restart docker
docker login tanzu-harbor.pngd.gob.pe
