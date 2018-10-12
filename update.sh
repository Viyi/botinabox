echo "Updating From Git Remote"
sudo systemctl stop /etc/rc-local.service
git fetch
git checkout origin/unstable
echo "Updated Restarting Bot"
python systemctl start /etc/rc-local.service



