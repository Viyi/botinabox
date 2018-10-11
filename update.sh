echo "Updating From Git Remote"
pkill Python
git fetch
git checkout origin/unstable
echo "Updated Restarting Bot"
python src/botinabox.py &



