# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
echo I am provisioning...
date > /etc/vagrant_provisioned_at
SCRIPT



Vagrant.configure("2") do |config|
  config.vm.provision "shell", inline: $script
end

Vagrant::Config.run do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.host_name = "postgresql" 

  config.vm.share_folder "bootstrap", "/mnt/bootstrap", ".", :create => true
  config.vm.share_folder "src", "/mnt/code", ".", :create => true
  config.vm.provision :shell, :path => "Vagrant-setup/bootstrap.sh"

  # PostgreSQL Server port forwarding
  config.vm.forward_port 5432, 15432
  config.vm.forward_port 8000, 8080
end

