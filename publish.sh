#!/usr/bin/env bash
source ~/.bash_profile

csd=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
# hack app
if [[ "$csd" == *.app/Contents/Resources ]]
then
    parentdir="$(dirname "$(pwd)")"
    parentdir="$(dirname "$parentdir")"
    csd="$(dirname "$parentdir")"
else
    csd=$csd
fi
# hack app done
package=$(basename "$csd")
cd "$csd"

# fallback for wxpython
python "$csd/$package/prepublish.py" || pythonw "$csd/$package/prepublish.py"

rm -rf dist
rm -rf *.egg-info

# python setup.py register

# uv build --sdist
python setup.py sdist
# python setup.py sdist upload
uvx twine upload dist/*

rm -rf *.egg-info

git add -A 
git commit -m 'update' 
git push origin master 

# /Library/Frameworks/Python.framework/Versions/2.7/bin/pip install $package --upgrade

# repeat several time to force upgrade (PyPI index can lag right after upload)
for _ in 1 2 3; do
    ezupdate
done
# do not use this, seems not working??
# Although not required, it’s common to locally install your project in "develop" or "editable" mode 
# while you’re working on it. This allows the project to be both installed and editable in project form.
# run the following:
# python setup.py develop
ls dist
uv pip show "$package" | grep Version