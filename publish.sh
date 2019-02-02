#!/bin/bash

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
cd $csd

# fallback for wxpython
python $csd/$package/prepublish.py || pythonw $csd/$package/prepublish.py

rm -r dist
rm -r *.egg-info

# python setup.py register

python setup.py sdist
python setup.py sdist upload

rm -r *.egg-info

# /Users/jerry/Library/Enthought/Canopy_64bit/User/bin/pip install $package --upgrade
# /Users/jerry/PyEnv/bin/pip install $package --upgrade
# /Library/Frameworks/Python.framework/Versions/2.7/bin/pip install $package --upgrade
source ~/.bash_profile
pip install $package --upgrade --no-cache-dir --disable-pip-version-check

# do not use this, seems not working??
# Although not required, it’s common to locally install your project in “develop” or “editable” mode 
# while you’re working on it. This allows the project to be both installed and editable in project form.
# run the following:
# python setup.py develop

git add -A 
git commit -m 'update' 
git push origin master 
