# Releasing

* Chack that the [README](README.md) are up-to-date.
  
* Check that `setup.py` contains the correct version number.

* Commit the changes:
  
        git commit -a -m "Getting ready for release X.Y.Z"
        git push
  
* Create a tag `X.Y.Z` from `main` and push it to the github repo.
  Use the next message:

        git tag -a vX.Y.Z -m "Tagging version X.Y.Z"
        git push --tags

* Make sure that you are in a clean directory. The best way is to
  re-clone and re-build:
  
      cd /tmp
      git clone --recursive git@github.com:aleixalcacer/memprofiler.git
      cd memprofiler
      python setup.py build_ext

* Make the tarball with the command:

        python setup.py sdist

* Upload it to the PyPi repository:

        twine upload dist/*

* Change back to the actual *memprofiler* repo:

        cd $HOME/memprofiler

* Edit the version number in `setup.py` to increment the version to the next
  minor one (i.e. `X.Y.Z` -> `X.Y.(Z+1).dev0`).

* Commit your changes with:

        git commit -a -m "Post X.Y.Z release actions done"
        git push

