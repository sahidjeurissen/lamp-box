Vagrant.configure("2") do |config|
  config.vm.box = "bento/debian-9.0"
  config.vm.network "private_network", ip: "192.168.33.10"

  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "provision/playbook.yml"
  end
end
