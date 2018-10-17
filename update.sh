echo "Updating From Git Remote"
pkill python3.6
git fetch
git checkout origin/unstable
echo "Updated Restarting Bot"
python3.6 src/botinabox.py &



