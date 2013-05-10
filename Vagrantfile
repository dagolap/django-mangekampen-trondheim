# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

# Box specific settings
  # Ubuntu 12.04 LTS Precise Pangolin
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"

  config.vm.network :forwarded_port, guest: 5555, host:5555

  # Provisioning
  config.vm.provision :shell, :path => "bootstrap.sh" 
end
