<!-- $ cli for creating a conf file and use it later (all this is from the root odoo folder btw) -->
python odoo-bin -d [databaseName] -r [databaseUser] -w [databasePassword] --addons-path=[ADDONS_PATH] --stop-after-init -s -c [configFileName].conf
<!-- $ once you created a config file simple use cli bellow to run odoo -->
python odoo-bin
<!-- $ cli for scaffolding a common module -->
python odoo-bin scaffold module_name .\[custom-addons-path]
<!-- $ cli for creating a new database, without -d to run all available database, choose from the ui -->
python odoo-bin -d [newDatabaseName]

<!--
  ? we can kill a odoo process directly with kill command but since we are using InstallScript from Yen to install
  ? our odoo instance on a ubuntu 20.04 server just use these instead sudo service odoo-server stop (location not matter)
  $ sudo service odoo-server start
  $ sudo service odoo-server stop
  $ sudo service odoo-server restart
-->